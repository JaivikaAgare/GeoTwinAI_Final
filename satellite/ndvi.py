import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds, transform
from rasterio.transform import xy

from pystac_client import Client
import planetary_computer

warnings.filterwarnings("ignore")


# ============================================================
# 1. PROJECT PATHS
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
# 2. OUTPUT FILES
# ============================================================

SPATIAL_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Sentinel2_NDVI_Spatial.csv"
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Sentinel2_NDVI_Summary.csv"
)

PNG_FILE = os.path.join(
    OUTPUT_DIR,
    "Nagpur_NDVI.png"
)


# ============================================================
# 3. NAGPUR SEARCH AREA
# ============================================================

# Nagpur approximate bounding box.
# This is a search/processing area, NOT a political boundary.

NAGPUR_BBOX = [
    78.95,   # West
    20.95,   # South
    79.25,   # East
    21.25    # North
]


# ============================================================
# 4. DATE RANGE
# ============================================================

START_DATE = "2026-01-01T00:00:00Z"
END_DATE = "2026-08-22T23:59:59Z"

MAX_CLOUD = 20


# ============================================================
# 5. SPATIAL AGGREGATION
# ============================================================

# Sentinel-2 B02/B03/B04/B08 = 10m.
#
# 10 x 10 pixels = approximately 100m grid.

FACTOR = 10


# ============================================================
# 6. HEADER
# ============================================================

print()
print("=" * 60)
print("          NAGPUR SENTINEL-2 NDVI")
print("=" * 60)

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)


# ============================================================
# 7. CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
print("Connecting to Sentinel-2 data source...")

STAC_URL = (
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)

catalog = Client.open(
    STAC_URL
)

print("Connection successful.")


# ============================================================
# 8. SEARCH SENTINEL-2
# ============================================================

print()
print("Searching Sentinel-2 imagery...")

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
    "Number of Sentinel-2 scenes found:",
    len(items)
)


if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found."
    )


# ============================================================
# 9. SORT BY CLOUD COVER
# ============================================================

items.sort(
    key=lambda item:
        item.properties.get(
            "eo:cloud_cover",
            100
        )
)


# ============================================================
# 10. SHOW AVAILABLE SCENES
# ============================================================

print()
print("Available scenes:")

for item in items[:10]:

    date = item.datetime.strftime(
        "%Y-%m-%d"
    )

    cloud = item.properties.get(
        "eo:cloud_cover",
        100
    )

    print(
        f"{date} | "
        f"Cloud: {cloud}% | "
        f"{item.id}"
    )


# ============================================================
# 11. SELECT BEST SCENE
# ============================================================

item = items[0]

item = planetary_computer.sign(
    item
)


SCENE_DATE = item.datetime.strftime(
    "%Y-%m-%d"
)

CLOUD_COVER = item.properties.get(
    "eo:cloud_cover",
    100
)

SCENE_ID = item.id


print()
print("Selected scene:")
print("Date:", SCENE_DATE)
print("Cloud cover:", CLOUD_COVER, "%")
print("Scene:", SCENE_ID)


# ============================================================
# 12. FUNCTION TO READ SENTINEL-2 BAND
# ============================================================

def read_band(
    band_name
):

    asset = item.assets.get(
        band_name
    )

    if asset is None:

        raise RuntimeError(
            f"Sentinel-2 asset not found: {band_name}"
        )


    with rasterio.open(
        asset.href
    ) as src:

        # Convert Nagpur WGS84 bbox
        # into the raster CRS.

        left, bottom, right, top = (
            transform_bounds(

                "EPSG:4326",

                src.crs,

                NAGPUR_BBOX[0],
                NAGPUR_BBOX[1],
                NAGPUR_BBOX[2],
                NAGPUR_BBOX[3]
            )
        )


        # Create raster window.

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


        # Read band.

        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


        # Transform of cropped raster.

        cropped_transform = (
            src.window_transform(
                window
            )
        )


        # CRS of raster.

        raster_crs = src.crs


        # Sentinel-2 L2A scaling.

        data = data / 10000.0


        return (
            data,
            cropped_transform,
            raster_crs
        )


# ============================================================
# 13. READ BANDS
# ============================================================

print()
print("Reading Sentinel-2 bands...")

print("B02 - Blue")

B02, raster_transform, raster_crs = (
    read_band("B02")
)


print("B03 - Green")

B03, _, _ = (
    read_band("B03")
)


print("B04 - Red")

B04, _, _ = (
    read_band("B04")
)


print("B08 - Near Infrared")

B08, _, _ = (
    read_band("B08")
)


# ============================================================
# 14. CHECK BAND DIMENSIONS
# ============================================================

