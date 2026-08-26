import os
import sys
import subprocess
from datetime import datetime

# ============================================================
# GEOTWINAI - COMPLETE AUTO UPDATE PIPELINE
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PYTHON = sys.executable

OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
SATELLITE_DIR = os.path.join(OUTPUT_DIR, "satellite")
PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SATELLITE_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def run_script(title, script_path):

    print("\n" + "=" * 80)
    print(f"RUNNING: {title}")
    print("=" * 80)

    full_path = os.path.join(PROJECT_DIR, script_path)

    if not os.path.exists(full_path):
        print(f"FILE NOT FOUND: {full_path}")
        return False

    result = subprocess.run(
        [PYTHON, full_path],
        cwd=PROJECT_DIR
    )

    if result.returncode == 0:
        print(f"\nSUCCESS: {title}")
        return True

    print(f"\nFAILED: {title}")
    print(f"Return code: {result.returncode}")

    return False


# ============================================================
# START
# ============================================================

print("\n" + "=" * 80)
print("              GEOTWINAI COMPLETE AUTO UPDATE")
print("              NAGPUR DIGITAL TWIN")
print("=" * 80)

print(f"\nProject:")
print(PROJECT_DIR)

print("\nUpdate time:")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("\n" + "=" * 80)


# ============================================================
# STEP 1
# OSM DATA
# ============================================================

print("\n" + "=" * 80)
print("STEP 1 - UPDATING OSM DATA")
print("=" * 80)

run_script(
    "Buildings / Roads / Hospitals / Schools / Parks / WaterBodies",
    "main.py"
)


# ============================================================
# STEP 2
# SATELLITE DATA
# ============================================================

print("\n" + "=" * 80)
print("STEP 2 - UPDATING SATELLITE DATA")
print("=" * 80)

satellite_scripts = [

    (
        "Sentinel-2 NDVI",
        "Satellite_1/ndvi.py"
    ),

    (
        "Green Cover",
        "Satellite_1/greencover.py"
    ),

    (
        "Built-up Area",
        "Satellite_1/builtup.py"
    ),

    (
        "Flood Risk",
        "Satellite_1/flood.py"
    ),

    (
        "Heatmap",
        "Satellite_1/heatmap.py"
    ),

    (
        "Land Use / LULC",
        "Satellite_1/landuse.py"
    ),
]

for title, script in satellite_scripts:

    success = run_script(title, script)

    if not success:
        print(
            f"\nWARNING: {title} failed."
            "\nContinuing with remaining pipeline..."
        )


# ============================================================
# STEP 3
# CLEAN ALL DATA
# ============================================================

print("\n" + "=" * 80)
print("STEP 3 - CLEANING ALL UPDATED DATA")
print("=" * 80)

clean_success = run_script(
    "Complete Data Cleaning",
    "Satellite_1/data_cleaning.py"
)

if not clean_success:

    print("\nWARNING:")
    print("Data cleaning failed.")
    print("Feature engineering will NOT be executed.")

else:

    # ========================================================
    # STEP 4
    # FEATURE ENGINEERING
    # ========================================================

    print("\n" + "=" * 80)
    print("STEP 4 - FEATURE ENGINEERING")
    print("=" * 80)

    feature_success = run_script(
        "Feature Dataset",
        "feature_engineering.py"
    )

    # ========================================================
    # STEP 5
    # ML MODEL
    # ========================================================

    print("\n" + "=" * 80)
    print("STEP 5 - ML MODEL")
    print("=" * 80)

    ml_success = run_script(
        "Urban Development ML Model",
        "scripts/ml_model.py"
    )

    # ========================================================
    # STEP 6
    # PREDICTION
    # ========================================================

    print("\n" + "=" * 80)
    print("STEP 6 - PREDICTION")
    print("=" * 80)

    prediction_success = run_script(
        "Urban Growth Prediction",
        "scripts/predict.py"
    )


# ============================================================
# STEP 7
# CHECK POWER BI FILES
# ============================================================

print("\n" + "=" * 80)
print("CHECKING POWER BI DATA FILES")
print("=" * 80)


powerbi_files = [

    "Nagpur_Buildings_Clean.csv",
    "Nagpur_Roads_Clean.csv",
    "Nagpur_Hospitals_Clean.csv",
    "Nagpur_Schools_Clean.csv",
    "Nagpur_Parks_Clean.csv",
    "Nagpur_WaterBodies_Clean.csv",

    "Nagpur_BuiltUp_Spatial_Clean.csv",
    "Nagpur_GreenCover_Spatial_Clean.csv",
    "Nagpur_Sentinel2_NDVI_Spatial_Clean.csv",

    "Nagpur_FloodRisk_Spatial_Clean.csv",
    "Nagpur_Heatmap_Spatial_Clean.csv",

    "Nagpur_LULC_Clean.csv",

    "Nagpur_Feature_Dataset_Clean.csv",

    "Nagpur_BuiltUp_Summary_Clean.csv",
    "Nagpur_GreenCover_Summary_Clean.csv",
    "Nagpur_FloodRisk_Summary_Clean.csv",
    "Nagpur_Heatmap_Summary_Clean.csv",
    "Nagpur_LULC_Summary_Clean.csv",
    "Nagpur_Sentinel2_NDVI_Summary_Clean.csv",
]


available = 0
missing = 0

for filename in powerbi_files:

    path = os.path.join(
        PROCESSED_DIR,
        filename
    )

    if os.path.exists(path):

        size_mb = os.path.getsize(path) / (1024 * 1024)

        print(
            f"OK  : {filename}"
            f" ({size_mb:.2f} MB)"
        )

        available += 1

    else:

        print(
            f"MISS: {filename}"
        )

        missing += 1


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 80)
print("             GEOTWINAI UPDATE FINISHED")
print("=" * 80)

print("\nPower BI folder:")
print(PROCESSED_DIR)

print("\nPower BI files available:")
print(f"{available}/{len(powerbi_files)}")

print("\nMissing files:")
print(missing)

print("\nIMPORTANT:")
print("Power BI should use the *_Clean.csv files from:")
print(PROCESSED_DIR)

print("\nNext:")
print("Open Power BI Desktop")
print("Home -> Refresh")

print("\n" + "=" * 80)
print("              PIPELINE COMPLETED")
print("=" * 80)