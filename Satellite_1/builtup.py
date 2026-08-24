# ============================================================
# GeoTwinAI - Nagpur Built-up Area Analysis
# Source: Microsoft Planetary Computer
# Dataset: Sentinel-2 Level-2A
# Method: NDBI + NDVI built-up detection
# ============================================================

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pystac_client
import planetary_computer
import rasterio
from rasterio.warp import reproject, Resampling

warnings.filterwarnings("ignore")


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_DIR / "output" / "satellite"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = OUTPUT_DIR / "Nagpur_BuiltUp_Spatial.csv"
SUMMARY_FILE = OUTPUT_DIR / "Nagpur_BuiltUp_Summary.csv"
PNG_FILE = OUTPUT_DIR / "Nagpur_BuiltUp.png"


# ============================================================
# NAGPUR APPROXIMATE AOI
# No GeoJSON / boundary file required
# ============================================================

# [min_lon, min_lat, max_lon, max_lat]
NAGPUR_BBOX = [
    78.95,
    21.05,
    79.20,
    21.25
]


# ============================================================
# SETTINGS
# ============================================================

COLLECTION = "sentinel-2-l2a"

MAX_CLOUD = 20

# Spatial aggregation
# 10 m Sentinel-2 pixels -> approximately 100 m cells
GRID_SIZE = 10

# Built-up detection thresholds
NDBI_THRESHOLD = 0.05
NDVI_MAX_FOR_BUILTUP = 0.40


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)
print("             NAGPUR BUILT-UP AREA ANALYSIS")
print("             SENTINEL-2 / PLANETARY COMPUTER")
print("=" * 70)

print()
print("Project:")
print(PROJECT_DIR)

print()
print("Output:")
print(OUTPUT_DIR)


# ============================================================
# CONNECT TO PLANETARY COMPUTER
# ============================================================

print()
print("Connecting to Microsoft Planetary Computer...")

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace
)

print("Connection successful.")


# ============================================================
# SEARCH SENTINEL-2
# ============================================================

print()
print("Searching Sentinel-2 L2A scenes...")

search = catalog.search(
    collections=[COLLECTION],
    bbox=NAGPUR_BBOX,
    datetime="2025-01-01/2026-12-31",
    query={
        "eo:cloud_cover": {
            "lt": MAX_CLOUD
        }
    }
)

items = list(search.items())

print()
print("Scenes found:", len(items))

if not items:
    raise RuntimeError(
        "No Sentinel-2 scenes found for the Nagpur area."
    )


# ============================================================
# SORT BY CLOUD COVER THEN DATE
# ============================================================

def cloud_value(item):
    value = item.properties.get("eo:cloud_cover", 999)

    try:
        return float(value)
    except Exception:
        return 999


items = sorted(
    items,
    key=lambda x: (
        cloud_value(x),
        -(x.datetime.timestamp() if x.datetime else 0)
    )
)


# ============================================================
# SHOW BEST SCENES
# ============================================================

print()
print("Best available scenes:")

for item in items[:10]:

    date_text = (
        item.datetime.strftime("%Y-%m-%d")
        if item.datetime
        else "Unknown"
    )

    cloud = cloud_value(item)

    print(
        f"{date_text} | "
        f"Cloud: {cloud:.2f}% | "
        f"{item.id}"
    )


# ============================================================
# SELECT BEST SCENE
# ============================================================

item = items[0]

scene_date = (
    item.datetime.strftime("%Y-%m-%d")
    if item.datetime
    else "Unknown"
)

scene_cloud = cloud_value(item)

print()
print("=" * 70)
print("                 SELECTED SENTINEL-2 SCENE")
print("=" * 70)

print()
print("Date:", scene_date)
print("Cloud cover:", scene_cloud, "%")
print("Scene:", item.id)


# ============================================================
# CHECK REQUIRED BANDS
# ============================================================

required_bands = ["B04", "B08", "B11"]

for band in required_bands:

    if band not in item.assets:

        raise RuntimeError(
            f"Required Sentinel-2 asset {band} "
            f"was not found in the selected scene."
        )

print()
print("Required bands available:")
print("B04 - Red")
print("B08 - Near Infrared")
print("B11 - SWIR")


# ============================================================
# READ BAND
# ============================================================

def read_band(asset):

    href = asset.href

    with rasterio.open(href) as src:

        data = src.read(1).astype("float32")

        transform = src.transform
        crs = src.crs

        nodata = src.nodata

        profile = src.profile.copy()

    return data, transform, crs, nodata, profile


# ============================================================
# READ B04
# ============================================================

print()
print("Reading B04...")

