import os
import warnings
<<<<<<< HEAD
from datetime import datetime, timezone
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds, transform
from rasterio.transform import xy

from pystac_client import Client
import planetary_computer

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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

<<<<<<< HEAD
NAGPUR_BBOX = [
    78.95,
    20.95,
    79.25,
    21.25
=======
# Nagpur approximate bounding box.
# This is a search/processing area, NOT a political boundary.

NAGPUR_BBOX = [
    78.95,   # West
    20.95,   # South
    79.25,   # East
    21.25    # North
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
]


# ============================================================
# 4. DATE RANGE
# ============================================================

START_DATE = "2026-01-01T00:00:00Z"
<<<<<<< HEAD

# Automatically use current UTC date/time.
# So you don't have to manually change this
# every time you run the script.

END_DATE = datetime.now(
    timezone.utc
).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)
=======
END_DATE = "2026-08-22T23:59:59Z"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

MAX_CLOUD = 20


# ============================================================
# 5. SPATIAL AGGREGATION
# ============================================================

<<<<<<< HEAD
=======
# Sentinel-2 B02/B03/B04/B08 = 10m.
#
# 10 x 10 pixels = approximately 100m grid.

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
FACTOR = 10


# ============================================================
# 6. HEADER
# ============================================================

print()
<<<<<<< HEAD
print("=" * 70)
print("              NAGPUR SENTINEL-2 NDVI")
print("=" * 70)
=======
print("=" * 60)
print("          NAGPUR SENTINEL-2 NDVI")
print("=" * 60)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

<<<<<<< HEAD
print()
print("Search Start Date:")
print(START_DATE)

print()
print("Search End Date:")
print(END_DATE)

print()
print("Maximum Cloud Cover:")
print(f"{MAX_CLOUD}%")

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

