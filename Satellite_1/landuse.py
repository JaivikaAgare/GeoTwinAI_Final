# ================================================================
#                  GEOTWINAI
#              NAGPUR DIGITAL TWIN
#          LAND USE / LAND COVER ANALYSIS
#
# Source:
# ESA WorldCover 2021 v200
# Direct ESA AWS Open Data
#
# NO GOOGLE EARTH ENGINE
# ================================================================

import os
import requests
import rasterio
import pandas as pd
import numpy as np

from rasterio.mask import mask
from rasterio.transform import xy
from shapely.geometry import box, mapping


# ================================================================
# PROJECT PATHS
# ================================================================

BASE_DIR = r"D:\GeoTwinAI_Final"

INPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "bhuvan",
    "lulc"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output",
    "satellite"
)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ================================================================
# FILE PATHS
# ================================================================

TILE_NAME = "ESA_WorldCover_10m_2021_v200_N21E078_Map.tif"

DOWNLOAD_URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/"
    "v200/2021/map/"
    + TILE_NAME
)

TILE_PATH = os.path.join(
    INPUT_DIR,
    TILE_NAME
)

NAGPUR_RASTER = os.path.join(
    OUTPUT_DIR,
    "Nagpur_LULC_2021.tif"
)

LULC_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_LULC.csv"
)

SUMMARY_CSV = os.path.join(
    OUTPUT_DIR,
    "Nagpur_LULC_Summary.csv"
)


# ================================================================
# NAGPUR AOI
# ================================================================
#
# Approximate Nagpur urban area
#
# West  = 78.95
# South = 21.00
# East  = 79.25
# North = 21.30
#
# ================================================================

NAGPUR_BBOX = (
    78.95,
    21.00,
    79.25,
    21.30
)


# ================================================================
# ESA WORLDCOVER CLASSES
# ================================================================

LULC_CLASSES = {

    10: "Tree Cover",

    20: "Shrubland",

    30: "Grassland",

    40: "Cropland",

    50: "Built-up",

    60: "Bare / Sparse Vegetation",

    70: "Snow / Ice",

    80: "Permanent Water Bodies",

    90: "Herbaceous Wetland",

    95: "Mangroves",

    100: "Moss / Lichen"
}


# ================================================================
# HEADER
# ================================================================

print("=" * 70)
print("              GEOTWINAI")
print("          NAGPUR DIGITAL TWIN")
print("       LAND USE / LAND COVER")
print("=" * 70)

print()
print("Source:")
print("ESA WorldCover 2021 v200")

print()
print("Method:")
print("Direct ESA AWS download")

print()
print("Earth Engine:")
print("NOT USED")

print()
print("Input:")
print(INPUT_DIR)

print()
print("Output:")
print(OUTPUT_DIR)

print("=" * 70)


# ================================================================
# STEP 1
# DOWNLOAD ESA TILE
# ================================================================

print()
print("STEP 1: Checking ESA WorldCover tile...")
print()

if os.path.exists(TILE_PATH):

    print("Tile already exists:")
    print(TILE_PATH)