red, red_transform, red_crs, red_nodata, red_profile = read_band(
    item.assets["B04"]
)

print("B04 shape:", red.shape)


# ============================================================
# READ B08
# ============================================================

print()
print("Reading B08...")

nir, nir_transform, nir_crs, nir_nodata, nir_profile = read_band(
    item.assets["B08"]
)

print("B08 shape:", nir.shape)


# ============================================================
# CHECK GRID
# ============================================================

if red.shape != nir.shape:

    print()
    print("B04 and B08 grids differ.")
    print("Reprojecting B08 to B04 grid...")

    nir_resampled = np.zeros_like(red, dtype="float32")

    reproject(
        source=nir,
        destination=nir_resampled,
        src_transform=nir_transform,
        src_crs=nir_crs,
        dst_transform=red_transform,
        dst_crs=red_crs,
        resampling=Resampling.bilinear
    )

    nir = nir_resampled


# ============================================================
# READ B11
# ============================================================

print()
print("Reading B11...")

swir, swir_transform, swir_crs, swir_nodata, swir_profile = read_band(
    item.assets["B11"]
)

print("B11 original shape:", swir.shape)


# ============================================================
# IMPORTANT FIX
# ============================================================
# B11 is 20 m.
# B04/B08 are 10 m.
#
# Instead of multiplying an Affine transform by a tuple,
# properly reproject B11 onto the B04 10 m grid.
# ============================================================

print()
print("Resampling B11 from 20 m to 10 m grid...")

swir_10m = np.zeros(
    red.shape,
    dtype="float32"
)

reproject(
    source=swir,
    destination=swir_10m,
    src_transform=swir_transform,
    src_crs=swir_crs,
    dst_transform=red_transform,
    dst_crs=red_crs,
    resampling=Resampling.bilinear
)

swir = swir_10m

print("B11 resampled shape:", swir.shape)


# ============================================================
# SENTINEL-2 REFLECTANCE SCALE
# ============================================================

# Sentinel-2 L2A reflectance is normally scaled by 10000.
#
# If the values are already <= 1, don't divide again.

def convert_reflectance(array):

    array = array.astype("float32")

    valid = array[np.isfinite(array)]

    if valid.size == 0:
        return array

    maximum = np.nanpercentile(valid, 99)

    if maximum > 2:
        array = array / 10000.0

    return array


red = convert_reflectance(red)
nir = convert_reflectance(nir)
swir = convert_reflectance(swir)


# ============================================================
# VALID PIXELS
# ============================================================

valid = (
    np.isfinite(red)
    &
    np.isfinite(nir)
    &
    np.isfinite(swir)
    &
    (red > 0)
    &
    (nir > 0)
    &
    (swir > 0)
)

print()
print("Valid pixels:", int(valid.sum()))


if valid.sum() == 0:

    raise RuntimeError(
        "No valid Sentinel-2 pixels were found."
    )


# ============================================================
# NDVI
# ============================================================

print()
print("Calculating NDVI...")

ndvi = np.full(
    red.shape,
    np.nan,
    dtype="float32"
)

ndvi_denominator = nir + red

safe_ndvi = (
    valid
    &
    (np.abs(ndvi_denominator) > 1e-8)
)

ndvi[safe_ndvi] = (
    (nir[safe_ndvi] - red[safe_ndvi])
    /
    ndvi_denominator[safe_ndvi]
)

# ============================================================
# NDBI
# ============================================================

print("Calculating NDBI...")

ndbi = np.full(
    red.shape,
    np.nan,
    dtype="float32"
)

ndbi_denominator = swir + nir

safe_ndbi = (
    valid
    &
    (np.abs(ndbi_denominator) > 1e-8)
)

ndbi[safe_ndbi] = (
    (swir[safe_ndbi] - nir[safe_ndbi])
    /
    ndbi_denominator[safe_ndbi]
)


# ============================================================
# BUILT-UP CLASSIFICATION
# ============================================================

print()
print("Classifying built-up pixels...")

builtup_mask = (
    valid
    &
    (ndbi > NDBI_THRESHOLD)
    &
    (ndvi < NDVI_MAX_FOR_BUILTUP)
)


builtup_percentage = (
    builtup_mask.sum()
    /
    valid.sum()
) * 100


print()
print("Built-up pixels:", int(builtup_mask.sum()))

print(
    "Built-up percentage:",
    round(float(builtup_percentage), 2),
    "%"
)


# ============================================================
# SPATIAL AGGREGATION
# ============================================================

print()
print("Aggregating pixels into approximately 100 m cells...")


height, width = red.shape

grid_rows = height // GRID_SIZE
grid_cols = width // GRID_SIZE


