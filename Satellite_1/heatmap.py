# ================================================================
# GeoTwinAI
# NAGPUR URBAN HEATMAP ANALYSIS
#
# SOURCE:
# Landsat 8/9 Collection 2 Level-2
# Microsoft Planetary Computer
#
# THERMAL ASSET:
# lwir11
#
# FEATURES:
# - Automatically searches up to today's date
# - Automatically selects latest available scene
# - Uses Nagpur BBOX
# - Reads thermal data safely using raster window
# - Converts DN -> Kelvin -> Celsius
# - Creates spatial CSV
# - Creates summary CSV
# - Creates heatmap PNG
# - CSV + PNG use SAME selected scene/date
# - No Google Earth Engine
# ================================================================

from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pystac_client
import planetary_computer

import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.warp import transform_bounds, transform
from rasterio.transform import xy


# ================================================================
# 1. PROJECT PATHS
# ================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_DIR / "output" / "satellite"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ================================================================
# 2. OUTPUT FILES
# ================================================================

SPATIAL_CSV = OUTPUT_DIR / "Nagpur_Heatmap_Spatial.csv"

SUMMARY_CSV = OUTPUT_DIR / "Nagpur_Heatmap_Summary.csv"

PNG_FILE = OUTPUT_DIR / "Nagpur_Heatmap.png"


# ================================================================
# 3. NAGPUR BOUNDING BOX
# ================================================================

MIN_LON = 78.95
MIN_LAT = 21.05

MAX_LON = 79.20
MAX_LAT = 21.25

BBOX = [
    MIN_LON,
    MIN_LAT,
    MAX_LON,
    MAX_LAT
]


# ================================================================
# 4. SEARCH SETTINGS
# ================================================================

COLLECTION = "landsat-c2-l2"

START_DATE = "2025-01-01T00:00:00Z"

END_DATE = datetime.now(
    timezone.utc
).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)

MAX_CLOUD = 40.0


# ================================================================
# 5. HEADER
# ================================================================

print()
print("=" * 70)
print("             NAGPUR URBAN HEATMAP ANALYSIS")
print("             LANDSAT 8/9 THERMAL DATA")
print("             MICROSOFT PLANETARY COMPUTER")
print("=" * 70)

print()
print("Project:")
print(PROJECT_DIR)

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
print(MAX_CLOUD, "%")

print()
print("Nagpur BBOX:")
print(
    MIN_LON,
    MIN_LAT,
    MAX_LON,
    MAX_LAT
)


# ================================================================
# 6. CONNECT TO PLANETARY COMPUTER
# ================================================================

print()
print("=" * 70)
print("CONNECTING TO PLANETARY COMPUTER")
print("=" * 70)

try:

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

except Exception as e:

    raise SystemExit(
        f"\nPlanetary Computer connection failed:\n{e}"
    )


print()
print("Connection successful.")


# ================================================================
# 7. SEARCH LANDSAT SCENES
# ================================================================

print()
print("=" * 70)
print("SEARCHING LANDSAT THERMAL SCENES")
print("=" * 70)

try:

    search = catalog.search(

        collections=[
            COLLECTION
        ],

        bbox=BBOX,

        datetime=(
            f"{START_DATE}/"
            f"{END_DATE}"
        ),

        query={
            "eo:cloud_cover": {
                "lt": MAX_CLOUD
            }
        }
    )

    items = list(
        search.item_collection()
    )

except Exception as e:

    raise SystemExit(
        f"\nLandsat search failed:\n{e}"
    )


print()
print(
    "Landsat scenes found:",
    len(items)
)


if not items:

    raise SystemExit(
        "\nNo Landsat scenes found."
    )


# ================================================================
# 8. KEEP ONLY SCENES WITH LWIR11
# ================================================================

print()
print("=" * 70)
print("CHECKING THERMAL ASSET")
print("=" * 70)

thermal_items = []

