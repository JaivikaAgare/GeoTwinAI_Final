import os
import warnings
from datetime import datetime, timezone

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

NAGPUR_BBOX = [
    78.95,
    20.95,
    79.25,
    21.25
]


# ============================================================
# 4. DATE RANGE
# ============================================================

START_DATE = "2026-01-01T00:00:00Z"

# Automatically use current UTC date/time.
# So you don't have to manually change this
# every time you run the script.

END_DATE = datetime.now(
    timezone.utc
).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

MAX_CLOUD = 20


# ============================================================
# 5. SPATIAL AGGREGATION
# ============================================================

FACTOR = 10


# ============================================================
# 6. HEADER
# ============================================================

print()
print("=" * 70)
print("              NAGPUR SENTINEL-2 NDVI")
print("=" * 70)

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

print()
print("Search Start Date:")
print(START_DATE)

print()
print("Search End Date:")
print(END_DATE)

print()
print("Maximum Cloud Cover:")
print(f"{MAX_CLOUD}%")


# ============================================================
# 7. CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
print("=" * 70)
print("CONNECTING TO PLANETARY COMPUTER")
print("=" * 70)

STAC_URL = (
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)

catalog = Client.open(
    STAC_URL
)

print()
print("Connection successful.")


# ============================================================
# 8. SEARCH SENTINEL-2 IMAGERY
# ============================================================

print()
print("=" * 70)
print("SEARCHING SENTINEL-2 IMAGERY")
print("=" * 70)

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


# ============================================================
# 9. CHECK SCENES
# ============================================================

if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found for "
        "the selected date range and cloud "
        "cover limit."
    )


# ============================================================
# 10. SORT BY LATEST DATE
# ============================================================

def get_scene_datetime(item):

    scene_datetime = item.datetime

    if scene_datetime is None:

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if scene_datetime.tzinfo is None:

        scene_datetime = (
            scene_datetime.replace(
                tzinfo=timezone.utc
            )
        )

    return scene_datetime


# IMPORTANT:
# Latest date FIRST.
#
# We are NOT sorting by cloud cover.
#
# This prevents an old 0% cloud scene
# like 2026-05-12 from automatically
# beating a newer scene.

items.sort(
    key=get_scene_datetime,
    reverse=True
)


# ============================================================
# 11. SHOW LATEST AVAILABLE SCENES
# ============================================================

print()
print("=" * 70)
print("LATEST AVAILABLE SENTINEL-2 SCENES")
print("=" * 70)

print()


for index, scene in enumerate(
    items[:15],
    start=1
):

    if scene.datetime is not None:

        scene_date = (
            scene.datetime.strftime(
                "%Y-%m-%d"
            )
        )

    else:

        scene_date = "Unknown"


    cloud = scene.properties.get(
        "eo:cloud_cover",
        100
    )


    print(
        f"{index:02d}. "
        f"{scene_date} | "
        f"Cloud: {cloud}% | "
        f"{scene.id}"
    )


# ============================================================
# 12. SELECT LATEST SCENE
# ============================================================

item = items[0]


# Sign Planetary Computer asset URLs.

item = planetary_computer.sign(
    item
)


SCENE_DATE = (
    item.datetime.strftime(
        "%Y-%m-%d"
    )
)


CLOUD_COVER = (
    item.properties.get(
        "eo:cloud_cover",
        100
    )
)


SCENE_ID = item.id


print()
print("=" * 70)
print("SELECTED SCENE")
print("=" * 70)

print()
print("Date:")
print(SCENE_DATE)

print()
print("Cloud cover:")
print(
    CLOUD_COVER,
    "%"
)

print()
print("Scene:")
print(SCENE_ID)


# ============================================================
# 13. FUNCTION TO READ SENTINEL-2 BAND
# ============================================================

def read_band(
    band_name
):

    asset = item.assets.get(
        band_name
    )


    if asset is None:

        raise RuntimeError(
            f"Sentinel-2 asset not found: "
            f"{band_name}"
        )


    with rasterio.open(
        asset.href
    ) as src:

        # ----------------------------------------------------
        # Convert Nagpur WGS84 bounding box
        # into Sentinel-2 raster CRS.
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Create raster window
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
        # Read raster band
        # ----------------------------------------------------

        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


        # ----------------------------------------------------
        # Transform of cropped raster
        # ----------------------------------------------------

        cropped_transform = (
            src.window_transform(
                window
            )
        )


        # ----------------------------------------------------
        # Raster CRS
        # ----------------------------------------------------

        raster_crs = src.crs


        # ----------------------------------------------------
        # Sentinel-2 L2A scaling
        # ----------------------------------------------------

        data = (
            data / 10000.0
        )


        return (
            data,
            cropped_transform,
            raster_crs
        )


# ============================================================
# 14. READ SENTINEL-2 BANDS
# ============================================================

print()
print("=" * 70)
print("READING SENTINEL-2 BANDS")
print("=" * 70)

