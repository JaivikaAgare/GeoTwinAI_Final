# ================================================================
# GeoTwinAI
# NAGPUR FLOOD RISK / INUNDATION ANALYSIS
#
# SOURCE:
# Sentinel-1 GRD
# Microsoft Planetary Computer
#
# METHOD:
# Before/After SAR change detection
#
# OUTPUT:
# Nagpur_FloodRisk_Spatial.csv
# Nagpur_FloodRisk_Summary.csv
# Nagpur_FloodRisk.png
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
from rasterio.vrt import WarpedVRT
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import xy
from rasterio.warp import transform


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
    OUTPUT_DIR
    / "Nagpur_FloodRisk_Spatial.csv"
)

SUMMARY_CSV = (
    OUTPUT_DIR
    / "Nagpur_FloodRisk_Summary.csv"
)

PNG_FILE = (
    OUTPUT_DIR
    / "Nagpur_FloodRisk.png"
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

COLLECTION = "sentinel-1-grd"

START_DATE = "2025-01-01"

END_DATE = datetime.now().strftime(
    "%Y-%m-%d"
)


# ================================================================
# TARGET OUTPUT RESOLUTION
#
# About 100 m spatial cells
# ================================================================

OUTPUT_RESOLUTION = 0.001


# ================================================================
# HEADER
# ================================================================

print()
print("=" * 70)
print("             NAGPUR FLOOD RISK ANALYSIS")
print("             SENTINEL-1 SAR")
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
print("Connecting to Microsoft Planetary Computer...")

try:

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

except Exception as e:

    raise SystemExit(
        f"\nPlanetary Computer connection failed:\n{e}"
    )


print("Connection successful.")


# ================================================================
# SEARCH SENTINEL-1
# ================================================================

print()
print("Searching Sentinel-1 GRD scenes...")

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
        )
    )

    items = list(
        search.item_collection()
    )

except Exception as e:

    raise SystemExit(
        f"\nSentinel-1 search failed:\n{e}"
    )


print()
print(
    "Total Sentinel-1 scenes found:",
    len(items)
)


# ================================================================
# FILTER VV + VH
# ================================================================

valid_items = []

for item in items:

    assets = set(
        item.assets.keys()
    )

    if (
        "vv" in assets
        and
        "vh" in assets
    ):

        valid_items.append(item)


print(
    "Scenes with VV + VH:",
    len(valid_items)
)


if len(valid_items) < 2:

    raise SystemExit(
        "\nNot enough Sentinel-1 VV/VH scenes."
    )


# ================================================================
# SORT
# ================================================================

valid_items.sort(
    key=lambda item: item.datetime
)


# ================================================================
# PRINT LATEST 10
# ================================================================

print()
print("Latest Sentinel-1 scenes:")

for item in valid_items[-10:]:

    print(
        item.datetime.strftime(
            "%Y-%m-%d"
        ),
        "|",
        item.id
    )


# ================================================================
# ONE SCENE PER DATE
# ================================================================

daily_items = {}

for item in valid_items:

    date = item.datetime.date()

    if date not in daily_items:

        daily_items[date] = item


unique_items = list(
    daily_items.values()
)


unique_items.sort(
    key=lambda item: item.datetime
)


print()
print(
    "Unique acquisition dates:",
    len(unique_items)
)


if len(unique_items) < 2:

    raise SystemExit(
        "\nLess than two different acquisition dates."
    )


# ================================================================
# SELECT BEFORE AND AFTER
# ================================================================

after_item = unique_items[-1]

before_item = unique_items[-2]


before_date = (
    before_item.datetime.date()
)

after_date = (
    after_item.datetime.date()
)


# ================================================================
# SELECTED SCENES
# ================================================================

print()
print("=" * 70)
print("                 SELECTED SCENES")
print("=" * 70)

print()
print("BEFORE DATE:")
print(before_date)

print()
print("BEFORE SCENE:")
print(before_item.id)

