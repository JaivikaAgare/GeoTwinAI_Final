<<<<<<< HEAD
import os
import warnings
from datetime import datetime, timezone
=======
# ============================================================
# GeoTwinAI - Nagpur Built-up Area Analysis
# Source: Microsoft Planetary Computer
# Dataset: Sentinel-2 Level-2A
# Method: NDBI + NDVI built-up detection
# ============================================================

from pathlib import Path
import warnings
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
<<<<<<< HEAD
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
import pystac_client
import planetary_computer

warnings.filterwarnings("ignore")

# ============================================================
# GEOTWINAI - NAGPUR BUILT-UP AREA
# SENTINEL-2 L2A + MICROSOFT PLANETARY COMPUTER
# WINDOW-BASED READING VERSION
# ============================================================

# -----------------------------
# PROJECT PATHS
# -----------------------------

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

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# NAGPUR BBOX
# -----------------------------

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

# -----------------------------
# SETTINGS
# -----------------------------

COLLECTION = "sentinel-2-l2a"

# Built-up detection:
# NDBI = (SWIR - NIR) / (SWIR + NIR)
#
# Built-up pixels:
# NDBI > NDBI_THRESHOLD
# AND
# NDBI > NDVI
#
NDBI_THRESHOLD = 0.00

# Spatial aggregation
GRID_SIZE_DEGREES = 0.001

# Maximum cloud cover preferred
MAX_CLOUD = 30.0
=======

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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)
print("             NAGPUR BUILT-UP AREA ANALYSIS")
print("             SENTINEL-2 / PLANETARY COMPUTER")
<<<<<<< HEAD
print("             WINDOW-BASED SAFE READING")
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print("=" * 70)

print()
print("Project:")
<<<<<<< HEAD
print(BASE_DIR)
=======
print(PROJECT_DIR)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()
print("Output:")
print(OUTPUT_DIR)

