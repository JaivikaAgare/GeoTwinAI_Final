# ============================================================
# GEOTWINAI
# NAGPUR DIGITAL TWIN
# SENTINEL-2 ALL BANDS ANALYSIS
#
# Source:
# Microsoft Planetary Computer
#
# Product:
# Sentinel-2 Level-2A
#
# Bands:
# B01, B02, B03, B04, B05, B06,
# B07, B08, B8A, B09, B11, B12
#
# Common analysis grid:
# 10 metres
#
# Indices:
# NDVI
# NDBI
# NDWI
#
# Google Earth Engine:
# NOT USED
# ============================================================


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rasterio

from rasterio.windows import from_bounds

from rasterio.warp import (
    transform_bounds,
    reproject,
    Resampling
)

from rasterio.transform import xy

from pystac_client import Client

import planetary_computer


warnings.filterwarnings("ignore")


# ============================================================
# 2. PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output",
    "satellite"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# 3. OUTPUT FILES
# ============================================================

SPATIAL_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Sentinel2_AllBands_Spatial.csv"
)


SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Sentinel2_AllBands_Summary.csv"
)


NDVI_TIF = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDVI.tif"
)


NDBI_TIF = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDBI.tif"
)


NDWI_TIF = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDWI.tif"
)


NDVI_PNG = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDVI.png"
)


NDBI_PNG = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDBI.png"
)


NDWI_PNG = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDWI.png"
)


# ============================================================
# 4. NAGPUR AREA OF INTEREST
# ============================================================
#
# Format:
# [West, South, East, North]
#
# IMPORTANT:
# This is an approximate bounding box.
# It is NOT an official Nagpur district boundary.
# ============================================================

NAGPUR_BBOX = [
    78.95,
    20.95,
    79.25,
    21.25
]


# ============================================================
# 5. DATE RANGE
# ============================================================

START_DATE = "2026-01-01T00:00:00Z"

END_DATE = "2026-08-22T23:59:59Z"

MAX_CLOUD = 20


# ============================================================
# 6. SENTINEL-2 BANDS
# ============================================================
#
# Sentinel-2 L2A provides these 12 useful spectral bands:
#
# B01 = Coastal aerosol       60m
# B02 = Blue                  10m
# B03 = Green                 10m
# B04 = Red                   10m
# B05 = Vegetation Red Edge   20m
# B06 = Vegetation Red Edge   20m
# B07 = Vegetation Red Edge   20m
# B08 = Near Infrared         10m
# B8A = Narrow NIR             20m
# B09 = Water Vapour          60m
# B11 = SWIR                  20m
# B12 = SWIR                  20m
#
# B10 is not included because it is not provided as a
# surface-reflectance band in Sentinel-2 L2A.
# ============================================================

BANDS = [
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B8A",
    "B09",
    "B11",
    "B12"
]


# ============================================================
# 7. PROGRAM HEADER
# ============================================================

print()
print("=" * 70)
print("          GEOTWINAI - SENTINEL-2 ALL BANDS")
print("=" * 70)

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)


# ============================================================
# 8. CONNECT TO MICROSOFT PLANETARY COMPUTER
# ============================================================

print()
print("Connecting to Microsoft Planetary Computer...")


STAC_URL = (
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)


catalog = Client.open(
    STAC_URL
)


print("Connection successful.")


# ============================================================
# 9. SEARCH SENTINEL-2 SCENES
# ============================================================

print()
print("Searching Sentinel-2 L2A scenes...")


search = catalog.search(

    collections=[
        "sentinel-2-l2a"
    ],

    bbox=NAGPUR_BBOX,

    datetime=(
        START_DATE
        + "/"
        + END_DATE
    ),

    query={
        "eo:cloud_cover": {
            "lt": MAX_CLOUD
        }
    }
)


items = list(
    search.items()
)


print()
print(
    "Scenes found:",
    len(items)
)


if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found."
    )