for item in items:

    if "lwir11" in item.assets:

        thermal_items.append(
            item
        )


print()
print(
    "Scenes with lwir11:",
    len(thermal_items)
)


if not thermal_items:

    raise SystemExit(
        "\nNo lwir11 thermal asset found."
    )


# ================================================================
# 9. CLOUD COVER FUNCTION
# ================================================================

def get_cloud_cover(item):

    value = item.properties.get(
        "eo:cloud_cover",
        999
    )

    try:

        return float(value)

    except Exception:

        return 999.0


# ================================================================
# 10. SORT NEWEST FIRST
# ================================================================

thermal_items = sorted(

    thermal_items,

    key=lambda item: (
        item.datetime
        if item.datetime is not None
        else datetime.min.replace(
            tzinfo=timezone.utc
        )
    ),

    reverse=True
)


# ================================================================
# 11. SHOW LATEST 15 SCENES
# ================================================================

print()
print("=" * 70)
print("LATEST AVAILABLE LANDSAT THERMAL SCENES")
print("=" * 70)

for index, item in enumerate(
    thermal_items[:15],
    start=1
):

    if item.datetime:

        date_text = item.datetime.strftime(
            "%Y-%m-%d"
        )

    else:

        date_text = "Unknown"

    cloud = get_cloud_cover(
        item
    )

    print(
        f"{index:02d}. "
        f"{date_text} | "
        f"Cloud: {cloud:.2f}% | "
        f"{item.id}"
    )


# ================================================================
# 12. SELECT LATEST SCENE
# ================================================================

selected_item = thermal_items[0]


if selected_item.datetime is None:

    raise SystemExit(
        "\nSelected scene has no acquisition date."
    )


selected_date = selected_item.datetime.strftime(
    "%Y-%m-%d"
)

cloud_cover = get_cloud_cover(
    selected_item
)

scene_id = selected_item.id


# ================================================================
# 13. SELECTED SCENE
# ================================================================

print()
print("=" * 70)
print("                 SELECTED LANDSAT SCENE")
print("=" * 70)

print()
print("Date:")
print(selected_date)

print()
print("Cloud cover:")
print(
    round(
        cloud_cover,
        2
    ),
    "%"
)

print()
print("Scene:")
print(scene_id)

print()
print("IMPORTANT:")
print(
    "All CSV files and PNG use this SAME scene."
)


# ================================================================
# 14. THERMAL ASSET
# ================================================================

thermal_asset = selected_item.assets.get(
    "lwir11"
)

if thermal_asset is None:

    raise SystemExit(
        "\nSelected scene does not contain lwir11."
    )


print()
print("Thermal asset:")
print("lwir11")


# ================================================================
# 15. READ SCALE AND OFFSET
# ================================================================

print()
print("=" * 70)
print("READING THERMAL SCALE AND OFFSET")
print("=" * 70)

try:

    raster_band_info = (
        thermal_asset.extra_fields.get(
            "raster:bands",
            []
        )
    )

except Exception:

    raster_band_info = []


if raster_band_info:

    scale = float(
        raster_band_info[0].get(
            "scale",
            0.00341802
        )
    )

    offset = float(
        raster_band_info[0].get(
            "offset",
            149.0
        )
    )

else:

    scale = 0.00341802
    offset = 149.0


print()
print("Scale:")
print(scale)

print()
print("Offset:")
print(offset)


# ================================================================
# 16. READ THERMAL RASTER
# ================================================================

print()
print("=" * 70)
print("READING LANDSAT THERMAL DATA")
print("=" * 70)