print()
print("AFTER DATE:")
print(after_date)

print()
print("AFTER SCENE:")
print(after_item.id)


# ================================================================
# GET CRS FROM STAC ITEM
# ================================================================

def get_item_crs(item):

    properties = item.properties

    print()
    print("Checking STAC projection metadata...")

    # ------------------------------------------------------------
    # proj:epsg
    # ------------------------------------------------------------

    epsg = properties.get(
        "proj:epsg"
    )

    if epsg is not None:

        print(
            "STAC proj:epsg:",
            epsg
        )

        return CRS.from_epsg(
            int(epsg)
        )

    # ------------------------------------------------------------
    # proj:code
    # ------------------------------------------------------------

    proj_code = properties.get(
        "proj:code"
    )

    if proj_code:

        print(
            "STAC proj:code:",
            proj_code
        )

        try:

            return CRS.from_user_input(
                proj_code
            )

        except Exception:

            pass

    # ------------------------------------------------------------
    # proj:wkt2
    # ------------------------------------------------------------

    proj_wkt = properties.get(
        "proj:wkt2"
    )

    if proj_wkt:

        print(
            "STAC projection WKT found."
        )

        return CRS.from_wkt(
            proj_wkt
        )

    return None


# ================================================================
# FALLBACK SENTINEL-1 CRS
#
# Sentinel-1 scenes over Nagpur are normally UTM zone 44N.
# EPSG:32644 = WGS84 / UTM zone 44N
# ================================================================

def get_safe_crs(
    item
):

    crs = get_item_crs(
        item
    )

    if crs is not None:

        return crs

    print(
        "STAC CRS metadata unavailable."
    )

    print(
        "Using Sentinel-1 Nagpur UTM fallback:"
    )

    print(
        "EPSG:32644"
    )

    return CRS.from_epsg(
        32644
    )


# ================================================================
# READ SENTINEL-1 AS EPSG:4326
#
# This is the important fix.
#
# We do NOT depend on src.crs.
# We obtain CRS from STAC metadata/fallback and then use
# WarpedVRT to safely crop Nagpur.
# ================================================================

def read_sentinel_band(
    item,
    asset_name
):

    print()
    print(
        f"Reading {asset_name.upper()}..."
    )

    asset = item.assets.get(
        asset_name
    )

    if asset is None:

        raise RuntimeError(
            f"{asset_name.upper()} asset not found."
        )


    source_crs = get_safe_crs(
        item
    )


    print(
        "Using source CRS:",
        source_crs
    )


    print(
        "Opening Sentinel-1 asset..."
    )


    try:

        with rasterio.open(
            asset.href
        ) as src:

            print(
                "Raster dimensions:",
                src.width,
                "x",
                src.height
            )

            print(
                "Raster reported CRS:",
                src.crs
            )


            # ----------------------------------------------------
            # WarpedVRT
            #
            # We explicitly provide source CRS.
            # Output is always EPSG:4326.
            # ----------------------------------------------------

            with WarpedVRT(

                src,

                src_crs=source_crs,

                crs="EPSG:4326",

                resampling=Resampling.bilinear,

                resolution=OUTPUT_RESOLUTION,

                transform=None

            ) as vrt:

                print(
                    "VRT CRS:",
                    vrt.crs
                )

                # ------------------------------------------------
                # Calculate window for Nagpur
                # ------------------------------------------------

                window = from_bounds(

                    MIN_LON,
                    MIN_LAT,
                    MAX_LON,
                    MAX_LAT,

                    transform=vrt.transform
                )


                window = (
                    window
                    .round_offsets()
                    .round_lengths()
                )


                # ------------------------------------------------
                # Read
                # ------------------------------------------------

                data = vrt.read(

                    1,

                    window=window,

                    masked=True
                )


                output_transform = (
                    vrt.window_transform(
                        window
                    )
                )


                output_crs = vrt.crs


                # ------------------------------------------------
                # Convert masked array
                # ------------------------------------------------

                data = data.astype(
                    "float32"
                )


                data = data.filled(
                    np.nan
                )


                print(
                    "Output shape:",
                    data.shape
                )


                valid_count = int(
                    np.isfinite(
                        data
                    ).sum()
                )


                print(
                    "Valid pixels:",
                    valid_count
                )


                if valid_count == 0:

                    raise RuntimeError(
                        f"No valid pixels returned for "
                        f"{asset_name.upper()}."
                    )


                return (
                    data,
                    output_transform,
                    output_crs
                )


    except Exception as e:

        raise RuntimeError(
            f"\nFailed reading "
            f"{asset_name.upper()}:\n{e}"
        )