# ============================================================
# 10. SORT BY CLOUD COVER
# ============================================================

items.sort(

    key=lambda scene:
        float(
            scene.properties.get(
                "eo:cloud_cover",
                100
            )
        )
)


# ============================================================
# 11. DISPLAY BEST SCENES
# ============================================================

print()
print("Best available scenes:")


for scene in items[:10]:

    scene_date = (
        scene.datetime.strftime(
            "%Y-%m-%d"
        )
    )

    scene_cloud = float(
        scene.properties.get(
            "eo:cloud_cover",
            100
        )
    )

    print(
        f"{scene_date} | "
        f"Cloud: {scene_cloud:.2f}% | "
        f"{scene.id}"
    )


# ============================================================
# 12. SELECT BEST SCENE
# ============================================================

item = items[0]


item = planetary_computer.sign(
    item
)


SCENE_ID = item.id


SCENE_DATE = item.datetime.strftime(
    "%Y-%m-%d"
)


CLOUD_COVER = float(
    item.properties.get(
        "eo:cloud_cover",
        100
    )
)


print()
print("=" * 70)
print("SELECTED SCENE")
print("=" * 70)

print()
print("Scene ID:")
print(SCENE_ID)

print()
print("Date:")
print(SCENE_DATE)

print()
print("Cloud cover:")
print(
    f"{CLOUD_COVER:.2f}%"
)


# ============================================================
# 13. CREATE 10m REFERENCE GRID USING B02
# ============================================================
#
# B02 has native 10m resolution.
#
# We use B02 as the common spatial reference.
#
# The 20m and 60m bands will be resampled onto this grid.
# ============================================================

print()
print("=" * 70)
print("CREATING COMMON 10m REFERENCE GRID")
print("=" * 70)


reference_asset = item.assets.get(
    "B02"
)


if reference_asset is None:

    raise RuntimeError(
        "B02 asset not found."
    )


with rasterio.open(
    reference_asset.href
) as src:

    # Convert WGS84 bounding box
    # to Sentinel-2 raster CRS.

    left, bottom, right, top = transform_bounds(

        "EPSG:4326",

        src.crs,

        NAGPUR_BBOX[0],
        NAGPUR_BBOX[1],
        NAGPUR_BBOX[2],
        NAGPUR_BBOX[3]
    )


    # Create reference window.

    reference_window = from_bounds(

        left,
        bottom,
        right,
        top,

        transform=src.transform
    )


    reference_window = (
        reference_window
        .round_offsets()
        .round_lengths()
    )


    # Read B02.

    reference_data = src.read(
        1,
        window=reference_window
    ).astype(
        np.float32
    )


    # Reference transform.

    reference_transform = (
        src.window_transform(
            reference_window
        )
    )


    # Reference CRS.

    reference_crs = src.crs


    # Dimensions.

    reference_height = (
        reference_data.shape[0]
    )


    reference_width = (
        reference_data.shape[1]
    )


print()
print(
    "Reference grid:"
)

print(
    reference_height,
    "x",
    reference_width
)


print()
print(
    "Total 10m pixels:"
)

print(
    reference_height
    *
    reference_width
)


# ============================================================
# 14. FUNCTION TO READ AND RESAMPLE A BAND
# ============================================================