try:

    with rasterio.open(
        thermal_asset.href
    ) as src:

        print()
        print(
            "Raster CRS:",
            src.crs
        )

        print(
            "Raster dimensions:",
            src.width,
            "x",
            src.height
        )

        if src.crs is None:

            raise RuntimeError(
                "Thermal raster CRS is missing."
            )

        # --------------------------------------------------------
        # TRANSFORM NAGPUR BBOX TO RASTER CRS
        # --------------------------------------------------------

        left, bottom, right, top = transform_bounds(

            "EPSG:4326",

            src.crs,

            MIN_LON,
            MIN_LAT,
            MAX_LON,
            MAX_LAT,

            densify_pts=21
        )

        # --------------------------------------------------------
        # CREATE WINDOW
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # KEEP WINDOW INSIDE RASTER
        # --------------------------------------------------------

        full_window = Window(
            0,
            0,
            src.width,
            src.height
        )

        window = window.intersection(
            full_window
        )

        if (
            window.width <= 0
            or
            window.height <= 0
        ):

            raise RuntimeError(
                "Nagpur BBOX does not overlap Landsat raster."
            )

        print()
        print(
            "Reading Nagpur thermal window:"
        )

        print(
            int(window.width),
            "x",
            int(window.height)
        )

        # --------------------------------------------------------
        # READ DATA
        # --------------------------------------------------------

        raw_data = src.read(
            1,
            window=window,
            masked=True
        )

        output_transform = src.window_transform(
            window
        )

        output_crs = src.crs

        nodata_value = src.nodata

except Exception as e:

    raise SystemExit(
        f"\nFailed reading thermal data:\n{e}"
    )


# ================================================================
# 17. RAW DATA -> FLOAT
# ================================================================

raw_values = raw_data.astype(
    "float32"
).filled(
    np.nan
)


# ================================================================
# 18. REMOVE NODATA
# ================================================================

if nodata_value is not None:

    raw_values[
        raw_values == nodata_value
    ] = np.nan


raw_values[
    raw_values <= 0
] = np.nan


# ================================================================
# 19. DN -> KELVIN
# ================================================================

print()
print(
    "Converting thermal DN to Kelvin..."
)

temperature_kelvin = (
    raw_values
    *
    scale
    +
    offset
)


# ================================================================
# 20. KELVIN -> CELSIUS
# ================================================================

print(
    "Converting Kelvin to Celsius..."
)

temperature_celsius = (
    temperature_kelvin
    -
    273.15
)


# ================================================================
# 21. VALID TEMPERATURE MASK
# ================================================================

# Remove unrealistic temperatures.
# This also prevents invalid nodata values
# from entering the statistics.

valid = (

    np.isfinite(
        temperature_celsius
    )

    &

    (
        temperature_celsius
        >=
        0
    )

    &

    (
        temperature_celsius
        <=
        70
    )
)


valid_count = int(
    valid.sum()
)


print()
print(
    "Valid thermal pixels:",
    valid_count
)


if valid_count == 0:

    raise SystemExit(
        "\nNo valid thermal pixels found."
    )


# ================================================================
# 22. TEMPERATURE STATISTICS
# ================================================================

values = temperature_celsius[
    valid
]


minimum_temperature = float(
    np.min(values)
)

maximum_temperature = float(
    np.max(values)
)

mean_temperature = float(
    np.mean(values)
)

median_temperature = float(
    np.median(values)
)


print()
print("=" * 70)
print("TEMPERATURE STATISTICS")
print("=" * 70)

print()
print(
    "Minimum:",
    round(
        minimum_temperature,
        2
    ),
    "°C"
)

print(
    "Maximum:",
    round(
        maximum_temperature,
        2
    ),
    "°C"
)

print(
    "Mean:",
    round(
        mean_temperature,
        2
    ),
    "°C"
)

print(
    "Median:",
    round(
        median_temperature,
        2
    ),
    "°C"
)


# ================================================================
# 23. CREATE SPATIAL RECORDS
# ================================================================

print()
print("=" * 70)
print("CREATING SPATIAL THERMAL RECORDS")
print("=" * 70)


height, width = temperature_celsius.shape


records = []


# ================================================================
# 24. SPATIAL RECORD LOOP
# ================================================================