else:

    print("Tile not found.")
    print()
    print("Downloading:")
    print(TILE_NAME)
    print()

    try:

        response = requests.get(
            DOWNLOAD_URL,
            stream=True,
            timeout=60
        )

        response.raise_for_status()

        total_size = int(
            response.headers.get(
                "content-length",
                0
            )
        )

        downloaded = 0

        with open(
            TILE_PATH,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    file.write(chunk)

                    downloaded += len(chunk)

                    if total_size:

                        percent = (
                            downloaded
                            / total_size
                            * 100
                        )

                        print(
                            f"\rDownloading: "
                            f"{percent:.1f}%",
                            end=""
                        )

        print()
        print()
        print("Download completed.")

    except Exception as e:

        print()
        print("ERROR while downloading ESA data.")
        print()
        print(e)

        raise SystemExit(1)


# ================================================================
# CHECK TILE
# ================================================================

if not os.path.exists(TILE_PATH):

    print()
    print("ERROR:")
    print("ESA WorldCover GeoTIFF was not created.")

    raise SystemExit(1)


file_size_mb = (
    os.path.getsize(TILE_PATH)
    / (1024 * 1024)
)

print()
print(
    f"Downloaded file size: "
    f"{file_size_mb:.2f} MB"
)


# ================================================================
# STEP 2
# CROP NAGPUR
# ================================================================

print()
print("=" * 70)
print("STEP 2: Extracting Nagpur area...")
print("=" * 70)

min_lon, min_lat, max_lon, max_lat = NAGPUR_BBOX

nagpur_polygon = box(
    min_lon,
    min_lat,
    max_lon,
    max_lat
)

try:

    with rasterio.open(TILE_PATH) as src:

        print()
        print("Original raster:")
        print("CRS:", src.crs)
        print("Width:", src.width)
        print("Height:", src.height)
        print("Resolution:", src.res)

        cropped_data, cropped_transform = mask(
            src,
            [mapping(nagpur_polygon)],
            crop=True
        )

        profile = src.profile.copy()

        profile.update(
            {
                "height": cropped_data.shape[1],
                "width": cropped_data.shape[2],
                "transform": cropped_transform,
                "compress": "lzw"
            }
        )

        with rasterio.open(
            NAGPUR_RASTER,
            "w",
            **profile
        ) as dst:

            dst.write(cropped_data)


except Exception as e:

    print()
    print("ERROR while cropping raster.")
    print(e)

    raise SystemExit(1)


print()
print("Nagpur raster created:")
print(NAGPUR_RASTER)


# ================================================================
# STEP 3
# READ NAGPUR RASTER
# ================================================================

print()
print("=" * 70)
print("STEP 3: Reading Nagpur LULC pixels...")
print("=" * 70)

with rasterio.open(
    NAGPUR_RASTER
) as src:

    data = src.read(1)

    transform = src.transform

    nodata = src.nodata

    width = src.width
    height = src.height

    crs = src.crs

    resolution = src.res


print()
print("Nagpur raster information:")
print()
print("Rows:", height)
print("Columns:", width)
print("CRS:", crs)
print("Resolution:", resolution)
print("NoData:", nodata)


# ================================================================
# STEP 4
# CREATE SPATIAL CSV
# ================================================================

print()
print("=" * 70)
print("STEP 4: Creating spatial LULC CSV...")
print("=" * 70)

rows = []

for row in range(height):

    for col in range(width):

        value = int(
            data[row, col]
        )

        # Skip invalid pixels
        if value == 0:
            continue

        if nodata is not None:

            if value == nodata:
                continue

        latitude, longitude = xy(
            transform,
            row,
            col,
            offset="center"
        )

        class_name = LULC_CLASSES.get(
            value,
            "Unknown"
        )

        rows.append(
            {
                "Latitude": latitude,
                "Longitude": longitude,
                "LULC_Code": value,
                "LULC_Class": class_name
            }
        )


# ================================================================
# DATAFRAME
# ================================================================

df = pd.DataFrame(rows)


# ================================================================
# SAVE SPATIAL CSV
# ================================================================

df.to_csv(
    LULC_CSV,
    index=False
)

print()
print("Spatial LULC CSV created:")
print(LULC_CSV)

print()
print(
    f"Total valid pixels: "
    f"{len(df):,}"
)


# ================================================================
# STEP 5
# LULC SUMMARY
# ================================================================

print()
print("=" * 70)
print("STEP 5: Calculating LULC area...")
print("=" * 70)


summary = (
    df.groupby(
        [
            "LULC_Code",
            "LULC_Class"
        ]
    )
    .size()
    .reset_index(
        name="Pixel_Count"
    )
)


# ================================================================
# AREA
# ================================================================
#
# WorldCover = approximately 10m
#
# Pixel area = 10m x 10m
#             = 100 square metres
#
# 1 km² = 1,000,000 m²
#
# ================================================================

summary["Area_m2"] = (
    summary["Pixel_Count"]
    * 100
)

summary["Area_km2"] = (
    summary["Area_m2"]
    / 1_000_000
)


# ================================================================
# PERCENTAGE
# ================================================================

total_pixels = (
    summary["Pixel_Count"]
    .sum()
)

summary["Percentage"] = (
    summary["Pixel_Count"]
    / total_pixels
    * 100
)


# ================================================================
# SORT
# ================================================================

summary = summary.sort_values(
    "Area_km2",
    ascending=False
)


# ================================================================
# SAVE SUMMARY
# ================================================================

summary.to_csv(
    SUMMARY_CSV,
    index=False
)


# ================================================================
# DISPLAY SUMMARY
# ================================================================

print()

print(
    summary[
        [
            "LULC_Code",
            "LULC_Class",
            "Pixel_Count",
            "Area_km2",
            "Percentage"
        ]
    ].to_string(
        index=False
    )
)


# ================================================================
# FINAL
# ================================================================

print()
print("=" * 70)
print("                    COMPLETED")
print("=" * 70)

print()
print("Generated files:")

print()
print("1. Original ESA tile:")
print(TILE_PATH)

print()
print("2. Nagpur LULC raster:")
print(NAGPUR_RASTER)

print()
print("3. Spatial LULC CSV:")
print(LULC_CSV)

print()
print("4. LULC Summary:")
print(SUMMARY_CSV)

print()
print("=" * 70)
print("          READY FOR POWER BI")
print("=" * 70)