def read_band(
    band_name
):

    print(
        "Processing:",
        band_name
    )


    # --------------------------------------------------------
    # Get asset
    # --------------------------------------------------------

    asset = item.assets.get(
        band_name
    )


    if asset is None:

        raise RuntimeError(
            f"Band {band_name} not found."
        )


    # --------------------------------------------------------
    # Open raster
    # --------------------------------------------------------

    with rasterio.open(
        asset.href
    ) as src:

        # ----------------------------------------------------
        # Convert Nagpur bbox to source CRS
        # ----------------------------------------------------

        left, bottom, right, top = transform_bounds(

            "EPSG:4326",

            src.crs,

            NAGPUR_BBOX[0],
            NAGPUR_BBOX[1],
            NAGPUR_BBOX[2],
            NAGPUR_BBOX[3]
        )


        # ----------------------------------------------------
        # Create source window
        # ----------------------------------------------------

        window = from_bounds(

            left,
            bottom,
            right,
            top,

            transform=src.transform
        )


        window = (
            window
            .round_offsets()
            .round_lengths()
        )


        # ----------------------------------------------------
        # Read source band
        # ----------------------------------------------------

        source_data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


        # ----------------------------------------------------
        # Transform of source window
        # ----------------------------------------------------

        source_transform = (
            src.window_transform(
                window
            )
        )


        source_crs = src.crs


        # ----------------------------------------------------
        # Create destination array
        # ----------------------------------------------------

        destination = np.full(

            (
                reference_height,
                reference_width
            ),

            np.nan,

            dtype=np.float32
        )


        # ----------------------------------------------------
        # Resample to common 10m grid
        # ----------------------------------------------------

        reproject(

            source=source_data,

            destination=destination,

            src_transform=source_transform,

            src_crs=source_crs,

            dst_transform=reference_transform,

            dst_crs=reference_crs,

            resampling=Resampling.bilinear,

            src_nodata=0,

            dst_nodata=np.nan
        )


        # ----------------------------------------------------
        # Sentinel-2 reflectance scaling
        # ----------------------------------------------------

        destination = (
            destination / 10000.0
        )


        # ----------------------------------------------------
        # Remove invalid negative values
        # ----------------------------------------------------

        destination[
            destination < 0
        ] = np.nan


        return destination


# ============================================================
# 15. READ ALL BANDS
# ============================================================

print()
print("=" * 70)
print("READING ALL SENTINEL-2 BANDS")
print("=" * 70)


band_data = {}


for band in BANDS:

    band_data[band] = read_band(
        band
    )


print()
print("All bands processed successfully.")


# ============================================================
# 16. VALID PIXELS
# ============================================================

print()
print("=" * 70)
print("CHECKING VALID PIXELS")
print("=" * 70)


valid = np.ones(

    (
        reference_height,
        reference_width
    ),

    dtype=bool
)


for band in BANDS:

    valid &= np.isfinite(
        band_data[band]
    )


print()
print(
    "Valid 10m pixels:",
    int(valid.sum())
)


if valid.sum() == 0:

    raise RuntimeError(
        "No valid pixels found."
    )


# ============================================================
# 17. CALCULATE NDVI
# ============================================================
#
# NDVI =
#
# (NIR - RED)
# -------------
# (NIR + RED)
#
# B08 = NIR
# B04 = Red
# ============================================================

print()
print("Calculating NDVI...")


ndvi_denominator = (

    band_data["B08"]
    +
    band_data["B04"]

)


NDVI = np.full(

    (
        reference_height,
        reference_width
    ),

    np.nan,

    dtype=np.float32
)


safe = (

    valid

    &

    (
        np.abs(
            ndvi_denominator
        )
        >
        1e-8
    )
)


NDVI[safe] = (

    band_data["B08"][safe]
    -
    band_data["B04"][safe]

) / (

    band_data["B08"][safe]
    +
    band_data["B04"][safe]

)


NDVI[

    (NDVI < -1)
    |
    (NDVI > 1)

] = np.nan


# ============================================================
# 18. CALCULATE NDBI
# ============================================================
#
# NDBI =
#
# (SWIR - NIR)
# ------------
# (SWIR + NIR)
#
# B11 = SWIR
# B08 = NIR
# ============================================================

print("Calculating NDBI...")


ndbi_denominator = (

    band_data["B11"]
    +
    band_data["B08"]

)


NDBI = np.full(

    (
        reference_height,
        reference_width
    ),

    np.nan,

    dtype=np.float32
)


safe = (

    valid

    &

    (
        np.abs(
            ndbi_denominator
        )
        >
        1e-8
    )
)