for row in range(height):

    for col in range(width):

        if not valid[row, col]:

            continue

        temperature = float(
            temperature_celsius[
                row,
                col
            ]
        )

        # --------------------------------------------------------
        # HEAT CLASS
        # --------------------------------------------------------

        if temperature >= 40:

            heat_class = "Very Hot"

        elif temperature >= 35:

            heat_class = "Hot"

        elif temperature >= 30:

            heat_class = "Warm"

        else:

            heat_class = "Normal"

        # --------------------------------------------------------
        # PIXEL CENTER
        # --------------------------------------------------------

        x, y = xy(

            output_transform,

            row,

            col,

            offset="center"
        )

        # --------------------------------------------------------
        # PROJECTED -> LAT/LON
        # --------------------------------------------------------

        longitude, latitude = transform(

            output_crs,

            "EPSG:4326",

            [x],
            [y]
        )

        records.append({

            "Region":
                "Nagpur",

            "Latitude":
                round(
                    float(latitude[0]),
                    6
                ),

            "Longitude":
                round(
                    float(longitude[0]),
                    6
                ),

            "Land_Surface_Temperature_C":
                round(
                    temperature,
                    2
                ),

            "Heat_Class":
                heat_class,

            "Date":
                selected_date,

            "Cloud_Cover_Percent":
                round(
                    cloud_cover,
                    2
                ),

            "Satellite":
                "Landsat 8/9",

            "Product":
                "Landsat Collection 2 Level-2",

            "Thermal_Band":
                "lwir11",

            "Source":
                "Microsoft Planetary Computer",

            "Spatial_Resolution_m":
                100

        })


# ================================================================
# 25. DATAFRAME
# ================================================================

df = pd.DataFrame(
    records
)


if df.empty:

    raise SystemExit(
        "\nNo spatial thermal records created."
    )


print()
print(
    "Spatial records:",
    len(df)
)


# ================================================================
# 26. SAVE SPATIAL CSV
# ================================================================

df.to_csv(
    SPATIAL_CSV,
    index=False
)


print()
print(
    "Spatial CSV created:"
)

print(
    SPATIAL_CSV
)


# ================================================================
# 27. HEAT CLASS COUNTS
# ================================================================

normal_count = int(
    (
        df["Heat_Class"]
        ==
        "Normal"
    ).sum()
)

warm_count = int(
    (
        df["Heat_Class"]
        ==
        "Warm"
    ).sum()
)

hot_count = int(
    (
        df["Heat_Class"]
        ==
        "Hot"
    ).sum()
)

very_hot_count = int(
    (
        df["Heat_Class"]
        ==
        "Very Hot"
    ).sum()
)


total_cells = len(df)


# ================================================================
# 28. HOT + VERY HOT PERCENTAGE
# ================================================================

hot_percentage = (

    (
        hot_count
        +
        very_hot_count
    )

    /

    total_cells

    *

    100
)


# ================================================================
# 29. SUMMARY DATASET
# ================================================================

summary_df = pd.DataFrame([{

    "Region":
        "Nagpur",

    "Date":
        selected_date,

    "Total_Thermal_Cells":
        total_cells,

    "Minimum_Temperature_C":
        round(
            minimum_temperature,
            2
        ),

    "Maximum_Temperature_C":
        round(
            maximum_temperature,
            2
        ),

    "Mean_Temperature_C":
        round(
            mean_temperature,
            2
        ),

    "Median_Temperature_C":
        round(
            median_temperature,
            2
        ),

    "Normal_Cells":
        normal_count,

    "Warm_Cells":
        warm_count,

    "Hot_Cells":
        hot_count,

    "Very_Hot_Cells":
        very_hot_count,

    "Hot_VeryHot_Percentage":
        round(
            hot_percentage,
            2
        ),

    "Cloud_Cover_Percent":
        round(
            cloud_cover,
            2
        ),

    "Satellite":
        "Landsat 8/9",

    "Product":
        "Landsat Collection 2 Level-2",

    "Thermal_Band":
        "lwir11",

    "Source":
        "Microsoft Planetary Computer",

    "Scale":
        scale,

    "Offset":
        offset

}])


