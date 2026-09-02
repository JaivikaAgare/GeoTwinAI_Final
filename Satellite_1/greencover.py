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
<<<<<<< HEAD
    os.path.abspath(__file__)
=======
    os.path.dirname(
        os.path.abspath(__file__)
    )
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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
    "Nagpur_GreenCover_Spatial.csv"
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_GreenCover_Summary.csv"
)

PNG_FILE = os.path.join(
    OUTPUT_DIR,
    "Nagpur_GreenCover.png"
)


# ============================================================
<<<<<<< HEAD
# 3. NAGPUR BOUNDING BOX
# ============================================================
#
# No shapefile required.
#
# WGS84:
# min longitude
# min latitude
# max longitude
# max latitude
#
# ============================================================

NAGPUR_BBOX = [
    78.95,
    21.05,
    79.20,
    21.25
=======
# 3. NAGPUR PROCESSING AREA
# ============================================================
# This is a processing/search box.
# It is NOT a political boundary.

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

END_DATE = datetime.now(
    timezone.utc
).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)


# ============================================================
# 5. PROCESSING SETTINGS
# ============================================================

MAX_CLOUD = 20

NDVI_THRESHOLD = 0.30

# Sentinel-2 B04/B08 = 10m
PIXEL_SIZE_M = 10

# 10 x 10 = approximately 100m x 100m
FACTOR = 10

# 10m x 10m = 100 m2 = 0.01 hectare
PIXEL_AREA_HA = 0.01


# ============================================================
# 6. HEADER
# ============================================================

print()
print("=" * 70)
print("       NAGPUR SENTINEL-2 GREEN COVER ANALYSIS")
print("=" * 70)
=======
END_DATE = "2026-08-22T23:59:59Z"

MAX_CLOUD = 20


# ============================================================
# 5. GREEN-COVER DEFINITION
# ============================================================
# NDVI >= 0.30 is classified as vegetated/green cover.
#
# This threshold is kept explicitly in the output.

GREEN_NDVI_THRESHOLD = 0.30


# ============================================================
# 6. SPATIAL GRID
# ============================================================
# Sentinel-2 B04 and B08 are 10 m.
#
# 10 x 10 pixels = approximately 100 m x 100 m.

FACTOR = 10


# ============================================================
# 7. HEADER
# ============================================================

print()
print("=" * 65)
print("              NAGPUR SENTINEL-2 GREEN COVER")
print("=" * 65)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

<<<<<<< HEAD
print()
print("Nagpur BBOX:")
print(
    NAGPUR_BBOX
)

print()
print("Search Start Date:")
print(START_DATE)

print()
print("Search End Date:")
print(END_DATE)

print()
print("Maximum Cloud Cover:")
print(
    f"{MAX_CLOUD}%"
)

print()
print("NDVI Green Cover Threshold:")
print(
    NDVI_THRESHOLD
)

print()
print("10m Pixel Area:")
print(
    PIXEL_AREA_HA,
    "ha"
)


# ============================================================
# 7. CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
print("=" * 70)
print("CONNECTING TO PLANETARY COMPUTER")
print("=" * 70)
=======

# ============================================================
# 8. CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
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
# 8. SEARCH SENTINEL-2 L2A
# ============================================================

print()
print("=" * 70)
print("SEARCHING SENTINEL-2 IMAGERY")
print("=" * 70)

