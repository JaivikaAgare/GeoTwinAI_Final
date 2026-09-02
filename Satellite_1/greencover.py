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
    os.path.abspath(__file__)
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
]


# ============================================================
# 4. DATE RANGE
# ============================================================

START_DATE = "2026-01-01T00:00:00Z"

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

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

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

STAC_URL = (
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)

catalog = Client.open(
    STAC_URL
)

print()
print("Connection successful.")


# ============================================================
# 8. SEARCH SENTINEL-2 L2A
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


if len(items) == 0:

    raise RuntimeError(
        "No Sentinel-2 scenes found."
    )


# ============================================================
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
)


# ============================================================
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
    )


# ============================================================
# 12. SELECT LATEST SCENE
# ============================================================

item = valid_items[0]


item = planetary_computer.sign(
    item
)


SCENE_DATE = (
    item.datetime.strftime(
        "%Y-%m-%d"
    )
)


CLOUD_COVER = item.properties.get(
    "eo:cloud_cover",
    100
)


SCENE_ID = item.id


print()
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


# ============================================================
# 13. READ SENTINEL-2 BAND
# ============================================================

def read_band(
    band_name
):

    asset = item.assets.get(
        band_name
    )


    if asset is None:

        raise RuntimeError(
            f"Asset not found: {band_name}"
        )


    with rasterio.open(
        asset.href
    ) as src:

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

        left, bottom, right, top = (
            transform_bounds(

                "EPSG:4326",

                src.crs,

                NAGPUR_BBOX[0],
                NAGPUR_BBOX[1],
                NAGPUR_BBOX[2],
                NAGPUR_BBOX[3],

                densify_pts=21
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


        print(
            "Reading window:",
            int(window.width),
            "x",
            int(window.height)
        )


        # ----------------------------------------------------
        # Read data
        # ----------------------------------------------------

        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


        # ----------------------------------------------------
        # Cropped transform
        # ----------------------------------------------------

        cropped_transform = (
            src.window_transform(
                window
            )
        )


        return (
            data,
            cropped_transform,
            src.crs
        )


# ============================================================
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
)


# ============================================================
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


if B04.shape != B08.shape:

    raise RuntimeError(
        "B04 and B08 dimensions do not match."
    )


# ============================================================
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
# ============================================================

valid_pixels = (

    np.isfinite(B04)

    & np.isfinite(B08)

    & (B04 >= 0)

    & (B08 >= 0)

)


valid_pixel_count = int(
    valid_pixels.sum()
)


print()
print(
    "Valid 10m pixels:",
    valid_pixel_count
)


# ============================================================
# 19. CALCULATE NDVI
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


NDVI[

    (NDVI < -1)

    |

    (NDVI > 1)

] = np.nan


valid_ndvi_pixels = int(
    np.isfinite(NDVI).sum()
)


print()
print(
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
        2
    ),
    "%"
)


# ============================================================
# 22. PREPARE 100m GRID
# ============================================================

print()
print("=" * 70)
print("AGGREGATING TO APPROXIMATELY 100m CELLS")
print("=" * 70)


height, width = NDVI.shape


new_height = (
    height // FACTOR
) * FACTOR


new_width = (
    width // FACTOR
) * FACTOR


NDVI = NDVI[
    :new_height,
    :new_width
]


green_mask = green_mask[
    :new_height,
    :new_width
]


# ============================================================
# 23. BLOCK MEAN
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
# 24. GREEN FRACTION
# ============================================================

def block_green_fraction(

    mask,
    factor

):

    h, w = mask.shape


    reshaped = mask.reshape(

        h // factor,

        factor,

        w // factor,

        factor

    )


    return (

        reshaped.mean(
            axis=(1, 3)
        )

    )


# ============================================================
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

print(
    "Potential cells:",
    grid_height * grid_width
)


# ============================================================
# 27. CREATE SPATIAL RECORDS
# ============================================================

print()
print("=" * 70)
print("CREATING GREEN COVER SPATIAL RECORDS")
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


        green_fraction = (
            GREEN_FRACTION_GRID[
                row,
                col
            ]
        )


        if not np.isfinite(
            ndvi_value
        ):

            continue


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

        )


        source_col = (

            col * FACTOR

            +

            FACTOR // 2

        )


        # ----------------------------------------------------
        # Raster coordinates
        # ----------------------------------------------------

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"

        )


        # ----------------------------------------------------
        # Convert to WGS84
        # ----------------------------------------------------

        longitude_list, latitude_list = transform(

            raster_crs,

            "EPSG:4326",

            [x],

            [y]

        )


        longitude = (
            longitude_list[0]
        )

        latitude = (
            latitude_list[0]
        )


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

            "NDVI":
                round(
                    float(
                        ndvi_value
                    ),
                    6
                ),

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
                    ),
                    2
                ),

            "Cell_Area_ha":
                cell_area_ha,

            "Green_Cover_Area_ha":
                round(
                    float(
                        green_area_ha
                    ),
                    6
                ),

            "Satellite":
                "Sentinel-2",

            "Product":
                "Sentinel-2 L2A",

            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
                round(
                    float(
                        CLOUD_COVER
                    ),
                    4
                ),

            "Grid_Size_m":
                100

        })


# ============================================================
# 28. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise RuntimeError(
        "Green Cover spatial dataset is empty."
    )


print()
print(
    "Final spatial records:",
    len(df)
)


# ============================================================
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

)


print()
print(
    "Spatial CSV saved:"
)

print(
    SPATIAL_CSV
)


# ============================================================
# 31. SUMMARY CSV
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

    "NDVI_Threshold": [
        NDVI_THRESHOLD
    ],

    "Spatial_Records": [
        len(df)
    ],

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

)


plt.figure(
    figsize=(12, 9)
)


plt.imshow(

    green_map,

    cmap="RdYlGn",

    vmin=0,

    vmax=1

)


plt.colorbar(
    label="Green Cover Fraction"
)


plt.contour(

    GREEN_FRACTION_GRID >= 0.5,

    levels=[0.5],

    linewidths=1.5

)


plt.title(

    "Nagpur Sentinel-2 Green Cover\n"

    f"Scene Date: {SCENE_DATE}\n"

    f"NDVI Threshold: {NDVI_THRESHOLD}"

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
    round(
        CLOUD_COVER,
        2
    ),
    "%"
)

print(
    "NDVI Threshold:",
    NDVI_THRESHOLD
)

print(
    "Spatial Records:",
    len(df)
)

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
    "3. Green Cover PNG:"
)

print(
    PNG_FILE
)

print()

print(
    "Data Source:",
    "Microsoft Planetary Computer"
)

print()
print("=" * 70)
print("GREEN COVER SCRIPT FINISHED SUCCESSFULLY")
print("=" * 70)