# ================================================================
# READ BEFORE VV
# ================================================================

before_vv, before_transform, before_crs = (
    read_sentinel_band(
        before_item,
        "vv"
    )
)


# ================================================================
# READ BEFORE VH
# ================================================================

before_vh, _, _ = (
    read_sentinel_band(
        before_item,
        "vh"
    )
)


# ================================================================
# READ AFTER VV
# ================================================================

after_vv, after_transform, after_crs = (
    read_sentinel_band(
        after_item,
        "vv"
    )
)


# ================================================================
# READ AFTER VH
# ================================================================

after_vh, _, _ = (
    read_sentinel_band(
        after_item,
        "vh"
    )
)


# ================================================================
# CHECK SHAPES
# ================================================================

print()
print("Checking raster dimensions...")


if before_vv.shape != before_vh.shape:

    raise SystemExit(
        "Before VV/VH dimensions do not match."
    )


if after_vv.shape != after_vh.shape:

    raise SystemExit(
        "After VV/VH dimensions do not match."
    )


if before_vv.shape != after_vv.shape:

    raise SystemExit(
        "Before and After dimensions do not match."
    )


print(
    "Raster dimensions OK:",
    before_vv.shape
)


# ================================================================
# CONVERT TO dB
# ================================================================

def to_db(
    array
):

    result = np.full(
        array.shape,
        np.nan,
        dtype="float32"
    )


    valid = (

        np.isfinite(
            array
        )

        &

        (array > 0)

    )


    result[valid] = (

        10.0

        *

        np.log10(
            array[valid]
        )

    )


    return result


print()
print("Converting SAR values to dB...")


before_vv_db = to_db(
    before_vv
)

before_vh_db = to_db(
    before_vh
)

after_vv_db = to_db(
    after_vv
)

after_vh_db = to_db(
    after_vh
)


# ================================================================
# VALID PIXELS
# ================================================================

valid = (

    np.isfinite(
        before_vv_db
    )

    &

    np.isfinite(
        before_vh_db
    )

    &

    np.isfinite(
        after_vv_db
    )

    &

    np.isfinite(
        after_vh_db
)


)


valid_count = int(
    valid.sum()
)


print()
print(
    "Valid comparison pixels:",
    valid_count
)


if valid_count == 0:

    raise SystemExit(
        "\nNo valid comparison pixels."
    )


# ================================================================
# SAR CHANGE
# ================================================================

print()
print("Calculating Sentinel-1 SAR change...")


vv_change = (
    after_vv_db
    -
    before_vv_db
)


vh_change = (
    after_vh_db
    -
    before_vh_db
)


# ================================================================
# FLOOD RISK SCORE
#
# Negative SAR change can indicate newly inundated/open-water
# surfaces. This is an indicator, not an official flood forecast.
# ================================================================

score = np.zeros(
    vv_change.shape,
    dtype="float32"
)


# VV
score[
    valid &
    (vv_change <= -3.0)
] += 40


score[
    valid &
    (vv_change <= -5.0)
] += 20


# VH
score[
    valid &
    (vh_change <= -2.0)
] += 30


score[
    valid &
    (vh_change <= -4.0)
] += 10


score = np.clip(
    score,
    0,
    100
)


# ================================================================
# CLASSIFICATION
# ================================================================