# ============================================================
# 7. CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
<<<<<<< HEAD
print("=" * 70)
print("CONNECTING TO PLANETARY COMPUTER")
print("=" * 70)
=======
print("Connecting to Sentinel-2 data source...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

STAC_URL = (
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)

catalog = Client.open(
    STAC_URL
)

<<<<<<< HEAD
print()
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print("Connection successful.")


# ============================================================
<<<<<<< HEAD
# 8. SEARCH SENTINEL-2 IMAGERY
# ============================================================

print()
print("=" * 70)
print("SEARCHING SENTINEL-2 IMAGERY")
print("=" * 70)

search = catalog.search(

=======
# 8. SEARCH SENTINEL-2
# ============================================================

print()
print("Searching Sentinel-2 imagery...")

search = catalog.search(
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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


<<<<<<< HEAD
# ============================================================
# 9. CHECK SCENES
# ============================================================

if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found for "
        "the selected date range and cloud "
        "cover limit."
=======
if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
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
=======
# 9. SORT BY CLOUD COVER
# ============================================================

items.sort(
    key=lambda item:
        item.properties.get(
            "eo:cloud_cover",
            100
        )
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


# ============================================================
<<<<<<< HEAD
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
=======
# 10. SHOW AVAILABLE SCENES
# ============================================================

print()
print("Available scenes:")

for item in items[:10]:

    date = item.datetime.strftime(
        "%Y-%m-%d"
    )

    cloud = item.properties.get(
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        "eo:cloud_cover",
        100
    )

<<<<<<< HEAD

    print(
        f"{index:02d}. "
        f"{scene_date} | "
        f"Cloud: {cloud}% | "
        f"{scene.id}"
=======
    print(
        f"{date} | "
        f"Cloud: {cloud}% | "
        f"{item.id}"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 12. SELECT LATEST SCENE
=======
# 11. SELECT BEST SCENE
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

item = items[0]

<<<<<<< HEAD

# Sign Planetary Computer asset URLs.

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
item = planetary_computer.sign(
    item
)


<<<<<<< HEAD
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


=======
SCENE_DATE = item.datetime.strftime(
    "%Y-%m-%d"
)

CLOUD_COVER = item.properties.get(
    "eo:cloud_cover",
    100
)

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
SCENE_ID = item.id


print()
<<<<<<< HEAD
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
=======
print("Selected scene:")
print("Date:", SCENE_DATE)
print("Cloud cover:", CLOUD_COVER, "%")
print("Scene:", SCENE_ID)


# ============================================================
# 12. FUNCTION TO READ SENTINEL-2 BAND
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

def read_band(
    band_name
):

    asset = item.assets.get(
        band_name
    )

<<<<<<< HEAD

    if asset is None:

        raise RuntimeError(
            f"Sentinel-2 asset not found: "
            f"{band_name}"
=======
    if asset is None:

        raise RuntimeError(
            f"Sentinel-2 asset not found: {band_name}"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )


    with rasterio.open(
        asset.href
    ) as src:

<<<<<<< HEAD
        # ----------------------------------------------------
        # Convert Nagpur WGS84 bounding box
        # into Sentinel-2 raster CRS.
        # ----------------------------------------------------
=======
        # Convert Nagpur WGS84 bbox
        # into the raster CRS.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        left, bottom, right, top = (
            transform_bounds(

                "EPSG:4326",

                src.crs,

                NAGPUR_BBOX[0],
                NAGPUR_BBOX[1],
                NAGPUR_BBOX[2],
                NAGPUR_BBOX[3]
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            )
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Create raster window
        # ----------------------------------------------------
=======
        # Create raster window.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

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


<<<<<<< HEAD
        # ----------------------------------------------------
        # Read raster band
        # ----------------------------------------------------
=======
        # Read band.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Transform of cropped raster
        # ----------------------------------------------------
=======
        # Transform of cropped raster.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        cropped_transform = (
            src.window_transform(
                window
            )
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Raster CRS
        # ----------------------------------------------------
=======
        # CRS of raster.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        raster_crs = src.crs


<<<<<<< HEAD
        # ----------------------------------------------------
        # Sentinel-2 L2A scaling
        # ----------------------------------------------------

        data = (
            data / 10000.0
        )
=======
        # Sentinel-2 L2A scaling.

        data = data / 10000.0
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


        return (
            data,
            cropped_transform,
            raster_crs
        )


# ============================================================
<<<<<<< HEAD
# 14. READ SENTINEL-2 BANDS
# ============================================================

print()
print("=" * 70)
print("READING SENTINEL-2 BANDS")
print("=" * 70)

print()
=======
# 13. READ BANDS
# ============================================================

print()
print("Reading Sentinel-2 bands...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

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
<<<<<<< HEAD
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
=======
# 14. CHECK BAND DIMENSIONS
# ============================================================

print()
print("Band dimensions:")

print("B02:", B02.shape)
print("B03:", B03.shape)
print("B04:", B04.shape)
print("B08:", B08.shape)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


if not (
    B02.shape
    == B03.shape
    == B04.shape
    == B08.shape
):

    raise RuntimeError(
<<<<<<< HEAD
        "B02, B03, B04 and B08 "
        "dimensions do not match."
=======
        "B02, B03, B04 and B08 dimensions do not match."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 16. VALID PIXELS
=======
# 15. VALID PIXELS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


print()
<<<<<<< HEAD

print(
    "Valid 10m pixels:",
    int(
        valid_pixels.sum()
    )
=======
print(
    "Valid 10m pixels:",
    int(valid_pixels.sum())
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


# ============================================================
<<<<<<< HEAD
# 17. CALCULATE NDVI
# ============================================================

print()
print("=" * 70)
print("CALCULATING NDVI")
print("=" * 70)
=======
# 16. CALCULATE NDVI
# ============================================================

print()
print("Calculating NDVI...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


denominator = (
    B08 + B04
)


NDVI = np.full(
    B04.shape,
    np.nan,
    dtype=np.float32
)


safe_pixels = (
<<<<<<< HEAD

    valid_pixels

    & (denominator != 0)

=======
    valid_pixels
    &
    (denominator != 0)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


NDVI[safe_pixels] = (

<<<<<<< HEAD
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
=======
    B08[safe_pixels]
    -
    B04[safe_pixels]

) / (

    B08[safe_pixels]
    +
    B04[safe_pixels]
)


# Keep NDVI within valid range.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

NDVI[
    (NDVI < -1)
    |
    (NDVI > 1)
] = np.nan


<<<<<<< HEAD
print()

print(
    "Valid NDVI pixels:",
    int(
        np.isfinite(
            NDVI
        ).sum()
=======
print(
    "Valid NDVI pixels:",
    int(
        np.isfinite(NDVI).sum()
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )
)


# ============================================================
<<<<<<< HEAD
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
=======
# 17. AGGREGATE TO ~100m
# ============================================================

print()
print(
    "Aggregating 10m pixels into approximately 100m cells..."
)


height, width = NDVI.shape
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


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

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B03 = B03[
    :new_height,
    :new_width
]

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B04 = B04[
    :new_height,
    :new_width
]

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B08 = B08[
    :new_height,
    :new_width
]

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
NDVI = NDVI[
    :new_height,
    :new_width
]


# ============================================================
<<<<<<< HEAD
# 19. BLOCK MEAN FUNCTION
=======
# 18. BLOCK MEAN FUNCTION
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

def block_mean(
    array,
    factor
):

<<<<<<< HEAD
    h, w = (
        array.shape
    )

=======
    h, w = array.shape
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    reshaped = array.reshape(

        h // factor,

        factor,

        w // factor,

        factor
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


    return np.nanmean(
        reshaped,
        axis=(1, 3)
    )


# ============================================================
<<<<<<< HEAD
# 20. CREATE 100m GRIDS
# ============================================================

print()
print(
    "Creating spatial grids..."
)


=======
# 19. CREATE 100m GRIDS
# ============================================================

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B02_GRID = block_mean(
    B02,
    FACTOR
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B03_GRID = block_mean(
    B03,
    FACTOR
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B04_GRID = block_mean(
    B04,
    FACTOR
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
B08_GRID = block_mean(
    B08,
    FACTOR
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
NDVI_GRID = block_mean(
    NDVI,
    FACTOR
)


grid_height, grid_width = (
    NDVI_GRID.shape
)


print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "Spatial grid:",
    grid_height,
    "x",
    grid_width
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "Spatial records:",
    grid_height * grid_width
)


# ============================================================
<<<<<<< HEAD
# 21. CREATE SPATIAL RECORDS
# ============================================================

print()
print("=" * 70)
print("CREATING SPATIAL CSV RECORDS")
print("=" * 70)
=======
# 20. CREATE SPATIAL RECORDS
# ============================================================

print()
print("Creating spatial CSV records...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


records = []


for row in range(
    grid_height
):

    for col in range(
        grid_width
    ):

<<<<<<< HEAD
        ndvi_value = (
            NDVI_GRID[
                row,
                col
            ]
        )
=======
        ndvi_value = NDVI_GRID[
            row,
            col
        ]
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


        if not np.isfinite(
            ndvi_value
        ):

            continue


<<<<<<< HEAD
        # ----------------------------------------------------
        # Center of 100m cell
        # ----------------------------------------------------
=======
        # Center of the 100m cell
        # in the original 10m raster.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        source_row = (
            row * FACTOR
            + FACTOR // 2
        )


        source_col = (
            col * FACTOR
            + FACTOR // 2
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Convert row/column to raster coordinates
        # ----------------------------------------------------
=======
        # Convert row/column to
        # raster coordinates.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"
<<<<<<< HEAD

        )


        # ----------------------------------------------------
        # Convert raster CRS to EPSG:4326
        # ----------------------------------------------------
=======
        )


        # ====================================================
        # IMPORTANT:
        # Convert raster CRS -> EPSG:4326
        #
        # This is the corrected part.
        # ====================================================
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        longitude_list, latitude_list = (
            transform(

                raster_crs,

                "EPSG:4326",

                [x],

                [y]
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            )
        )


        longitude = (
            longitude_list[0]
        )

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        latitude = (
            latitude_list[0]
        )


<<<<<<< HEAD
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
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


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


<<<<<<< HEAD
        # ====================================================
        # APPEND RECORD
        # ====================================================

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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

<<<<<<< HEAD
            # Actual satellite acquisition date.
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
                CLOUD_COVER,

            "Grid_Size_m":
                100

        })


# ============================================================
<<<<<<< HEAD
# 22. CREATE DATAFRAME
=======
# 21. CREATE DATAFRAME
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise RuntimeError(
        "Spatial NDVI dataset is empty."
    )


print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "Final spatial records:",
    len(df)
)


# ============================================================
<<<<<<< HEAD
# 23. SAVE SPATIAL CSV
=======
# 22. SAVE SPATIAL CSV
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

df.to_csv(
    SPATIAL_CSV,
    index=False
)


print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "Spatial CSV saved:"
)

print(
    SPATIAL_CSV
)


# ============================================================
<<<<<<< HEAD
# 24. CREATE SUMMARY
# ============================================================

print()
print("=" * 70)
print("CREATING NDVI SUMMARY")
print("=" * 70)


=======
# 23. CREATE SUMMARY
# ============================================================

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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
<<<<<<< HEAD
            df[
                "NDVI"
            ] >= 0.30
        ).mean()
        * 100

=======
            df["NDVI"] >= 0.30
        ).mean()
        * 100
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ],

    "Spatial_Records": [
        len(df)
    ]

})


<<<<<<< HEAD
# ============================================================
# 25. SAVE SUMMARY CSV
# ============================================================

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
summary_df.to_csv(
    SUMMARY_CSV,
    index=False
)


print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "Summary CSV saved:"
)

print(
    SUMMARY_CSV
)


# ============================================================
<<<<<<< HEAD
# 26. CREATE NDVI PNG
# ============================================================

print()
print("=" * 70)
print("CREATING NDVI PNG")
print("=" * 70)
=======
# 24. CREATE NDVI PNG
# ============================================================

print()
print(
    "Creating NDVI PNG..."
)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


plt.figure(
    figsize=(12, 9)
)


plt.imshow(

    NDVI_GRID,

    cmap="RdYlGn",

    vmin=-1,

    vmax=1
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
plt.ylabel(
    "100m Grid"
)


plt.tight_layout()


plt.savefig(

    PNG_FILE,

    dpi=300,

    bbox_inches="tight"
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


plt.close()


<<<<<<< HEAD
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
=======
# ============================================================
# 25. FINAL RESULTS
# ============================================================

print()
print("=" * 60)
print("              NDVI COMPLETED")
print("=" * 60)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()

print(
    "Satellite:",
    "Sentinel-2"
)

print(
<<<<<<< HEAD
    "Product:",
    "Sentinel-2 L2A"
)

print(
    "Selected Scene Date:",
=======
    "Scene date:",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    SCENE_DATE
)

print(
<<<<<<< HEAD
    "Cloud Cover:",
=======
    "Cloud cover:",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    CLOUD_COVER,
    "%"
)

print(
<<<<<<< HEAD
    "Spatial Records:",
=======
    "Spatial records:",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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
<<<<<<< HEAD

print(
    "Spatial CSV:"
=======
print("FILES CREATED")

print()
print(
    "1. Spatial CSV:"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

print(
    SPATIAL_CSV
)

print()
<<<<<<< HEAD

print(
    "Summary CSV:"
=======
print(
    "2. Summary CSV:"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

print(
    SUMMARY_CSV
)

print()
<<<<<<< HEAD

print(
    "NDVI PNG:"
=======
print(
    "3. NDVI PNG:"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

print(
    PNG_FILE
)

print()
<<<<<<< HEAD

print("=" * 70)
print("NDVI SCRIPT FINISHED SUCCESSFULLY")
print("=" * 70)
=======
print(
    "Google Earth Engine: NOT USED"
)

print(
    "GeoJSON boundary: NOT REQUIRED"
)

print()
print("=" * 60)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