search = catalog.search(

=======
# 9. SEARCH SENTINEL-2 L2A
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

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
items = list(
    search.items()
)

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print()
print(
    "Number of Sentinel-2 scenes found:",
    len(items)
)


if len(items) == 0:

    raise RuntimeError(
<<<<<<< HEAD
        "No Sentinel-2 scenes found."
=======
        "No Sentinel-2 scenes found for Nagpur."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 9. CHECK REQUIRED BANDS
# ============================================================

valid_items = []

for scene in items:

    if (
        scene.assets.get("B04")
        is not None
        and
        scene.assets.get("B08")
        is not None
    ):

        valid_items.append(
            scene
        )


print()
print(
    "Scenes with B04 and B08:",
    len(valid_items)
)


if len(valid_items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scene contains B04 and B08."
    )


# ============================================================
# 10. SORT BY DATE
# ============================================================

def get_scene_datetime(item):

    dt = item.datetime

    if dt is None:

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    if dt.tzinfo is None:

        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt


valid_items.sort(
    key=get_scene_datetime,
    reverse=True
=======
# 10. SORT BY CLOUD COVER
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
# 11. SHOW LATEST SCENES
# ============================================================

print()
print("=" * 70)
print("LATEST AVAILABLE SENTINEL-2 SCENES")
print("=" * 70)

print()

for index, scene in enumerate(
    valid_items[:15],
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
        f"Cloud: {cloud:.2f}% | "
        f"{scene.id}"
=======
# 11. SHOW AVAILABLE SCENES
# ============================================================

print()
print("Available scenes:")

for item_temp in items[:10]:

    date_temp = (
        item_temp.datetime.strftime(
            "%Y-%m-%d"
        )
    )

    cloud_temp = (
        item_temp.properties.get(
            "eo:cloud_cover",
            100
        )
    )

    print(
        f"{date_temp} | "
        f"Cloud: {cloud_temp}% | "
        f"{item_temp.id}"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 12. SELECT LATEST SCENE
# ============================================================

item = valid_items[0]

=======
# 12. SELECT BEST SCENE
# ============================================================

item = items[0]
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

item = planetary_computer.sign(
    item
)


SCENE_DATE = (
    item.datetime.strftime(
        "%Y-%m-%d"
    )
)

<<<<<<< HEAD

CLOUD_COVER = item.properties.get(
    "eo:cloud_cover",
    100
)


=======
CLOUD_COVER = (
    item.properties.get(
        "eo:cloud_cover",
        100
    )
)

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
SCENE_ID = item.id


print()
<<<<<<< HEAD
print("=" * 70)
print("SELECTED SENTINEL-2 SCENE")
print("=" * 70)

print()
print("Date:")
print(
    SCENE_DATE
)

print()
print("Cloud cover:")
print(
    round(
        CLOUD_COVER,
        2
    ),
    "%"
)

print()
print("Scene:")
print(
    SCENE_ID
)
=======
print("Selected scene:")
print("Date:", SCENE_DATE)
print("Cloud cover:", CLOUD_COVER, "%")
print("Scene:", SCENE_ID)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


# ============================================================
# 13. READ SENTINEL-2 BAND
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
            f"Asset not found: {band_name}"
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
        print()
        print(
            f"Reading {band_name}"
        )

        print(
            "Source CRS:",
            src.crs
        )

        print(
            "Source size:",
            src.width,
            "x",
            src.height
        )


        # ----------------------------------------------------
        # Convert Nagpur BBOX to raster CRS
        # ----------------------------------------------------
=======
        # Convert WGS84 Nagpur box
        # into raster CRS.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        left, bottom, right, top = (
            transform_bounds(

                "EPSG:4326",

                src.crs,

                NAGPUR_BBOX[0],
                NAGPUR_BBOX[1],
                NAGPUR_BBOX[2],
<<<<<<< HEAD
                NAGPUR_BBOX[3],

                densify_pts=21
=======
                NAGPUR_BBOX[3]
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            )
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Create raster window
        # ----------------------------------------------------

=======
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
        print(
            "Reading window:",
            int(window.width),
            "x",
            int(window.height)
        )


        # ----------------------------------------------------
        # Read data
        # ----------------------------------------------------

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # Cropped transform
        # ----------------------------------------------------

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        cropped_transform = (
            src.window_transform(
                window
            )
        )


<<<<<<< HEAD
        return (
            data,
            cropped_transform,
            src.crs
=======
        raster_crs = src.crs


        # Sentinel-2 L2A reflectance scaling.

        data = data / 10000.0


        return (
            data,
            cropped_transform,
            raster_crs
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )


# ============================================================
<<<<<<< HEAD
# 14. READ B04
# ============================================================

print()
print("=" * 70)
print("READING B04 - RED")
print("=" * 70)

B04, raster_transform, raster_crs = (
    read_band(
        "B04"
    )
)


# ============================================================
# 15. READ B08
# ============================================================

print()
print("=" * 70)
print("READING B08 - NIR")
print("=" * 70)

B08, _, _ = (
    read_band(
        "B08"
    )
=======
# 14. READ B04 AND B08
# ============================================================

print()
print("Reading Sentinel-2 bands...")

print("B04 - Red")

B04, raster_transform, raster_crs = (
    read_band("B04")
)

print("B08 - Near Infrared")

B08, _, _ = (
    read_band("B08")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


# ============================================================
<<<<<<< HEAD
# 16. DIMENSION CHECK
# ============================================================

print()
print("=" * 70)
print("BAND DIMENSIONS")
print("=" * 70)

print()
print(
    "B04:",
    B04.shape
)

print(
    "B08:",
    B08.shape
)
=======
# 15. CHECK DIMENSIONS
# ============================================================

print()
print("Band dimensions:")

print("B04:", B04.shape)
print("B08:", B08.shape)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


if B04.shape != B08.shape:

    raise RuntimeError(
        "B04 and B08 dimensions do not match."
    )


# ============================================================
<<<<<<< HEAD
# 17. CONVERT SENTINEL-2 SCALE
# ============================================================

B04 = (
    B04 / 10000.0
)

B08 = (
    B08 / 10000.0
)


# ============================================================
# 18. VALID PIXELS
=======
# 16. VALID PIXELS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

valid_pixels = (

    np.isfinite(B04)

    & np.isfinite(B08)

    & (B04 >= 0)

    & (B08 >= 0)
<<<<<<< HEAD

)


valid_pixel_count = int(
    valid_pixels.sum()
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


print()
print(
    "Valid 10m pixels:",
<<<<<<< HEAD
    valid_pixel_count
=======
    int(valid_pixels.sum())
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


# ============================================================
<<<<<<< HEAD
# 19. CALCULATE NDVI
# ============================================================

print()
print("=" * 70)
print("CALCULATING NDVI")
print("=" * 70)

=======
# 17. CALCULATE NDVI
# ============================================================

print()
print("Calculating NDVI for green-cover detection...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

denominator = (
    B08 + B04
)


NDVI = np.full(
<<<<<<< HEAD

    B04.shape,

    np.nan,

=======
    B04.shape,
    np.nan,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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


NDVI[

    (NDVI < -1)

    |

    (NDVI > 1)

] = np.nan


=======
    B08[safe_pixels]
    -
    B04[safe_pixels]

) / (

    B08[safe_pixels]
    +
    B04[safe_pixels]
)


# Remove impossible values.

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
# 18. GREEN COVER MASK
# ============================================================

print()
print(
    "Detecting green cover using NDVI threshold:",
    GREEN_NDVI_THRESHOLD
)


green_cover_mask = (

    np.isfinite(NDVI)

    & (
        NDVI
        >= GREEN_NDVI_THRESHOLD
    )
)


green_pixels = int(
    green_cover_mask.sum()
)


>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
valid_ndvi_pixels = int(
    np.isfinite(NDVI).sum()
)


print()
print(
<<<<<<< HEAD
    "Valid NDVI pixels:",
    valid_ndvi_pixels
)


# ============================================================
# 20. GREEN COVER AT 10m
# ============================================================

print()
print("=" * 70)
print("CALCULATING GREEN COVER")
print("=" * 70)


green_mask = (

    np.isfinite(NDVI)

    & (NDVI >= NDVI_THRESHOLD)

)


green_pixels = int(
    green_mask.sum()
)


print()
print(
    "NDVI Threshold:",
    NDVI_THRESHOLD
)

print(
    "Green 10m pixels:",
    green_pixels
)

print(
    "Valid NDVI pixels:",
    valid_ndvi_pixels
)


# ============================================================
# 21. CORRECT 10m GREEN AREA
# ============================================================

green_area_ha_10m = (

    green_pixels

    *

    PIXEL_AREA_HA

)


valid_area_ha_10m = (

    valid_ndvi_pixels

    *

    PIXEL_AREA_HA

)


if valid_ndvi_pixels > 0:

    green_percentage_10m = (

        green_pixels

        /

        valid_ndvi_pixels

        *

        100

    )

else:

    green_percentage_10m = 0


print()
print(
    "Green Cover Area (10m):",
    round(
        green_area_ha_10m,
        2
    ),
    "ha"
)

print(
    "Valid Area:",
    round(
        valid_area_ha_10m,
        2
    ),
    "ha"
)

print(
    "Green Cover Percentage:",
    round(
        green_percentage_10m,
=======
    "Green-cover 10m pixels:",
    green_pixels
)


print(
    "Green-cover percentage:",
    round(
        (
            green_pixels
            /
            valid_ndvi_pixels
        )
        * 100,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        2
    ),
    "%"
)


# ============================================================
<<<<<<< HEAD
# 22. PREPARE 100m GRID
# ============================================================

print()
print("=" * 70)
print("AGGREGATING TO APPROXIMATELY 100m CELLS")
print("=" * 70)
=======
# 19. AGGREGATE TO APPROX. 100m
# ============================================================

print()
print(
    "Aggregating 10m pixels into approximately 100m cells..."
)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


height, width = NDVI.shape


new_height = (
    height // FACTOR
) * FACTOR


new_width = (
    width // FACTOR
) * FACTOR


<<<<<<< HEAD
=======
B04 = B04[
    :new_height,
    :new_width
]

B08 = B08[
    :new_height,
    :new_width
]

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
NDVI = NDVI[
    :new_height,
    :new_width
]

<<<<<<< HEAD

green_mask = green_mask[
=======
green_cover_mask = green_cover_mask[
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    :new_height,
    :new_width
]


# ============================================================
<<<<<<< HEAD
# 23. BLOCK MEAN
=======
# 20. BLOCK MEAN FUNCTION
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

def block_mean(
    array,
    factor
):

    h, w = array.shape

<<<<<<< HEAD

=======
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
<<<<<<< HEAD

        reshaped,

        axis=(1, 3)

=======
        reshaped,
        axis=(1, 3)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 24. GREEN FRACTION
# ============================================================

def block_green_fraction(

    mask,
    factor

=======
# 21. BLOCK GREEN-COVER PERCENTAGE
# ============================================================

def block_green_percentage(
    mask,
    factor
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
):

    h, w = mask.shape

<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    reshaped = mask.reshape(

        h // factor,

        factor,

        w // factor,

        factor
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


    return (
<<<<<<< HEAD

        reshaped.mean(
            axis=(1, 3)
        )

=======
        reshaped.mean(
            axis=(1, 3)
        )
        * 100
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# 25. CREATE 100m NDVI GRID
# ============================================================

NDVI_GRID = block_mean(

    NDVI,

    FACTOR

)


# ============================================================
# 26. CREATE GREEN FRACTION GRID
# ============================================================

GREEN_FRACTION_GRID = (
    block_green_fraction(
        green_mask,
=======
# 22. CREATE SPATIAL GRIDS
# ============================================================

NDVI_GRID = block_mean(
    NDVI,
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


GREEN_PERCENT_GRID = (
    block_green_percentage(
        green_cover_mask,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        FACTOR
    )
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

<<<<<<< HEAD
print(
    "Potential cells:",
=======

print(
    "Potential spatial cells:",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    grid_height * grid_width
)


# ============================================================
<<<<<<< HEAD
# 27. CREATE SPATIAL RECORDS
# ============================================================

print()
print("=" * 70)
print("CREATING GREEN COVER SPATIAL RECORDS")
print("=" * 70)
=======
# 23. CREATE SPATIAL CSV
# ============================================================

print()
print(
    "Creating green-cover spatial records..."
)
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


        green_fraction = (
            GREEN_FRACTION_GRID[
=======
        ndvi_value = NDVI_GRID[
            row,
            col
        ]


        green_percentage = (
            GREEN_PERCENT_GRID[
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
                row,
                col
            ]
        )


        if not np.isfinite(
            ndvi_value
        ):

            continue


<<<<<<< HEAD
        if not np.isfinite(
            green_fraction
        ):

            continue


        # ----------------------------------------------------
        # Center pixel of 100m block
        # ----------------------------------------------------

        source_row = (

            row * FACTOR

            +

            FACTOR // 2

=======
        # Center of the 100m cell.

        source_row = (
            row * FACTOR
            + FACTOR // 2
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )


        source_col = (
<<<<<<< HEAD

            col * FACTOR

            +

            FACTOR // 2

        )


        # ----------------------------------------------------
        # Raster coordinates
        # ----------------------------------------------------
=======
            col * FACTOR
            + FACTOR // 2
        )


        # Raster row/column
        # -> projected coordinate.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"
<<<<<<< HEAD

        )


        # ----------------------------------------------------
        # Convert to WGS84
        # ----------------------------------------------------

        longitude_list, latitude_list = transform(

            raster_crs,

            "EPSG:4326",

            [x],

            [y]

=======
        )


        # Projected CRS -> WGS84.

        longitude_list, latitude_list = (
            transform(

                raster_crs,

                "EPSG:4326",

                [x],

                [y]
            )
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )


        longitude = (
            longitude_list[0]
        )

        latitude = (
            latitude_list[0]
        )


<<<<<<< HEAD
        # ----------------------------------------------------
        # 100m cell area
        # ----------------------------------------------------

        cell_area_ha = 1.0


        # ----------------------------------------------------
        # ACTUAL GREEN AREA
        #
        # Example:
        #
        # 70% of 100m cell green
        #
        # green area = 0.70 ha
        #
        # ----------------------------------------------------

        green_area_ha = (

            green_fraction

            *

            cell_area_ha

        )


        green_percent = (

            green_fraction

            *

            100

        )


        # ----------------------------------------------------
        # Green status
        # ----------------------------------------------------

        if green_fraction >= 0.5:

            green_status = (
                "Green Cover"
            )

            green_flag = 1

        else:

            green_status = (
                "Non-Green Cover"
            )

            green_flag = 0


        # ----------------------------------------------------
        # Append
        # ----------------------------------------------------

        records.append({

            "Region":
                "Nagpur",

=======
        # Approximate area represented
        # by each 100m cell.

        cell_area_m2 = 100 * 100

        green_area_m2 = (
            green_percentage
            / 100
            * cell_area_m2
        )

        green_area_ha = (
            green_area_m2
            / 10000
        )


        # Green-cover class.

        if green_percentage >= 75:

            green_class = (
                "Very High Green Cover"
            )

        elif green_percentage >= 50:

            green_class = (
                "High Green Cover"
            )

        elif green_percentage >= 25:

            green_class = (
                "Moderate Green Cover"
            )

        elif green_percentage > 0:

            green_class = (
                "Low Green Cover"
            )

        else:

            green_class = (
                "No Green Cover"
            )


        records.append({

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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

<<<<<<< HEAD
            "NDVI":
=======
            "NDVI_Mean":
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
                round(
                    float(
                        ndvi_value
                    ),
                    6
                ),

<<<<<<< HEAD
            "NDVI_Threshold":
                NDVI_THRESHOLD,

            "Green_Cover":
                green_status,

            "Green_Flag":
                green_flag,

            "Green_Fraction":
                round(
                    float(
                        green_fraction
                    ),
                    6
                ),

            "Green_Cover_Percent":
                round(
                    float(
                        green_percent
=======
            "Green_Cover_Percent":
                round(
                    float(
                        green_percentage
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
                    ),
                    2
                ),

<<<<<<< HEAD
            "Cell_Area_ha":
                cell_area_ha,
=======
            "Green_Cover_Area_m2":
                round(
                    float(
                        green_area_m2
                    ),
                    2
                ),
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

            "Green_Cover_Area_ha":
                round(
                    float(
                        green_area_ha
                    ),
                    6
                ),

<<<<<<< HEAD
=======
            "Green_Cover_Class":
                green_class,

            "B04_Red_Mean":
                round(
                    float(
                        B04_GRID[
                            row,
                            col
                        ]
                    ),
                    6
                ),

            "B08_NIR_Mean":
                round(
                    float(
                        B08_GRID[
                            row,
                            col
                        ]
                    ),
                    6
                ),

            "NDVI_Threshold":
                GREEN_NDVI_THRESHOLD,

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            "Satellite":
                "Sentinel-2",

            "Product":
                "Sentinel-2 L2A",

            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
<<<<<<< HEAD
                round(
                    float(
                        CLOUD_COVER
                    ),
                    4
                ),

            "Grid_Size_m":
                100

=======
                CLOUD_COVER,

            "Grid_Size_m":
                100,

            "Data_Source":
                "Microsoft Planetary Computer Sentinel-2 L2A"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        })


# ============================================================
<<<<<<< HEAD
# 28. CREATE DATAFRAME
=======
# 24. DATAFRAME
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise RuntimeError(
<<<<<<< HEAD
        "Green Cover spatial dataset is empty."
=======
        "Green-cover spatial dataset is empty."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


print()
print(
    "Final spatial records:",
    len(df)
)


# ============================================================
<<<<<<< HEAD
# 29. CORRECT AREA CALCULATION
# ============================================================

processed_area_ha = (

    df["Cell_Area_ha"]

    *

    df["Green_Fraction"].notna()

).sum()


green_cover_area_ha = (
    df[
        "Green_Cover_Area_ha"
    ].sum()
)


if processed_area_ha > 0:

    green_cover_percent = (

        green_cover_area_ha

        /

        processed_area_ha

        *

        100

    )

else:

    green_cover_percent = 0


mean_ndvi = (
    df["NDVI"].mean()
)


min_ndvi = (
    df["NDVI"].min()
)


max_ndvi = (
    df["NDVI"].max()
)


mean_green_fraction = (
    df[
        "Green_Fraction"
    ].mean()
)


print()
print("=" * 70)
print("GREEN COVER STATISTICS")
print("=" * 70)


print()
print(
    "Processed Area (ha):",
    round(
        processed_area_ha,
        2
    )
)


print(
    "Green Cover Area (ha):",
    round(
        green_cover_area_ha,
        2
    )
)


print(
    "Green Cover Percentage:",
    round(
        green_cover_percent,
        2
    ),
    "%"
)


print(
    "Mean Green Fraction:",
    round(
        mean_green_fraction,
        4
    )
)


print(
    "Mean NDVI:",
    round(
        mean_ndvi,
        4
    )
)


print(
    "Minimum NDVI:",
    round(
        min_ndvi,
        4
    )
)


print(
    "Maximum NDVI:",
    round(
        max_ndvi,
        4
    )
)


# ============================================================
# 30. SAVE SPATIAL CSV
# ============================================================

df.to_csv(

    SPATIAL_CSV,

    index=False

=======
# 25. SAVE SPATIAL CSV
# ============================================================

df.to_csv(
    SPATIAL_CSV,
    index=False
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


print()
print(
    "Spatial CSV saved:"
)

print(
    SPATIAL_CSV
)


# ============================================================
<<<<<<< HEAD
# 31. SUMMARY CSV
# ============================================================

=======
# 26. SUMMARY STATISTICS
# ============================================================

total_area_ha = (
    len(df)
    * 1.0
)


green_area_ha = (
    df[
        "Green_Cover_Area_ha"
    ].sum()
)


green_percentage = (

    green_area_ha
    /
    total_area_ha
) * 100


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

    "NDVI_Threshold": [
<<<<<<< HEAD
        NDVI_THRESHOLD
=======
        GREEN_NDVI_THRESHOLD
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ],

    "Spatial_Records": [
        len(df)
    ],

<<<<<<< HEAD
    "Processed_Area_ha": [
        processed_area_ha
    ],

    "Green_Cover_Area_ha": [
        green_cover_area_ha
    ],

    "Green_Cover_Percent": [
        green_cover_percent
    ],

    "Mean_Green_Fraction": [
        mean_green_fraction
    ],

    "Mean_NDVI": [
        mean_ndvi
    ],

    "Min_NDVI": [
        min_ndvi
    ],

    "Max_NDVI": [
        max_ndvi
    ],

    "Data_Source": [
        "Microsoft Planetary Computer"
=======
    "Green_Cover_Area_ha": [
        round(
            green_area_ha,
            4
        )
    ],

    "Processed_Area_ha": [
        round(
            total_area_ha,
            4
        )
    ],

    "Green_Cover_Percent": [
        round(
            green_percentage,
            2
        )
    ],

    "Mean_NDVI": [
        round(
            df[
                "NDVI_Mean"
            ].mean(),
            4
        )
    ],

    "Min_NDVI": [
        round(
            df[
                "NDVI_Mean"
            ].min(),
            4
        )
    ],

    "Max_NDVI": [
        round(
            df[
                "NDVI_Mean"
            ].max(),
            4
        )
    ],

    "Data_Source": [
        "Microsoft Planetary Computer Sentinel-2 L2A"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]

})


summary_df.to_csv(
<<<<<<< HEAD

    SUMMARY_CSV,

    index=False

=======
    SUMMARY_CSV,
    index=False
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


print()
print(
    "Summary CSV saved:"
)

print(
    SUMMARY_CSV
)


# ============================================================
<<<<<<< HEAD
# 32. CREATE GREEN COVER MAP
# ============================================================

print()
print("=" * 70)
print("CREATING GREEN COVER PNG")
print("=" * 70)


green_map = np.where(

    np.isfinite(
        GREEN_FRACTION_GRID
    ),

    GREEN_FRACTION_GRID,

    np.nan

=======
# 27. CREATE PNG
# ============================================================

print()
print(
    "Creating Green Cover PNG..."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


plt.figure(
    figsize=(12, 9)
)


plt.imshow(

<<<<<<< HEAD
    green_map,

    cmap="RdYlGn",

    vmin=0,

    vmax=1

=======
    GREEN_PERCENT_GRID,

    cmap="YlGn",

    vmin=0,

    vmax=100
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


plt.colorbar(
<<<<<<< HEAD
    label="Green Cover Fraction"
)


plt.contour(

    GREEN_FRACTION_GRID >= 0.5,

    levels=[0.5],

    linewidths=1.5

=======
    label="Green Cover (%)"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


plt.title(
<<<<<<< HEAD

    "Nagpur Sentinel-2 Green Cover\n"

    f"Scene Date: {SCENE_DATE}\n"

    f"NDVI Threshold: {NDVI_THRESHOLD}"

=======
    "Nagpur Sentinel-2 Green Cover\n"
    f"Scene Date: {SCENE_DATE}"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
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
    "Green Cover PNG saved:"
)

print(
    PNG_FILE
)


# ============================================================
# 33. FINAL RESULTS
# ============================================================

print()
print("=" * 70)
print("             GREEN COVER ANALYSIS COMPLETED")
print("=" * 70)
=======
# ============================================================
# 28. FINAL OUTPUT
# ============================================================

print()
print("=" * 65)
print("              GREEN COVER COMPLETED")
print("=" * 65)
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
    round(
        CLOUD_COVER,
        2
    ),
=======
    "Cloud cover:",
    CLOUD_COVER,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    "%"
)

print(
<<<<<<< HEAD
    "NDVI Threshold:",
    NDVI_THRESHOLD
)

print(
    "Spatial Records:",
=======
    "NDVI threshold:",
    GREEN_NDVI_THRESHOLD
)

print(
    "Spatial records:",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    len(df)
)

print(
<<<<<<< HEAD
    "Processed Area (ha):",
    round(
        processed_area_ha,
        2
    )
)

print(
    "Green Cover Area (ha):",
    round(
        green_cover_area_ha,
        2
    )
)

print(
    "Green Cover Percentage:",
    round(
        green_cover_percent,
=======
    "Green-cover area:",
    round(
        green_area_ha,
        2
    ),
    "ha"
)

print(
    "Green-cover percentage:",
    round(
        green_percentage,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        2
    ),
    "%"
)

<<<<<<< HEAD
print(
    "Mean NDVI:",
    round(
        mean_ndvi,
        4
    )
)

print(
    "Minimum NDVI:",
    round(
        min_ndvi,
        4
    )
)

print(
    "Maximum NDVI:",
    round(
        max_ndvi,
        4
    )
)

print()
print("=" * 70)
print("FILES CREATED")
print("=" * 70)

print()

=======
print()
print("FILES CREATED")

print()
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "1. Spatial CSV:"
)

print(
    SPATIAL_CSV
)

print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "2. Summary CSV:"
)

print(
    SUMMARY_CSV
)

print()
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print(
    "3. Green Cover PNG:"
)

print(
    PNG_FILE
)

print()
<<<<<<< HEAD

print(
    "Data Source:",
    "Microsoft Planetary Computer"
)

print()
print("=" * 70)
print("GREEN COVER SCRIPT FINISHED SUCCESSFULLY")
print("=" * 70)
=======
print(
    "Google Earth Engine: NOT USED"
)

print(
    "GeoJSON boundary: NOT REQUIRED"
)

print()
print("=" * 65)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