<<<<<<< HEAD
print()
print("Nagpur BBOX:")
print(MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

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

<<<<<<< HEAD
now = datetime.now(timezone.utc)

search = catalog.search(
    collections=[COLLECTION],
    bbox=BBOX,
    datetime=f"2024-01-01T00:00:00Z/{now.isoformat()}",
)

items = list(search.item_collection())
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()
print("Scenes found:", len(items))

<<<<<<< HEAD

# ============================================================
# FIND ITEMS WITH REQUIRED ASSETS
# ============================================================

valid_items = []

for item in items:

    assets = item.assets

    # Different STAC naming possibilities
    red_ok = (
        "B04" in assets
        or "red" in assets
    )

    nir_ok = (
        "B08" in assets
        or "nir08" in assets
    )

    swir_ok = (
        "B11" in assets
        or "swir16" in assets
    )

    if red_ok and nir_ok and swir_ok:
        valid_items.append(item)


print("Scenes with required bands:", len(valid_items))


if not valid_items:
    raise RuntimeError(
        "No Sentinel-2 scenes containing Red, NIR and SWIR assets were found."
=======
if not items:
    raise RuntimeError(
        "No Sentinel-2 scenes found for the Nagpur area."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
<<<<<<< HEAD
# CLOUD COVER
# ============================================================

def get_cloud(item):

    value = item.properties.get(
        "eo:cloud_cover",
        999
    )
=======
# SORT BY CLOUD COVER THEN DATE
# ============================================================

def cloud_value(item):
    value = item.properties.get("eo:cloud_cover", 999)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    try:
        return float(value)
    except Exception:
<<<<<<< HEAD
        return 999.0


# ============================================================
# PREFER LATEST AVAILABLE SCENE
# ============================================================

low_cloud_items = [
    item
    for item in valid_items
    if get_cloud(item) <= MAX_CLOUD
]

if low_cloud_items:
    candidate_items = low_cloud_items
else:
    candidate_items = valid_items


candidate_items = sorted(
    candidate_items,
    key=lambda x: x.datetime or datetime.min.replace(
        tzinfo=timezone.utc
    ),
    reverse=True
)


print()
print("=" * 70)
print("                 BEST AVAILABLE SCENES")
print("=" * 70)

for item in candidate_items[:10]:
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    date_text = (
        item.datetime.strftime("%Y-%m-%d")
        if item.datetime
        else "Unknown"
    )

<<<<<<< HEAD
    print(
        f"{date_text} | "
        f"Cloud: {get_cloud(item):.2f}% | "
=======
    cloud = cloud_value(item)

    print(
        f"{date_text} | "
        f"Cloud: {cloud:.2f}% | "
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        f"{item.id}"
    )


# ============================================================
<<<<<<< HEAD
# SELECT LATEST
# ============================================================

item = candidate_items[0]
=======
# SELECT BEST SCENE
# ============================================================

item = items[0]
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

scene_date = (
    item.datetime.strftime("%Y-%m-%d")
    if item.datetime
    else "Unknown"
)

<<<<<<< HEAD
cloud = get_cloud(item)

=======
scene_cloud = cloud_value(item)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

print()
print("=" * 70)
print("                 SELECTED SENTINEL-2 SCENE")
print("=" * 70)

print()
print("Date:", scene_date)
<<<<<<< HEAD
print("Cloud cover:", cloud, "%")
=======
print("Cloud cover:", scene_cloud, "%")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
print("Scene:", item.id)


# ============================================================
<<<<<<< HEAD
# ASSET FINDER
# ============================================================

def get_asset(item, possible_names):

    for name in possible_names:

        if name in item.assets:
            return item.assets[name]

    raise KeyError(
        f"Could not find any of these assets: {possible_names}"
    )


red_asset = get_asset(
    item,
    ["B04", "red"]
)

nir_asset = get_asset(
    item,
    ["B08", "nir08"]
)

swir_asset = get_asset(
    item,
    ["B11", "swir16"]
)


print()
print("Required bands available:")

print("Red :", red_asset.title or red_asset.key)
print("NIR :", nir_asset.title or nir_asset.key)
print("SWIR:", swir_asset.title or swir_asset.key)


# ============================================================
# SAFE WINDOW READING
# ============================================================

def read_bbox_window(
    asset,
    bbox,
    target_shape=None
):

    """
    Read ONLY the Nagpur bounding box.

    This avoids:
        src.read(1)

    which attempts to read the complete raster.
    """

    with rasterio.open(asset.href) as src:

        print()
        print("Source CRS:", src.crs)
        print("Source size:", src.width, "x", src.height)

        # Transform WGS84 bbox into source CRS
        left, bottom, right, top = transform_bounds(
            "EPSG:4326",
            src.crs,
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            densify_pts=21
        )

        window = from_bounds(
            left,
            bottom,
            right,
            top,
            transform=src.transform
        )

        # Keep window inside raster
        window = window.round_offsets().round_lengths()

        window = window.intersection(
            rasterio.windows.Window(
                0,
                0,
                src.width,
                src.height
            )
        )

        if window.width <= 0 or window.height <= 0:
            raise RuntimeError(
                "Nagpur BBOX does not overlap raster."
            )

        print(
            "Reading window:",
            int(window.width),
            "x",
            int(window.height)
        )

        if target_shape is None:

            data = src.read(
                1,
                window=window,
                masked=True
            )

            transform = src.window_transform(window)

        else:

            data = src.read(
                1,
                window=window,
                out_shape=target_shape,
                resampling=Resampling.bilinear,
                masked=True
            )

            # New transform after resizing
            transform = src.window_transform(window)

            transform = transform * transform.scale(
                window.width / target_shape[1],
                window.height / target_shape[0]
            )

        data = data.astype("float32")

        return data, transform, src.crs


# ============================================================
# READ RED
# ============================================================

print()
print("=" * 70)
print("READING RED BAND")
print("=" * 70)

red, red_transform, red_crs = read_bbox_window(
    red_asset,
    BBOX
)

print(
    "Red shape:",
    red.shape
)


# ============================================================
# READ NIR
# ============================================================

print()
print("=" * 70)
print("READING NIR BAND")
print("=" * 70)

nir, nir_transform, nir_crs = read_bbox_window(
    nir_asset,
    BBOX,
    target_shape=red.shape
)

print(
    "NIR shape:",
    nir.shape
)


# ============================================================
# READ SWIR
# ============================================================

print()
print("=" * 70)
print("READING SWIR BAND")
print("=" * 70)

swir, swir_transform, swir_crs = read_bbox_window(
    swir_asset,
    BBOX,
    target_shape=red.shape
)

print(
    "SWIR shape:",
    swir.shape
)


# ============================================================
# CONVERT MASKED ARRAYS
# ============================================================

red_data = np.asarray(
    red.filled(np.nan),
    dtype="float32"
)

nir_data = np.asarray(
    nir.filled(np.nan),
    dtype="float32"
)

swir_data = np.asarray(
    swir.filled(np.nan),
    dtype="float32"
)


# ============================================================
# SCALE REFLECTANCE
# ============================================================

# Sentinel-2 L2A reflectance values are normally scaled.
#
# Dividing by 10000 does not change NDVI/NDBI because
# the same scale factor exists in numerator and denominator.
#
# We keep values as float32 for faster processing.

red_data = red_data / 10000.0
nir_data = nir_data / 10000.0
swir_data = swir_data / 10000.0
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


# ============================================================
# VALID PIXELS
# ============================================================

valid = (
<<<<<<< HEAD
    np.isfinite(red_data)
    &
    np.isfinite(nir_data)
    &
    np.isfinite(swir_data)
    &
    (red_data >= 0)
    &
    (nir_data >= 0)
    &
    (swir_data >= 0)
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

print()
print("Valid pixels:", int(valid.sum()))


if valid.sum() == 0:
<<<<<<< HEAD
    raise RuntimeError(
        "No valid Sentinel-2 pixels found inside Nagpur BBOX."
=======

    raise RuntimeError(
        "No valid Sentinel-2 pixels were found."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )


# ============================================================
# NDVI
# ============================================================

print()
print("Calculating NDVI...")

<<<<<<< HEAD
ndvi_den = nir_data + red_data

ndvi = np.full(
    red_data.shape,
=======
ndvi = np.full(
    red.shape,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    np.nan,
    dtype="float32"
)

<<<<<<< HEAD
ndvi_mask = (
    valid
    &
    (np.abs(ndvi_den) > 1e-8)
)

ndvi[ndvi_mask] = (
    (nir_data[ndvi_mask] - red_data[ndvi_mask])
    /
    ndvi_den[ndvi_mask]
)


=======
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

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================
# NDBI
# ============================================================

print("Calculating NDBI...")

<<<<<<< HEAD
ndbi_den = swir_data + nir_data

ndbi = np.full(
    red_data.shape,
=======
ndbi = np.full(
    red.shape,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    np.nan,
    dtype="float32"
)

<<<<<<< HEAD
ndbi_mask = (
    valid
    &
    (np.abs(ndbi_den) > 1e-8)
)

ndbi[ndbi_mask] = (
    (swir_data[ndbi_mask] - nir_data[ndbi_mask])
    /
    ndbi_den[ndbi_mask]
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)


# ============================================================
<<<<<<< HEAD
# BUILT-UP DETECTION
# ============================================================

print()
print("Detecting built-up pixels...")

builtup_mask = (
    np.isfinite(ndbi)
    &
    np.isfinite(ndvi)
    &
    (ndbi > NDBI_THRESHOLD)
    &
    (ndbi > ndvi)
)

builtup_pixels = int(
    builtup_mask.sum()
)

valid_pixels = int(
    np.isfinite(ndbi).sum()
)

print(
    "Built-up pixels:",
    builtup_pixels
)

print(
    "Valid NDBI pixels:",
    valid_pixels
)


if valid_pixels > 0:

    builtup_percentage = (
        builtup_pixels
        /
        valid_pixels
        *
        100
    )

else:

    builtup_percentage = 0


print(
    "Built-up percentage:",
    round(builtup_percentage, 2),
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    "%"
)


# ============================================================
<<<<<<< HEAD
# CREATE APPROXIMATE 100m GRID
# ============================================================

print()
print("Aggregating pixels into approximately 100m cells...")


height, width = ndbi.shape

# Approximately 10 pixels for Sentinel-2 10m data
BLOCK = 10


records = []

pixel_transform = red_transform


# ============================================================
# SPATIAL AGGREGATION
# ============================================================

for row_start in range(
    0,
    height,
    BLOCK
):

    row_end = min(
        row_start + BLOCK,
        height
    )

    for col_start in range(
        0,
        width,
        BLOCK
    ):

        col_end = min(
            col_start + BLOCK,
            width
        )

        ndbi_block = ndbi[
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            row_start:row_end,
            col_start:col_end
        ]

<<<<<<< HEAD
        ndvi_block = ndvi[
=======
        ndbi_block = ndbi[
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            row_start:row_end,
            col_start:col_end
        ]

        built_block = builtup_mask[
            row_start:row_end,
            col_start:col_end
        ]

<<<<<<< HEAD
        valid_block = np.isfinite(
            ndbi_block
        )

        count = int(
            valid_block.sum()
        )

        if count == 0:
            continue

        mean_ndbi = float(
            np.nanmean(ndbi_block)
        )

        mean_ndvi = float(
            np.nanmean(ndvi_block)
        )

        built_count = int(
            built_block.sum()
        )

        fraction = (
            built_count / count
        )

        # Cell centre
        center_row = (
            row_start + row_end
        ) / 2

        center_col = (
            col_start + col_end
        ) / 2

        x, y = rasterio.transform.xy(
            pixel_transform,
            center_row,
            center_col,
            offset="center"
        )

        # Convert projected coordinates back to WGS84
        from rasterio.warp import transform

        lon, lat = transform(
            red_crs,
            "EPSG:4326",
            [x],
            [y]
        )

        longitude = float(
            lon[0]
        )

        latitude = float(
            lat[0]
        )

        if fraction >= 0.50:

            built_class = "High Built-up"

        elif fraction >= 0.20:

            built_class = "Moderate Built-up"

        else:

            built_class = "Low Built-up"


        records.append(
            {
                "Latitude": latitude,
                "Longitude": longitude,
                "Mean_NDBI": round(
                    mean_ndbi,
                    4
                ),
                "Mean_NDVI": round(
                    mean_ndvi,
                    4
                ),
                "BuiltUp_Pixel_Count": built_count,
                "Valid_Pixel_Count": count,
                "BuiltUp_Fraction": round(
                    fraction,
                    4
                ),
                "BuiltUp_Percent": round(
                    fraction * 100,
                    2
                ),
                "BuiltUp_Class": built_class,
                "Scene_Date": scene_date,
                "Cloud_Cover_Percent": round(
                    cloud,
                    2
                ),
                "Satellite": "Sentinel-2"
            }
        )
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


# ============================================================
# DATAFRAME
# ============================================================

<<<<<<< HEAD
df = pd.DataFrame(
    records
)

print()
print(
    "Spatial records:",
    len(df)
)


if df.empty:
    raise RuntimeError(
        "No spatial built-up records were generated."
    )


=======
df = pd.DataFrame(records)


if df.empty:

    raise RuntimeError(
        "No spatial records were created."
    )


print()
print("Spatial records:", len(df))


>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================
# SAVE SPATIAL CSV
# ============================================================

<<<<<<< HEAD
spatial_csv = os.path.join(
    OUTPUT_DIR,
    "Nagpur_BuiltUp_Spatial.csv"
)

df.to_csv(
    spatial_csv,
    index=False
)

print()
print("Spatial CSV saved:")
print(spatial_csv)

=======
df.to_csv(
    CSV_FILE,
    index=False
)

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

# ============================================================
# SUMMARY
# ============================================================

<<<<<<< HEAD
mean_ndbi = float(
    df["Mean_NDBI"].mean()
)

max_ndbi = float(
    df["Mean_NDBI"].max()
)

min_ndbi = float(
    df["Mean_NDBI"].min()
)

mean_builtup = float(
    df["BuiltUp_Percent"].mean()
)

high_cells = int(
    (
        df["BuiltUp_Class"]
        ==
        "High Built-up"
    ).sum()
)

moderate_cells = int(
    (
        df["BuiltUp_Class"]
        ==
        "Moderate Built-up"
    ).sum()
)

low_cells = int(
    (
        df["BuiltUp_Class"]
        ==
        "Low Built-up"
    ).sum()
)


summary = pd.DataFrame(
    [
        {
            "Dataset": "Nagpur Built-up Area",
            "Satellite": "Sentinel-2",
            "Scene_Date": scene_date,
            "Cloud_Cover_Percent": round(
                cloud,
                2
            ),
            "Spatial_Records": len(df),
            "Valid_Pixels": valid_pixels,
            "BuiltUp_Pixels": builtup_pixels,
            "BuiltUp_Percentage": round(
                builtup_percentage,
                2
            ),
            "Mean_NDBI": round(
                mean_ndbi,
                4
            ),
            "Minimum_NDBI": round(
                min_ndbi,
                4
            ),
            "Maximum_NDBI": round(
                max_ndbi,
                4
            ),
            "Mean_Cell_BuiltUp_Percent": round(
                mean_builtup,
                2
            ),
            "High_BuiltUp_Cells": high_cells,
            "Moderate_BuiltUp_Cells": moderate_cells,
            "Low_BuiltUp_Cells": low_cells
        }
    ]
)


summary_csv = os.path.join(
    OUTPUT_DIR,
    "Nagpur_BuiltUp_Summary.csv"
)

summary.to_csv(
    summary_csv,
    index=False
)

print()
print("Summary CSV saved:")
print(summary_csv)


# ============================================================
# PNG
# ============================================================

print()
print("Creating Built-up PNG...")


plt.figure(
    figsize=(12, 8)
)

scatter = plt.scatter(
    df["Longitude"],
    df["Latitude"],
    c=df["BuiltUp_Percent"],
    s=8,
    cmap="Reds",
    vmin=0,
    vmax=100
)

plt.colorbar(
    scatter,
    label="Built-up Percentage (%)"
)

plt.xlabel(
    "Longitude"
)

plt.ylabel(
    "Latitude"
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

plt.title(
    f"Nagpur Built-up Area\n"
    f"Sentinel-2 | {scene_date}"
)

<<<<<<< HEAD
plt.tight_layout()


png_path = os.path.join(
    OUTPUT_DIR,
    "Nagpur_BuiltUp.png"
)

plt.savefig(
    png_path,
    dpi=150
=======
plt.xlabel("10 m Grid Column")
plt.ylabel("10 m Grid Row")

plt.tight_layout()

plt.savefig(
    PNG_FILE,
    dpi=200,
    bbox_inches="tight"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

plt.close()


# ============================================================
<<<<<<< HEAD
# FINAL REPORT
=======
# FINAL OUTPUT
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

print()
print("=" * 70)
<<<<<<< HEAD
print("              BUILT-UP ANALYSIS COMPLETED")
print("=" * 70)

print()
print("Satellite:", "Sentinel-2")
print("Scene date:", scene_date)
print("Cloud cover:", round(cloud, 2), "%")

print()
print("Spatial records:", len(df))

print(
    "Built-up pixels:",
    builtup_pixels
)

print(
    "Built-up percentage:",
    round(
        builtup_percentage,
        2
    ),
    "%"
)

print(
    "Mean NDBI:",
    round(
        mean_ndbi,
        4
    )
)

print()
print("FILES CREATED")
print()
print("1. Spatial CSV:")
print(spatial_csv)

print()
print("2. Summary CSV:")
print(summary_csv)

print()
print("3. PNG:")
print(png_path)

print()
print("Google Earth Engine: NOT USED")

print()
print("=" * 70)
print("                    SUCCESS")
print("=" * 70)
=======
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
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