print()
print("Band dimensions:")

print("B02:", B02.shape)
print("B03:", B03.shape)
print("B04:", B04.shape)
print("B08:", B08.shape)


if not (
    B02.shape
    == B03.shape
    == B04.shape
    == B08.shape
):

    raise RuntimeError(
        "B02, B03, B04 and B08 dimensions do not match."
    )


# ============================================================
# 15. VALID PIXELS
# ============================================================

valid_pixels = (

    np.isfinite(B02)

    & np.isfinite(B03)

    & np.isfinite(B04)

    & np.isfinite(B08)

    & (B02 >= 0)

    & (B03 >= 0)

    & (B04 >= 0)

    & (B08 >= 0)
)


print()
print(
    "Valid 10m pixels:",
    int(valid_pixels.sum())
)


# ============================================================
# 16. CALCULATE NDVI
# ============================================================

print()
print("Calculating NDVI...")


denominator = (
    B08 + B04
)


NDVI = np.full(
    B04.shape,
    np.nan,
    dtype=np.float32
)


safe_pixels = (
    valid_pixels
    &
    (denominator != 0)
)


NDVI[safe_pixels] = (

    B08[safe_pixels]
    -
    B04[safe_pixels]

) / (

    B08[safe_pixels]
    +
    B04[safe_pixels]
)


# Keep NDVI within valid range.

NDVI[
    (NDVI < -1)
    |
    (NDVI > 1)
] = np.nan


print(
    "Valid NDVI pixels:",
    int(
        np.isfinite(NDVI).sum()
    )
)


# ============================================================
# 17. AGGREGATE TO ~100m
# ============================================================

print()
print(
    "Aggregating 10m pixels into approximately 100m cells..."
)


height, width = NDVI.shape


new_height = (
    height // FACTOR
) * FACTOR


new_width = (
    width // FACTOR
) * FACTOR


# Crop to complete blocks.

B02 = B02[
    :new_height,
    :new_width
]

B03 = B03[
    :new_height,
    :new_width
]

B04 = B04[
    :new_height,
    :new_width
]

B08 = B08[
    :new_height,
    :new_width
]

NDVI = NDVI[
    :new_height,
    :new_width
]


# ============================================================
# 18. BLOCK MEAN FUNCTION
# ============================================================

def block_mean(
    array,
    factor
):

    h, w = array.shape

    reshaped = array.reshape(

        h // factor,

        factor,

        w // factor,

        factor
    )


    return np.nanmean(
        reshaped,
        axis=(1, 3)
    )


# ============================================================
# 19. CREATE 100m GRIDS
# ============================================================

B02_GRID = block_mean(
    B02,
    FACTOR
)

B03_GRID = block_mean(
    B03,
    FACTOR
)

B04_GRID = block_mean(
    B04,
    FACTOR
)

B08_GRID = block_mean(
    B08,
    FACTOR
)

NDVI_GRID = block_mean(
    NDVI,
    FACTOR
)


grid_height, grid_width = (
    NDVI_GRID.shape
)


print()
print(
    "Spatial grid:",
    grid_height,
    "x",
    grid_width
)

print(
    "Spatial records:",
    grid_height * grid_width
)


# ============================================================
# 20. CREATE SPATIAL RECORDS
# ============================================================

print()
print("Creating spatial CSV records...")


records = []


for row in range(
    grid_height
):

    for col in range(
        grid_width
    ):

        ndvi_value = NDVI_GRID[
            row,
            col
        ]


        if not np.isfinite(
            ndvi_value
        ):

            continue


        # Center of the 100m cell
        # in the original 10m raster.

        source_row = (
            row * FACTOR
            + FACTOR // 2
        )


        source_col = (
            col * FACTOR
            + FACTOR // 2
        )


        # Convert row/column to
        # raster coordinates.

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"
        )


        # ====================================================
        # IMPORTANT:
        # Convert raster CRS -> EPSG:4326
        #
        # This is the corrected part.
        # ====================================================

        longitude_list, latitude_list = (
            transform(

                raster_crs,

                "EPSG:4326",

                [x],

                [y]
            )
        )


        longitude = (
            longitude_list[0]
        )

        latitude = (
            latitude_list[0]
        )


        b02_value = B02_GRID[
            row,
            col
        ]

        b03_value = B03_GRID[
            row,
            col
        ]

        b04_value = B04_GRID[
            row,
            col
        ]

        b08_value = B08_GRID[
            row,
            col
        ]


        # ====================================================
        # NDVI CLASS
        # ====================================================

        if ndvi_value < 0:

            ndvi_class = (
                "Water / Bare Surface"
            )

        elif ndvi_value < 0.20:

            ndvi_class = (
                "Very Low Vegetation"
            )

        elif ndvi_value < 0.40:

            ndvi_class = (
                "Low Vegetation"
            )

        elif ndvi_value < 0.60:

            ndvi_class = (
                "Moderate Vegetation"
            )

        else:

            ndvi_class = (
                "Dense Vegetation"
            )


        records.append({

            "Latitude":
                round(
                    latitude,
                    6
                ),

            "Longitude":
                round(
                    longitude,
                    6
                ),

            "B02_Blue":
                round(
                    float(
                        b02_value
                    ),
                    6
                ),

            "B03_Green":
                round(
                    float(
                        b03_value
                    ),
                    6
                ),

            "B04_Red":
                round(
                    float(
                        b04_value
                    ),
                    6
                ),

            "B08_NIR":
                round(
                    float(
                        b08_value
                    ),
                    6
                ),

            "NDVI":
                round(
                    float(
                        ndvi_value
                    ),
                    6
                ),

            "NDVI_Class":
                ndvi_class,

            "Satellite":
                "Sentinel-2",

            "Product":
                "Sentinel-2 L2A",

            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
                CLOUD_COVER,

            "Grid_Size_m":
                100

        })