NDBI[safe] = (

    band_data["B11"][safe]
    -
    band_data["B08"][safe]

) / (

    band_data["B11"][safe]
    +
    band_data["B08"][safe]

)


NDBI[

    (NDBI < -1)
    |
    (NDBI > 1)

] = np.nan


# ============================================================
# 19. CALCULATE NDWI
# ============================================================
#
# NDWI =
#
# (GREEN - NIR)
# -------------
# (GREEN + NIR)
#
# B03 = Green
# B08 = NIR
# ============================================================

print("Calculating NDWI...")


ndwi_denominator = (

    band_data["B03"]
    +
    band_data["B08"]

)


NDWI = np.full(

    (
        reference_height,
        reference_width
    ),

    np.nan,

    dtype=np.float32
)


safe = (

    valid

    &

    (
        np.abs(
            ndwi_denominator
        )
        >
        1e-8
    )
)


NDWI[safe] = (

    band_data["B03"][safe]
    -
    band_data["B08"][safe]

) / (

    band_data["B03"][safe]
    +
    band_data["B08"][safe]

)


NDWI[

    (NDWI < -1)
    |
    (NDWI > 1)

] = np.nan


# ============================================================
# 20. SAVE INDEX RASTER FUNCTION
# ============================================================

def save_raster(
    filename,
    array
):

    with rasterio.open(

        filename,

        "w",

        driver="GTiff",

        height=array.shape[0],

        width=array.shape[1],

        count=1,

        dtype="float32",

        crs=reference_crs,

        transform=reference_transform,

        nodata=np.nan

    ) as dst:

        dst.write(

            array.astype(
                np.float32
            ),

            1

        )


# ============================================================
# 21. SAVE NDVI / NDBI / NDWI MAPS
# ============================================================

print()
print("=" * 70)
print("SAVING INDEX RASTERS")
print("=" * 70)


save_raster(
    NDVI_TIF,
    NDVI
)


print(
    "NDVI raster saved."
)


save_raster(
    NDBI_TIF,
    NDBI
)


print(
    "NDBI raster saved."
)


save_raster(
    NDWI_TIF,
    NDWI
)


print(
    "NDWI raster saved."
)


# ============================================================
# 22. CREATE FAST SPATIAL CSV
# ============================================================
#
# IMPORTANT:
#
# The old code processed 10+ million pixels using nested
# Python loops.
#
# That was extremely slow.
#
# This version uses NumPy vectorization.
# ============================================================

print()
print("=" * 70)
print("CREATING SPATIAL CSV")
print("=" * 70)


rows, cols = np.where(
    valid
)


print()
print(
    "Pixels to export:",
    len(rows)
)


# ============================================================
# 23. GENERATE PIXEL COORDINATES
# ============================================================

print()
print(
    "Generating coordinates..."
)


xs, ys = xy(

    reference_transform,

    rows,

    cols,

    offset="center"
)


xs = np.asarray(
    xs
)


ys = np.asarray(
    ys
)


# ============================================================
# 24. CONVERT TO LATITUDE/LONGITUDE
# ============================================================

print()
print(
    "Converting coordinates to latitude/longitude..."
)


longitudes, latitudes = rasterio.warp.transform(

    reference_crs,

    "EPSG:4326",

    xs.tolist(),

    ys.tolist()
)


longitudes = np.asarray(
    longitudes
)


latitudes = np.asarray(
    latitudes
)


# ============================================================
# 25. CREATE DATA DICTIONARY
# ============================================================

print()
print(
    "Creating dataframe..."
)


data = {

    "Latitude":
        np.round(
            latitudes,
            6
        ),

    "Longitude":
        np.round(
            longitudes,
            6
        )
}


# ============================================================
# 26. ADD ALL BANDS
# ============================================================

for band in BANDS:

    data[band] = np.round(

        band_data[band][
            rows,
            cols
        ],

        6
    )