risk_class = np.full(
    score.shape,
    "Low",
    dtype=object
)


risk_class[
    score >= 40
] = "Moderate"


risk_class[
    score >= 70
] = "High"


risk_class[
    score >= 90
] = "Very High"


# ================================================================
# SPATIAL AGGREGATION
#
# The Sentinel-1 raster is converted into approximately
# 100 m cells for Power BI.
# ================================================================

print()
print(
    "Aggregating SAR pixels into approximately 100 m cells..."
)


height, width = score.shape


# Determine aggregation size from raster dimensions
# Approximately 10x10 pixels

factor = 10


grid_rows = (
    height // factor
)

grid_cols = (
    width // factor
)


print()
print(
    "Spatial grid:",
    grid_cols,
    "x",
    grid_rows
)


# ================================================================
# COORDINATE CONVERSION
# ================================================================

def pixel_to_lonlat(
    row,
    col
):

    x, y = xy(

        before_transform,

        row,

        col,

        offset="center"

    )


    lon, lat = transform(

        before_crs,

        "EPSG:4326",

        [x],

        [y]

    )


    return (
        float(lon[0]),
        float(lat[0])
    )


# ================================================================
# CREATE RECORDS
# ================================================================

records = []


print()
print(
    "Creating spatial flood-risk records..."
)