print()

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
# 15. CHECK BAND DIMENSIONS
# ============================================================

print()
print("=" * 70)
print("BAND DIMENSIONS")
print("=" * 70)

print()

print(
    "B02:",
    B02.shape
)

print(
    "B03:",
    B03.shape
)

print(
    "B04:",
    B04.shape
)

print(
    "B08:",
    B08.shape
)


if not (
    B02.shape
    == B03.shape
    == B04.shape
    == B08.shape
):

    raise RuntimeError(
        "B02, B03, B04 and B08 "
        "dimensions do not match."
    )


# ============================================================
# 16. VALID PIXELS
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
    int(
        valid_pixels.sum()
    )
)


# ============================================================
# 17. CALCULATE NDVI
# ============================================================

print()
print("=" * 70)
print("CALCULATING NDVI")
print("=" * 70)


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

    & (denominator != 0)

)


NDVI[safe_pixels] = (

    (
        B08[safe_pixels]
        -
        B04[safe_pixels]
    )

    /

    (
        B08[safe_pixels]
        +
        B04[safe_pixels]
    )

)


# Keep NDVI between -1 and +1.

NDVI[
    (NDVI < -1)
    |
    (NDVI > 1)
] = np.nan


print()

print(
    "Valid NDVI pixels:",
    int(
        np.isfinite(
            NDVI
        ).sum()
    )
)


# ============================================================
# 18. AGGREGATE TO APPROXIMATELY 100m
# ============================================================

print()
print("=" * 70)
print(
    "AGGREGATING 10m PIXELS "
    "INTO APPROXIMATELY 100m CELLS"
)
print("=" * 70)


height, width = (
    NDVI.shape
)


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
# 19. BLOCK MEAN FUNCTION
# ============================================================

def block_mean(
    array,
    factor
):

    h, w = (
        array.shape
    )


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
# 20. CREATE 100m GRIDS
# ============================================================

print()
print(
    "Creating spatial grids..."
)


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
# 21. CREATE SPATIAL RECORDS
# ============================================================

print()
print("=" * 70)
print("CREATING SPATIAL CSV RECORDS")
print("=" * 70)


records = []


for row in range(
    grid_height
):

    for col in range(
        grid_width
    ):

        ndvi_value = (
            NDVI_GRID[
                row,
                col
            ]
        )


        if not np.isfinite(
            ndvi_value
        ):

            continue


        # ----------------------------------------------------
        # Center of 100m cell
        # ----------------------------------------------------

        source_row = (
            row * FACTOR
            + FACTOR // 2
        )


        source_col = (
            col * FACTOR
            + FACTOR // 2
        )


        # ----------------------------------------------------
        # Convert row/column to raster coordinates
        # ----------------------------------------------------

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"

        )


        # ----------------------------------------------------
        # Convert raster CRS to EPSG:4326
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Band values
        # ----------------------------------------------------

        b02_value = (
            B02_GRID[
                row,
                col
            ]
        )


        b03_value = (
            B03_GRID[
                row,
                col
            ]
        )


        b04_value = (
            B04_GRID[
                row,
                col
            ]
        )


        b08_value = (
            B08_GRID[
                row,
                col
            ]
        )


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


        # ====================================================
        # APPEND RECORD
        # ====================================================

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

            # Actual satellite acquisition date.
            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
                CLOUD_COVER,

            "Grid_Size_m":
                100

        })


# ============================================================
# 22. CREATE DATAFRAME
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
# 23. SAVE SPATIAL CSV
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
# 24. CREATE SUMMARY
# ============================================================

print()
print("=" * 70)
print("CREATING NDVI SUMMARY")
print("=" * 70)


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
            df[
                "NDVI"
            ] >= 0.30
        ).mean()
        * 100

    ],

    "Spatial_Records": [
        len(df)
    ]

})


# ============================================================
# 25. SAVE SUMMARY CSV
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
# 26. CREATE NDVI PNG
# ============================================================

print()
print("=" * 70)
print("CREATING NDVI PNG")
print("=" * 70)


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


print()

print(
    "NDVI PNG saved:"
)

print(
    PNG_FILE
)


# ============================================================
# 27. FINAL RESULTS
# ============================================================

print()
print("=" * 70)
print("                 NDVI COMPLETED")
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
    "Selected Scene Date:",
    SCENE_DATE
)

print(
    "Cloud Cover:",
    CLOUD_COVER,
    "%"
)

print(
    "Spatial Records:",
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

print(
    "Spatial CSV:"
)

print(
    SPATIAL_CSV
)

print()

print(
    "Summary CSV:"
)

print(
    SUMMARY_CSV
)

print()

print(
    "NDVI PNG:"
)

print(
    PNG_FILE
)

print()

print("=" * 70)
print("NDVI SCRIPT FINISHED SUCCESSFULLY")
print("=" * 70)