# ============================================================
# 27. ADD INDICES
# ============================================================

data["NDVI"] = np.round(

    NDVI[
        rows,
        cols
    ],

    6
)


data["NDBI"] = np.round(

    NDBI[
        rows,
        cols
    ],

    6
)


data["NDWI"] = np.round(

    NDWI[
        rows,
        cols
    ],

    6
)


# ============================================================
# 28. ADD METADATA
# ============================================================

data["Satellite"] = (
    "Sentinel-2"
)


data["Product"] = (
    "Sentinel-2 L2A"
)


data["Scene_ID"] = (
    SCENE_ID
)


data["Scene_Date"] = (
    SCENE_DATE
)


data["Cloud_Cover_Percent"] = (
    CLOUD_COVER
)


data["Grid_Size_m"] = (
    10
)


data["Data_Source"] = (
    "Microsoft Planetary Computer"
)


# ============================================================
# 29. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    data
)


if df.empty:

    raise RuntimeError(
        "Spatial dataset is empty."
    )


print()
print(
    "Spatial records:",
    len(df)
)


print()
print(
    "Columns:",
    len(df.columns)
)


# ============================================================
# 30. SAVE SPATIAL CSV
# ============================================================

print()
print(
    "Saving spatial CSV..."
)


df.to_csv(

    SPATIAL_CSV,

    index=False

)


print()
print(
    "Spatial CSV saved:"
)

print(
    SPATIAL_CSV
)


# ============================================================
# 31. CREATE SUMMARY
# ============================================================

print()
print("=" * 70)
print("CREATING SUMMARY")
print("=" * 70)


summary_record = {

    "Region":
        "Nagpur",

    "Satellite":
        "Sentinel-2",

    "Product":
        "Sentinel-2 L2A",

    "Scene_ID":
        SCENE_ID,

    "Scene_Date":
        SCENE_DATE,

    "Cloud_Cover_Percent":
        CLOUD_COVER,

    "Grid_Size_m":
        10,

    "Spatial_Records":
        len(df),

    "Data_Source":
        "Microsoft Planetary Computer",

    "Mean_NDVI":
        round(
            float(
                df["NDVI"].mean()
            ),
            6
        ),

    "Min_NDVI":
        round(
            float(
                df["NDVI"].min()
            ),
            6
        ),

    "Max_NDVI":
        round(
            float(
                df["NDVI"].max()
            ),
            6
        ),

    "Mean_NDBI":
        round(
            float(
                df["NDBI"].mean()
            ),
            6
        ),

    "Min_NDBI":
        round(
            float(
                df["NDBI"].min()
            ),
            6
        ),

    "Max_NDBI":
        round(
            float(
                df["NDBI"].max()
            ),
            6
        ),

    "Mean_NDWI":
        round(
            float(
                df["NDWI"].mean()
            ),
            6
        ),

    "Min_NDWI":
        round(
            float(
                df["NDWI"].min()
            ),
            6
        ),

    "Max_NDWI":
        round(
            float(
                df["NDWI"].max()
            ),
            6
        )
}


# ============================================================
# 32. ADD BAND STATISTICS
# ============================================================

for band in BANDS:

    summary_record[
        band + "_Mean"
    ] = round(

        float(
            df[band].mean()
        ),

        6
    )


summary_df = pd.DataFrame(
    [summary_record]
)


# ============================================================
# 33. SAVE SUMMARY CSV
# ============================================================

summary_df.to_csv(

    SUMMARY_CSV,

    index=False

)


print()
print(
    "Summary CSV saved:"
)

print(
    SUMMARY_CSV
)


# ============================================================
# 34. CREATE PNG PREVIEWS
# ============================================================

print()
print("=" * 70)
print("CREATING PREVIEW IMAGES")
print("=" * 70)


# ------------------------------------------------------------
# NDVI
# ------------------------------------------------------------

plt.figure(
    figsize=(10, 8)
)


