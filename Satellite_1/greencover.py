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
# 3. NAGPUR PROCESSING AREA
# ============================================================
# This is a processing/search box.
# It is NOT a political boundary.

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

print()
print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(OUTPUT_DIR)


# ============================================================
# 8. CONNECT TO PLANETARY COMPUTER
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
# 9. SEARCH SENTINEL-2 L2A
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
        "No Sentinel-2 scenes found for Nagpur."
    )


# ============================================================
# 10. SORT BY CLOUD COVER
# ============================================================

items.sort(
    key=lambda item:
        item.properties.get(
            "eo:cloud_cover",
            100
        )
)


# ============================================================
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
    )


# ============================================================
# 12. SELECT BEST SCENE
# ============================================================

item = items[0]

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
print("Selected scene:")
print("Date:", SCENE_DATE)
print("Cloud cover:", CLOUD_COVER, "%")
print("Scene:", SCENE_ID)


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
            f"Sentinel-2 asset not found: {band_name}"
        )


    with rasterio.open(
        asset.href
    ) as src:

        # Convert WGS84 Nagpur box
        # into raster CRS.

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


        data = src.read(
            1,
            window=window
        ).astype(
            np.float32
        )


        cropped_transform = (
            src.window_transform(
                window
            )
        )


        raster_crs = src.crs


        # Sentinel-2 L2A reflectance scaling.

        data = data / 10000.0


        return (
            data,
            cropped_transform,
            raster_crs
        )


# ============================================================
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
)


# ============================================================
# 15. CHECK DIMENSIONS
# ============================================================

print()
print("Band dimensions:")

print("B04:", B04.shape)
print("B08:", B08.shape)


if B04.shape != B08.shape:

    raise RuntimeError(
        "B04 and B08 dimensions do not match."
    )


# ============================================================
# 16. VALID PIXELS
# ============================================================

valid_pixels = (

    np.isfinite(B04)

    & np.isfinite(B08)

    & (B04 >= 0)

    & (B08 >= 0)
)


print()
print(
    "Valid 10m pixels:",
    int(valid_pixels.sum())
)


# ============================================================
# 17. CALCULATE NDVI
# ============================================================

print()
print("Calculating NDVI for green-cover detection...")

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


valid_ndvi_pixels = int(
    np.isfinite(NDVI).sum()
)


print()
print(
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
        2
    ),
    "%"
)


# ============================================================
# 19. AGGREGATE TO APPROX. 100m
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

green_cover_mask = green_cover_mask[
    :new_height,
    :new_width
]


# ============================================================
# 20. BLOCK MEAN FUNCTION
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
# 21. BLOCK GREEN-COVER PERCENTAGE
# ============================================================

def block_green_percentage(
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
        * 100
    )


# ============================================================
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
    "Potential spatial cells:",
    grid_height * grid_width
)


# ============================================================
# 23. CREATE SPATIAL CSV
# ============================================================

print()
print(
    "Creating green-cover spatial records..."
)


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


        green_percentage = (
            GREEN_PERCENT_GRID[
                row,
                col
            ]
        )


        if not np.isfinite(
            ndvi_value
        ):

            continue


        # Center of the 100m cell.

        source_row = (
            row * FACTOR
            + FACTOR // 2
        )


        source_col = (
            col * FACTOR
            + FACTOR // 2
        )


        # Raster row/column
        # -> projected coordinate.

        x, y = xy(

            raster_transform,

            source_row,

            source_col,

            offset="center"
        )


        # Projected CRS -> WGS84.

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

            "NDVI_Mean":
                round(
                    float(
                        ndvi_value
                    ),
                    6
                ),

            "Green_Cover_Percent":
                round(
                    float(
                        green_percentage
                    ),
                    2
                ),

            "Green_Cover_Area_m2":
                round(
                    float(
                        green_area_m2
                    ),
                    2
                ),

            "Green_Cover_Area_ha":
                round(
                    float(
                        green_area_ha
                    ),
                    6
                ),

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

            "Satellite":
                "Sentinel-2",

            "Product":
                "Sentinel-2 L2A",

            "Scene_Date":
                SCENE_DATE,

            "Cloud_Cover_Percent":
                CLOUD_COVER,

            "Grid_Size_m":
                100,

            "Data_Source":
                "Microsoft Planetary Computer Sentinel-2 L2A"
        })


# ============================================================
# 24. DATAFRAME
# ============================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise RuntimeError(
        "Green-cover spatial dataset is empty."
    )


print()
print(
    "Final spatial records:",
    len(df)
)


# ============================================================
# 25. SAVE SPATIAL CSV
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
        GREEN_NDVI_THRESHOLD
    ],

    "Spatial_Records": [
        len(df)
    ],

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
# 27. CREATE PNG
# ============================================================

print()
print(
    "Creating Green Cover PNG..."
)


plt.figure(
    figsize=(12, 9)
)


plt.imshow(

    GREEN_PERCENT_GRID,

    cmap="YlGn",

    vmin=0,

    vmax=100
)


plt.colorbar(
    label="Green Cover (%)"
)


plt.title(
    "Nagpur Sentinel-2 Green Cover\n"
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
# 28. FINAL OUTPUT
# ============================================================

print()
print("=" * 65)
print("              GREEN COVER COMPLETED")
print("=" * 65)

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
    "NDVI threshold:",
    GREEN_NDVI_THRESHOLD
)

print(
    "Spatial records:",
    len(df)
)

print(
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
        2
    ),
    "%"
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
    "3. Green Cover PNG:"
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
print("=" * 65)