print()
print("Spatial grid:")
print(
    grid_cols,
    "x",
    grid_rows
)


records = []


# ============================================================
# COORDINATE TRANSFORMATION
# ============================================================

def pixel_to_lonlat(row, col):

    x, y = rasterio.transform.xy(
        red_transform,
        row,
        col,
        offset="center"
    )

    return float(x), float(y)


# ============================================================
# CREATE SPATIAL RECORDS
# ============================================================

print()
print("Creating spatial CSV records...")


for r in range(grid_rows):

    row_start = r * GRID_SIZE
    row_end = row_start + GRID_SIZE

    for c in range(grid_cols):

        col_start = c * GRID_SIZE
        col_end = col_start + GRID_SIZE

        ndvi_block = ndvi[
            row_start:row_end,
            col_start:col_end
        ]

        ndbi_block = ndbi[
            row_start:row_end,
            col_start:col_end
        ]

        built_block = builtup_mask[
            row_start:row_end,
            col_start:col_end
        ]

        valid_block = valid[
            row_start:row_end,
            col_start:col_end
        ]

        if not valid_block.any():
            continue

        valid_ndvi = ndvi_block[
            np.isfinite(ndvi_block)
        ]

        valid_ndbi = ndbi_block[
            np.isfinite(ndbi_block)
        ]

        if valid_ndvi.size == 0:
            continue

        if valid_ndbi.size == 0:
            continue

        built_pixels = int(
            built_block.sum()
        )

        total_pixels = int(
            valid_block.sum()
        )

        built_percent = (
            built_pixels /
            total_pixels
        ) * 100

        center_row = (
            row_start + row_end - 1
        ) // 2

        center_col = (
            col_start + col_end - 1
        ) // 2

        lon, lat = pixel_to_lonlat(
            center_row,
            center_col
        )

        records.append({

            "Region": "Nagpur",

            "Latitude": round(lat, 6),

            "Longitude": round(lon, 6),

            "NDVI_Mean": round(
                float(np.nanmean(valid_ndvi)),
                4
            ),

            "NDBI_Mean": round(
                float(np.nanmean(valid_ndbi)),
                4
            ),

            "BuiltUp_Pixels": built_pixels,

            "Valid_Pixels": total_pixels,

            "BuiltUp_Percent": round(
                float(built_percent),
                2
            ),

            "Scene_Date": scene_date,

            "Cloud_Cover_Percent": round(
                float(scene_cloud),
                4
            ),

            "Satellite": "Sentinel-2",

            "Source": "Microsoft Planetary Computer"

        })


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(records)


if df.empty:

    raise RuntimeError(
        "No spatial records were created."
    )


print()
print("Spatial records:", len(df))


# ============================================================
# SAVE SPATIAL CSV
# ============================================================

df.to_csv(
    CSV_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

summary = pd.DataFrame([{

    "Region": "Nagpur",

    "Scene_Date": scene_date,

    "Cloud_Cover_Percent": round(
        float(scene_cloud),
        4
    ),

    "Valid_Pixels": int(
        valid.sum()
    ),

    "BuiltUp_Pixels": int(
        builtup_mask.sum()
    ),

    "BuiltUp_Percentage": round(
        float(builtup_percentage),
        2
    ),

    "Mean_NDVI": round(
        float(np.nanmean(ndvi)),
        4
    ),

    "Mean_NDBI": round(
        float(np.nanmean(ndbi)),
        4
    ),

    "Satellite": "Sentinel-2",

    "Source": "Microsoft Planetary Computer"

}])


summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# PNG MAP
# ============================================================

print()
print("Creating built-up map...")


plt.figure(
    figsize=(10, 8)
)

plt.imshow(
    builtup_mask,
    cmap="gray",
    interpolation="nearest"
)

plt.title(
    f"Nagpur Built-up Area\n"
    f"Sentinel-2 | {scene_date}"
)

plt.xlabel("10 m Grid Column")
plt.ylabel("10 m Grid Row")

plt.tight_layout()

plt.savefig(
    PNG_FILE,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("                  PROCESS COMPLETED")
print("=" * 70)

print()
print("CSV:")
print(CSV_FILE)

print()
print("SUMMARY:")
print(SUMMARY_FILE)

print()
print("PNG:")
print(PNG_FILE)

print()
print("Built-up percentage:")
print(
    round(float(builtup_percentage), 2),
    "%"
)

print()
print("Source:")
print("Microsoft Planetary Computer / Sentinel-2 L2A")

print()
print("No Google Earth Engine used.")
print("No GeoJSON boundary required.")
print()