plt.imshow(

    NDVI,

    cmap="RdYlGn",

    vmin=-1,

    vmax=1
)


plt.colorbar(
    label="NDVI"
)


plt.title(
    "Nagpur Sentinel-2 NDVI\n"
    f"Date: {SCENE_DATE}"
)


plt.xlabel(
    "10m Grid"
)


plt.ylabel(
    "10m Grid"
)


plt.tight_layout()


plt.savefig(

    NDVI_PNG,

    dpi=200,

    bbox_inches="tight"
)


plt.close()


# ------------------------------------------------------------
# NDBI
# ------------------------------------------------------------

plt.figure(
    figsize=(10, 8)
)


plt.imshow(

    NDBI,

    cmap="RdYlGn",

    vmin=-1,

    vmax=1
)


plt.colorbar(
    label="NDBI"
)


plt.title(
    "Nagpur Sentinel-2 NDBI\n"
    f"Date: {SCENE_DATE}"
)


plt.xlabel(
    "10m Grid"
)


plt.ylabel(
    "10m Grid"
)


plt.tight_layout()


plt.savefig(

    NDBI_PNG,

    dpi=200,

    bbox_inches="tight"
)


plt.close()


# ------------------------------------------------------------
# NDWI
# ------------------------------------------------------------

plt.figure(
    figsize=(10, 8)
)


plt.imshow(

    NDWI,

    cmap="RdYlGn",

    vmin=-1,

    vmax=1
)


plt.colorbar(
    label="NDWI"
)


plt.title(
    "Nagpur Sentinel-2 NDWI\n"
    f"Date: {SCENE_DATE}"
)


plt.xlabel(
    "10m Grid"
)


plt.ylabel(
    "10m Grid"
)


plt.tight_layout()


plt.savefig(

    NDWI_PNG,

    dpi=200,

    bbox_inches="tight"
)


plt.close()


# ============================================================
# 35. FINAL RESULTS
# ============================================================

print()
print("=" * 70)
print("          SENTINEL-2 ALL BANDS COMPLETED")
print("=" * 70)


print()
print(
    "Satellite:",
    "Sentinel-2"
)


print(
    "Product:",
    "Sentinel-2 L2A"
)


print(
    "Scene date:",
    SCENE_DATE
)


print(
    "Cloud cover:",
    f"{CLOUD_COVER:.2f}%"
)


print(
    "Bands processed:",
    len(BANDS)
)


print(
    "Spatial records:",
    len(df)
)


print(
    "Mean NDVI:",
    round(
        float(
            df["NDVI"].mean()
        ),
        4
    )
)


print(
    "Mean NDBI:",
    round(
        float(
            df["NDBI"].mean()
        ),
        4
    )
)


print(
    "Mean NDWI:",
    round(
        float(
            df["NDWI"].mean()
        ),
        4
    )
)


print()
print("FILES CREATED")


print()
print(
    "1. All Bands Spatial CSV:"
)

print(
    SPATIAL_CSV
)


print()
print(
    "2. All Bands Summary CSV:"
)

print(
    SUMMARY_CSV
)


print()
print(
    "3. NDVI GeoTIFF:"
)

print(
    NDVI_TIF
)


print()
print(
    "4. NDBI GeoTIFF:"
)

print(
    NDBI_TIF
)


print()
print(
    "5. NDWI GeoTIFF:"
)

print(
    NDWI_TIF
)


print()
print(
    "6. NDVI PNG:"
)

print(
    NDVI_PNG
)


print()
print(
    "7. NDBI PNG:"
)

print(
    NDBI_PNG
)


print()
print(
    "8. NDWI PNG:"
)

print(
    NDWI_PNG
)


print()
print(
    "Google Earth Engine: NOT USED"
)


print(
    "Data Source: Microsoft Planetary Computer"
)


print(
    "Common Analysis Grid: 10m"
)


print()
print("=" * 70)
print("                    DONE")
print("=" * 70)