# ============================================================
# 21. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise RuntimeError(
        "Spatial NDVI dataset is empty."
    )


print()
print(
    "Final spatial records:",
    len(df)
)


# ============================================================
# 22. SAVE SPATIAL CSV
# ============================================================

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
# 23. CREATE SUMMARY
# ============================================================

summary_df = pd.DataFrame({

    "Region": [
        "Nagpur"
    ],

    "Satellite": [
        "Sentinel-2"
    ],

    "Product": [
        "Sentinel-2 L2A"
    ],

    "Scene_Date": [
        SCENE_DATE
    ],

    "Cloud_Cover_Percent": [
        CLOUD_COVER
    ],

    "B02_Mean": [
        df[
            "B02_Blue"
        ].mean()
    ],

    "B03_Mean": [
        df[
            "B03_Green"
        ].mean()
    ],

    "B04_Mean": [
        df[
            "B04_Red"
        ].mean()
    ],

    "B08_Mean": [
        df[
            "B08_NIR"
        ].mean()
    ],

    "NDVI_Mean": [
        df[
            "NDVI"
        ].mean()
    ],

    "NDVI_Min": [
        df[
            "NDVI"
        ].min()
    ],

    "NDVI_Max": [
        df[
            "NDVI"
        ].max()
    ],

    "Vegetation_Percentage": [

        (
            df["NDVI"] >= 0.30
        ).mean()
        * 100
    ],

    "Spatial_Records": [
        len(df)
    ]

})


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
# 24. CREATE NDVI PNG
# ============================================================

print()
print(
    "Creating NDVI PNG..."
)


plt.figure(
    figsize=(12, 9)
)


plt.imshow(

    NDVI_GRID,

    cmap="RdYlGn",

    vmin=-1,

    vmax=1
)


plt.colorbar(
    label="NDVI"
)


plt.title(
    "Nagpur Sentinel-2 NDVI\n"
    f"Scene Date: {SCENE_DATE}"
)


plt.xlabel(
    "100m Grid"
)

plt.ylabel(
    "100m Grid"
)


plt.tight_layout()


plt.savefig(

    PNG_FILE,

    dpi=300,

    bbox_inches="tight"
)


plt.close()


# ============================================================
# 25. FINAL RESULTS
# ============================================================

print()
print("=" * 60)
print("              NDVI COMPLETED")
print("=" * 60)

print()

print(
    "Satellite:",
    "Sentinel-2"
)

print(
    "Scene date:",
    SCENE_DATE
)

print(
    "Cloud cover:",
    CLOUD_COVER,
    "%"
)

print(
    "Spatial records:",
    len(df)
)

print(
    "Mean NDVI:",
    round(
        df["NDVI"].mean(),
        4
    )
)

print(
    "Minimum NDVI:",
    round(
        df["NDVI"].min(),
        4
    )
)

print(
    "Maximum NDVI:",
    round(
        df["NDVI"].max(),
        4
    )
)

print()
print("FILES CREATED")

print()
print(
    "1. Spatial CSV:"
)

print(
    SPATIAL_CSV
)

print()
print(
    "2. Summary CSV:"
)

print(
    SUMMARY_CSV
)

print()
print(
    "3. NDVI PNG:"
)

print(
    PNG_FILE
)

print()
print(
    "Google Earth Engine: NOT USED"
)

print(
    "GeoJSON boundary: NOT REQUIRED"
)

print()
print("=" * 60)