# ================================================================
# 30. SAVE SUMMARY
# ================================================================

summary_df.to_csv(
    SUMMARY_CSV,
    index=False
)


print()
print(
    "Summary CSV created:"
)

print(
    SUMMARY_CSV
)


# ================================================================
# 31. CREATE HEATMAP PNG
# ================================================================

print()
print("=" * 70)
print("CREATING HEATMAP PNG")
print("=" * 70)


plt.figure(
    figsize=(12, 9)
)


scatter = plt.scatter(

    df["Longitude"],

    df["Latitude"],

    c=df[
        "Land_Surface_Temperature_C"
    ],

    cmap="hot",

    s=8,

    alpha=0.85
)


plt.colorbar(

    scatter,

    label="Land Surface Temperature (°C)"
)


plt.xlabel(
    "Longitude"
)

plt.ylabel(
    "Latitude"
)


plt.title(

    "Nagpur Urban Heatmap\n"

    "Landsat Surface Temperature | "

    f"{selected_date}"
)


plt.grid(
    alpha=0.25
)


plt.tight_layout()


plt.savefig(

    PNG_FILE,

    dpi=200,

    bbox_inches="tight"
)


plt.close()


print()
print(
    "Heatmap PNG created:"
)

print(
    PNG_FILE
)


# ================================================================
# 32. FINAL REPORT
# ================================================================

print()
print("=" * 70)
print("             HEATMAP ANALYSIS COMPLETE")
print("=" * 70)

print()
print("Selected date:")
print(selected_date)

print()
print("Cloud cover:")
print(
    round(
        cloud_cover,
        2
    ),
    "%"
)

print()
print("Satellite:")
print("Landsat 8/9")

print()
print("Thermal pixels:")
print(valid_count)

print()
print("Spatial records:")
print(total_cells)

print()
print(
    "Minimum temperature:",
    round(
        minimum_temperature,
        2
    ),
    "°C"
)

print(
    "Maximum temperature:",
    round(
        maximum_temperature,
        2
    ),
    "°C"
)

print(
    "Mean temperature:",
    round(
        mean_temperature,
        2
    ),
    "°C"
)

print(
    "Median temperature:",
    round(
        median_temperature,
        2
    ),
    "°C"
)

print()
print("HEAT CLASS COUNTS")

print(
    "Normal:",
    normal_count
)

print(
    "Warm:",
    warm_count
)

print(
    "Hot:",
    hot_count
)

print(
    "Very Hot:",
    very_hot_count
)

print()
print(
    "Hot + Very Hot Percentage:",
    round(
        hot_percentage,
        2
    ),
    "%"
)


# ================================================================
# 33. FILES CREATED
# ================================================================

print()
print("=" * 70)
print("FILES CREATED")
print("=" * 70)

print()
print("1. Spatial CSV:")
print(
    SPATIAL_CSV
)

print()
print("2. Summary CSV:")
print(
    SUMMARY_CSV
)

print()
print("3. Heatmap PNG:")
print(
    PNG_FILE
)


# ================================================================
# 34. IMPORTANT
# ================================================================

print()
print("=" * 70)
print("IMPORTANT")
print("=" * 70)

print()

print(
    "CSV and PNG date:",
    selected_date
)

print(
    "All outputs use the same selected Landsat scene."
)

print(
    "Running this script again searches up to today's date."
)

print(
    "If a newer scene becomes available, "
    "the latest scene will automatically be selected."
)

print()

print(
    "Google Earth Engine: NOT USED"
)

print(
    "Source: Microsoft Planetary Computer"
)


# ================================================================
# 35. SUCCESS
# ================================================================

print()
print("=" * 70)
print("                    SUCCESS")
print("=" * 70)