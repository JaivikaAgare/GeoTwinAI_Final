# ================================================================
# GeoTwinAI
# NAGPUR URBAN HEATMAP ANALYSIS
#
# SOURCE:
# Landsat 8/9 Collection 2 Level-2
# Microsoft Planetary Computer
#
# THERMAL ASSET:
# lwir11 = Surface Temperature Band
# ================================================================

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pystac_client
import planetary_computer

import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds, transform
from rasterio.transform import xy


# ================================================================
# PROJECT
# ================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_DIR
    / "output"
    / "satellite"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ================================================================
# OUTPUT FILES
# ================================================================

SPATIAL_CSV = (
    OUTPUT_DIR /
    "Nagpur_Heatmap_Spatial.csv"
)

SUMMARY_CSV = (
    OUTPUT_DIR /
    "Nagpur_Heatmap_Summary.csv"
)

PNG_FILE = (
    OUTPUT_DIR /
    "Nagpur_Heatmap.png"
)


# ================================================================
# NAGPUR BOUNDING BOX
# ================================================================

MIN_LON = 78.95
MIN_LAT = 21.05

MAX_LON = 79.20
MAX_LAT = 21.25


# ================================================================
# SEARCH SETTINGS
# ================================================================

COLLECTION = "landsat-c2-l2"

START_DATE = "2025-01-01"

END_DATE = datetime.now().strftime(
    "%Y-%m-%d"
)

MAX_CLOUD = 40


# ================================================================
# HEADER
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
print("Nagpur BBOX:")
print(
    MIN_LON,
    MIN_LAT,
    MAX_LON,
    MAX_LAT
)


# ================================================================
# CONNECT
# ================================================================

print()
print(
    "Connecting to Microsoft Planetary Computer..."
)

try:

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

except Exception as e:

    raise SystemExit(
        f"\nPlanetary Computer connection failed:\n{e}"
    )

print(
    "Connection successful."
)


# ================================================================
# SEARCH LANDSAT
# ================================================================

print()
print(
    "Searching Landsat thermal scenes..."
)