for r in range(
    grid_rows
):

    r1 = (
        r * factor
    )

    r2 = min(
        r1 + factor,
        height
    )


    for c in range(
        grid_cols
    ):

        c1 = (
            c * factor
        )

        c2 = min(
            c1 + factor,
            width
        )


        valid_block = valid[
            r1:r2,
            c1:c2
        ]


        count = int(
            valid_block.sum()
        )


        if count < 5:

            continue


        vv_block = vv_change[
            r1:r2,
            c1:c2
        ]


        vh_block = vh_change[
            r1:r2,
            c1:c2
        ]


        score_block = score[
            r1:r2,
            c1:c2
        ]


        vv_values = vv_block[
            np.isfinite(
                vv_block
            )
        ]


        vh_values = vh_block[
            np.isfinite(
                vh_block
            )
        ]


        score_values = score_block[
            np.isfinite(
                score_block
            )
        ]


        if (

            vv_values.size == 0

            or

            vh_values.size == 0

            or

            score_values.size == 0

        ):

            continue


        mean_vv = float(
            np.mean(
                vv_values
            )
        )


        mean_vh = float(
            np.mean(
                vh_values
            )
        )


        mean_score = float(
            np.mean(
                score_values
            )
        )


        # --------------------------------------------------------
        # Cell classification
        # --------------------------------------------------------

        if mean_score >= 90:

            classification = (
                "Very High"
            )

        elif mean_score >= 70:

            classification = (
                "High"
            )

        elif mean_score >= 40:

            classification = (
                "Moderate"
            )

        else:

            classification = (
                "Low"
            )


        # --------------------------------------------------------
        # Center coordinate
        # --------------------------------------------------------

        center_row = (
            r1 + r2 - 1
        ) // 2


        center_col = (
            c1 + c2 - 1
        ) // 2


        lon, lat = (
            pixel_to_lonlat(
                center_row,
                center_col
            )
        )


        records.append({

            "Region":
                "Nagpur",

            "Latitude":
                round(
                    lat,
                    6
                ),

            "Longitude":
                round(
                    lon,
                    6
                ),

            "VV_Change_dB":
                round(
                    mean_vv,
                    3
                ),

            "VH_Change_dB":
                round(
                    mean_vh,
                    3
                ),

            "Flood_Risk_Score":
                round(
                    mean_score,
                    2
                ),

            "Flood_Risk_Class":
                classification,

            "Before_Date":
                str(
                    before_date
                ),

            "After_Date":
                str(
                    after_date
                ),

            "Satellite":
                "Sentinel-1",

            "Product":
                "Sentinel-1 GRD",

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
        "\nNo spatial records generated."
    )


print()
print(
    "Spatial records:",
    len(df)
)


# ================================================================
# SANITY CHECK
# ================================================================

if len(df) < 100:

    print()
    print(
        "WARNING:"
    )

    print(
        "Very few spatial cells were generated."
    )

    print(
        "The CSV will still only be saved if records exist."
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
# SUMMARY COUNTS
# ================================================================

very_high_count = int(
    (
        df[
            "Flood_Risk_Class"
        ]
        ==
        "Very High"
    ).sum()
)


high_count = int(
    (
        df[
            "Flood_Risk_Class"
        ]
        ==
        "High"
    ).sum()
)


moderate_count = int(
    (
        df[
            "Flood_Risk_Class"
        ]
        ==
        "Moderate"
    ).sum()
)


low_count = int(
    (
        df[
            "Flood_Risk_Class"
        ]
        ==
        "Low"
    ).sum()
)


total_cells = len(
    df
)


high_risk_percentage = (

    (
        very_high_count
        +
        high_count
    )

    /

    total_cells

    *

    100

)


# ================================================================
# SUMMARY CSV
# ================================================================

summary_df = pd.DataFrame([{

    "Region":
        "Nagpur",

    "Before_Date":
        str(
            before_date
        ),

    "After_Date":
        str(
            after_date
        ),

    "Total_Spatial_Cells":
        total_cells,

    "Very_High_Cells":
        very_high_count,

    "High_Cells":
        high_count,

    "Moderate_Cells":
        moderate_count,

    "Low_Cells":
        low_count,

    "High_Risk_Percentage":
        round(
            high_risk_percentage,
            2
        ),

    "Mean_VV_Change_dB":
        round(
            df[
                "VV_Change_dB"
            ].mean(),
            3
        ),

    "Mean_VH_Change_dB":
        round(
            df[
                "VH_Change_dB"
            ].mean(),
            3
        ),

    "Mean_Flood_Risk_Score":
        round(
            df[
                "Flood_Risk_Score"
            ].mean(),
            2
        ),

    "Satellite":
        "Sentinel-1",

    "Product":
        "Sentinel-1 GRD",

    "Source":
        "Microsoft Planetary Computer"

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
# CREATE PNG MAP
# ================================================================

print()
print(
    "Creating flood-risk map..."
)


plt.figure(
    figsize=(12, 9)
)


scatter = plt.scatter(

    df[
        "Longitude"
    ],

    df[
        "Latitude"
    ],

    c=df[
        "Flood_Risk_Score"
    ],

    cmap="RdYlGn_r",

    s=8,

    alpha=0.85,

    vmin=0,

    vmax=100

)


plt.colorbar(
    scatter,
    label="Flood Risk Score"
)


plt.xlabel(
    "Longitude"
)


plt.ylabel(
    "Latitude"
)


plt.title(

    "Nagpur Flood Risk / Inundation Indicator\n"

    f"Sentinel-1 SAR | "

    f"{before_date} → {after_date}"

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
# FINAL OUTPUT
# ================================================================

print()
print("=" * 70)
print("                 FLOOD ANALYSIS COMPLETE")
print("=" * 70)

print()
print(
    "Before date:",
    before_date
)

print(
    "After date:",
    after_date
)

print()
print(
    "Spatial cells:",
    total_cells
)

print()
print(
    "Very High:",
    very_high_count
)

print(
    "High:",
    high_count
)

print(
    "Moderate:",
    moderate_count
)

print(
    "Low:",
    low_count
)

print()
print(
    "High + Very High:",
    round(
        high_risk_percentage,
        2
    ),
    "%"
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
    "Flood map:"
)

print(
    PNG_FILE
)

print()
print(
    "Source:"
)

print(
    "Sentinel-1 GRD / Microsoft Planetary Computer"
)

print()
print(
    "Google Earth Engine: NOT USED"
)

print(
    "Bhuvan WMS: NOT USED"
)

print("=" * 70)