try:

    search = catalog.search(

        collections=[
            COLLECTION
        ],

        bbox=[
            MIN_LON,
            MIN_LAT,
            MAX_LON,
            MAX_LAT
        ],

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
# FIND LWIR11
# ================================================================

print()
print(
    "Searching for Landsat Surface Temperature asset..."
)


thermal_items = []


for item in items:

    if "lwir11" in item.assets:

        thermal_items.append(
            item
        )


print(
    "Scenes with lwir11:",
    len(thermal_items)
)


if not thermal_items:

    raise SystemExit(
        "\nNo lwir11 Surface Temperature asset found."
    )


# ================================================================
# SORT
# ================================================================

thermal_items.sort(
    key=lambda item: item.datetime
)


# ================================================================
# SHOW LATEST SCENES
# ================================================================

print()
print(
    "Latest Landsat thermal scenes:"
)


for item in thermal_items[-10:]:

    cloud = item.properties.get(
        "eo:cloud_cover",
        np.nan
    )

    print(
        item.datetime.strftime(
            "%Y-%m-%d"
        ),
        "| Cloud:",
        round(
            float(cloud),
            2
        ),
        "%",
        "|",
        item.id
    )


# ================================================================
# SELECT LATEST
# ================================================================

selected_item = thermal_items[-1]

selected_date = (
    selected_item.datetime.date()
)

cloud_cover = selected_item.properties.get(
    "eo:cloud_cover",
    np.nan
)


# ================================================================
# ASSET
# ================================================================

thermal_asset = (
    selected_item.assets[
        "lwir11"
    ]
)


print()
print("=" * 70)
print(
    "                 SELECTED LANDSAT SCENE"
)
print("=" * 70)

print()
print(
    "Date:",
    selected_date
)

print(
    "Cloud cover:",
    round(
        float(cloud_cover),
        2
    ),
    "%"
)

print(
    "Scene:",
    selected_item.id
)

print(
    "Thermal asset: lwir11"
)


# ================================================================
# READ SCALE/OFFSET FROM STAC
# ================================================================

print()
print(
    "Reading thermal scale and offset..."
)


try:

    raster_band_info = (
        thermal_asset.extra_fields
        .get(
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

    # Landsat Collection 2 Level-2
    # Surface Temperature standard values

    scale = 0.00341802

    offset = 149.0


print(
    "Scale:",
    scale
)

print(
    "Offset:",
    offset
)


# ================================================================
# READ THERMAL DATA
# ================================================================

print()
print(
    "Opening Landsat thermal asset..."
)


try:

    with rasterio.open(
        thermal_asset.href
    ) as src:

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
        # Convert Nagpur geographic BBOX
        # to raster CRS
        # --------------------------------------------------------

        left, bottom, right, top = (
            transform_bounds(

                "EPSG:4326",

                src.crs,

                MIN_LON,
                MIN_LAT,
                MAX_LON,
                MAX_LAT,

                densify_pts=21

            )
        )


        # --------------------------------------------------------
        # Create raster window
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


        print()
        print(
            "Reading Nagpur thermal window..."
        )


        raw_data = src.read(

            1,

            window=window,

            masked=True

        )


        output_transform = (
            src.window_transform(
                window
            )
        )


        output_crs = src.crs

        nodata_value = src.nodata


except Exception as e:

    raise SystemExit(
        f"\nFailed reading thermal data:\n{e}"
    )


# ================================================================
# RAW DATA
# ================================================================

raw_data = raw_data.astype(
    "float32"
)


raw_values = raw_data.filled(
    np.nan
)


# ================================================================
# REMOVE FILL VALUE
# ================================================================

if nodata_value is not None:

    raw_values[
        raw_values == nodata_value
    ] = np.nan


raw_values[
    raw_values <= 0
] = np.nan


# ================================================================
# CONVERT DN -> KELVIN
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
# KELVIN -> CELSIUS
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
# VALID TEMPERATURES
# ================================================================

valid = (

    np.isfinite(
        temperature_celsius
    )

    &

    (
        temperature_celsius
        >=
        -20
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
# STATISTICS
# ================================================================

values = (
    temperature_celsius[
        valid
    ]
)


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
print(
    "Temperature statistics:"
)

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
# SPATIAL RECORDS
# ================================================================

print()
print(
    "Creating spatial thermal records..."
)


height, width = (
    temperature_celsius.shape
)


records = []


for row in range(
    height
):

    for col in range(
        width
    ):

        if not valid[
            row,
            col
        ]:

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

            heat_class = (
                "Very Hot"
            )

        elif temperature >= 35:

            heat_class = (
                "Hot"
            )

        elif temperature >= 30:

            heat_class = (
                "Warm"
            )

        else:

            heat_class = (
                "Normal"
            )


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
        # CONVERT TO LAT/LON
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
                str(
                    selected_date
                ),

            "Cloud_Cover_Percent":
                round(
                    float(cloud_cover),
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
# DATAFRAME
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
# SAVE SPATIAL CSV
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
# HEAT COUNTS
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


total_cells = len(
    df
)


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
# SUMMARY
# ================================================================

summary_df = pd.DataFrame([{

    "Region":
        "Nagpur",

    "Date":
        str(
            selected_date
        ),

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
            float(cloud_cover),
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
# HEATMAP PNG
# ================================================================

print()
print(
    "Creating heatmap PNG..."
)


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

    f"Landsat Surface Temperature | "
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


# ================================================================
# FINAL
# ================================================================

print()
print("=" * 70)
print(
    "             HEATMAP ANALYSIS COMPLETE"
)
print("=" * 70)

print()
print(
    "Selected date:",
    selected_date
)

print(
    "Cloud cover:",
    round(
        float(cloud_cover),
        2
    ),
    "%"
)

print()
print(
    "Thermal pixels:",
    valid_count
)

print(
    "Spatial records:",
    total_cells
)

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

print()
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
    "Heatmap PNG:"
)

print(
    PNG_FILE
)

print()
print(
    "Source:"
)

print(
    "Landsat 8/9 Collection 2 Level-2"
)

print(
    "Microsoft Planetary Computer"
)

print("=" * 70)