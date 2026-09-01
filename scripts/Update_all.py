import os
import sys
import subprocess
import shutil
from datetime import datetime

import pandas as pd


# ============================================================
# GEOTWINAI - COMPLETE AUTO UPDATE PIPELINE
#
# FEATURES:
# 1. OSM update
# 2. Sentinel-2 NDVI
# 3. Green Cover
# 4. Built-up
# 5. Flood Risk
# 6. Heatmap
# 7. LULC
# 8. Data Cleaning
# 9. Feature Engineering
# 10. ML Model
# 11. Prediction
# 12. Historical data preservation
# 13. Same Update_Date for every file in one run
# 14. Power BI ready historical CSV files
#
# ============================================================


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PYTHON = sys.executable


# ============================================================
# 2. OUTPUT DIRECTORIES
# ============================================================

OUTPUT_DIR = os.path.join(
    PROJECT_DIR,
    "output"
)

PROCESSED_DIR = os.path.join(
    OUTPUT_DIR,
    "processed"
)

HISTORY_DIR = os.path.join(
    OUTPUT_DIR,
    "history"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    PROCESSED_DIR,
    exist_ok=True
)

os.makedirs(
    HISTORY_DIR,
    exist_ok=True
)


# ============================================================
# 3. CURRENT RUN DATE
# ============================================================

RUN_DATE = datetime.now().strftime(
    "%Y-%m-%d"
)

RUN_TIMESTAMP = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# ============================================================
# 4. HEADER
# ============================================================

print()
print("=" * 90)
print("                 GEOTWINAI AUTO UPDATE")
print("                 NAGPUR DIGITAL TWIN")
print("=" * 90)

print()
print("PROJECT:")
print(PROJECT_DIR)

print()
print("CURRENT UPDATE DATE:")
print(RUN_DATE)

print()
print("CURRENT UPDATE TIME:")
print(RUN_TIMESTAMP)

print()
print("HISTORY FOLDER:")
print(HISTORY_DIR)

print()
print("=" * 90)


# ============================================================
# 5. RUN PYTHON SCRIPT
# ============================================================

def run_script(title, script_path):

    print()
    print("=" * 90)
    print(f"RUNNING: {title}")
    print("=" * 90)

    full_path = os.path.join(
        PROJECT_DIR,
        script_path
    )

    if not os.path.exists(full_path):

        print()
        print("❌ FILE NOT FOUND")
        print(full_path)

        return False

    try:

        result = subprocess.run(
            [
                PYTHON,
                full_path
            ],
            cwd=PROJECT_DIR
        )

    except Exception as e:

        print()
        print("❌ ERROR")
        print(e)

        return False

    if result.returncode == 0:

        print()
        print(f"✅ SUCCESS: {title}")

        return True

    print()
    print(f"❌ FAILED: {title}")

    print(
        f"Return Code: {result.returncode}"
    )

    return False


# ============================================================
# 6. FIND ALL CLEAN CSV FILES
# ============================================================

def find_clean_files():

    files_found = []

    if not os.path.exists(
        PROCESSED_DIR
    ):
        return files_found

    for root, dirs, files in os.walk(
        PROCESSED_DIR
    ):

        for filename in files:

            if not filename.lower().endswith(
                ".csv"
            ):
                continue

            if "_Clean" not in filename:
                continue

            full_path = os.path.join(
                root,
                filename
            )

            files_found.append(
                full_path
            )

    return sorted(
        list(
            set(files_found)
        )
    )


# ============================================================
# 7. SAVE CURRENT CLEAN FILE INTO HISTORY
# ============================================================

def update_history():

    print()
    print("=" * 90)
    print("SAVING CURRENT DATA INTO HISTORY")
    print("=" * 90)

    clean_files = find_clean_files()

    if not clean_files:

        print()
        print(
            "❌ No *_Clean.csv files found."
        )

        return False

    print()
    print(
        f"Clean files found: {len(clean_files)}"
    )

    successful = 0
    failed = 0

    for source_path in clean_files:

        filename = os.path.basename(
            source_path
        )

        history_path = os.path.join(
            HISTORY_DIR,
            filename
        )

        print()
        print("-" * 80)
        print(
            f"Processing: {filename}"
        )

        try:

            # ------------------------------------------------
            # CURRENT CLEAN DATA
            # ------------------------------------------------

            current_df = pd.read_csv(
                source_path,
                low_memory=False
            )

            if current_df.empty:

                print(
                    "⚠️ File is empty. Skipping."
                )

                continue


            # =================================================
            # ADD COMMON SNAPSHOT DATE
            # =================================================

            current_df["Date"] = RUN_DATE

            current_df["Update_Date"] = RUN_DATE

            current_df["Update_Timestamp"] = (
                RUN_TIMESTAMP
            )


            # =================================================
            # READ EXISTING HISTORY
            # =================================================

            if os.path.exists(
                history_path
            ):

                history_df = pd.read_csv(
                    history_path,
                    low_memory=False
                )

            else:

                history_df = pd.DataFrame()


            # =================================================
            # REMOVE OLD Date COLUMN ONLY FROM CURRENT DATA
            # =================================================
            #
            # We intentionally DO NOT modify:
            #
            # Scene_Date
            # Before_Date
            # After_Date
            # Acquisition_Date
            #
            # Those can represent actual satellite dates.
            #
            # =================================================


            # =================================================
            # APPEND CURRENT RUN
            # =================================================

            combined_df = pd.concat(
                [
                    history_df,
                    current_df
                ],
                ignore_index=True
            )


            # =================================================
            # REMOVE EXACT DUPLICATES
            # =================================================

            combined_df = (
                combined_df
                .drop_duplicates()
                .reset_index(drop=True)
            )


            # =================================================
            # SAVE HISTORY
            # =================================================

            combined_df.to_csv(
                history_path,
                index=False
            )


            print(
                f"✅ History updated"
            )

            print(
                f"Previous + New rows: "
                f"{len(combined_df)}"
            )

            print(
                f"Current snapshot date: "
                f"{RUN_DATE}"
            )

            successful += 1

        except Exception as e:

            print()
            print(
                f"❌ FAILED: {filename}"
            )

            print(
                f"ERROR: {e}"
            )

            failed += 1


    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 90)
    print("HISTORY UPDATE COMPLETED")
    print("=" * 90)

    print()
    print(
        f"Total files: {len(clean_files)}"
    )

    print(
        f"Successful: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print()
    print(
        f"Current Date: {RUN_DATE}"
    )

    return failed == 0


# ============================================================
# 8. STEP 1 - OSM
# ============================================================

print()
print("=" * 90)
print("STEP 1 - OSM DATA")
print("=" * 90)


osm_success = run_script(
    "Buildings / Roads / Hospitals / Schools / Parks / WaterBodies",
    "main.py"
)


# ============================================================
# 9. STEP 2 - SATELLITE
# ============================================================

print()
print("=" * 90)
print("STEP 2 - SATELLITE DATA")
print("=" * 90)


satellite_scripts = [

    # NDVI
    (
        "Sentinel-2 NDVI",
        "Satellite_1/ndvi.py"
    ),

    # Green Cover
    (
        "Green Cover",
        "Satellite_1/greencover.py"
    ),

    # Built-up
    (
        "Built-up Area",
        "Satellite_1/builtup.py"
    ),

    # Flood Risk
    (
        "Flood Risk",
        "Satellite_1/flood.py"
    ),

    # Heatmap
    (
        "Heatmap",
        "Satellite_1/heatmap.py"
    ),

    # LULC
    (
        "Land Use / LULC",
        "Satellite_1/landuse.py"
    )

]


satellite_success = 0
satellite_failed = 0


for title, script in satellite_scripts:

    result = run_script(
        title,
        script
    )

    if result:

        satellite_success += 1

    else:

        satellite_failed += 1

        print()
        print(
            f"⚠️ {title} failed."
        )

        print(
            "Continuing..."
        )


# ============================================================
# 10. STEP 3 - DATA CLEANING
# ============================================================

print()
print("=" * 90)
print("STEP 3 - DATA CLEANING")
print("=" * 90)


clean_success = run_script(
    "Complete Data Cleaning",
    "scripts/clean_data.py"
)


# ============================================================
# 11. STEP 4 - FEATURE ENGINEERING
# ============================================================

feature_success = False


if clean_success:

    print()
    print("=" * 90)
    print("STEP 4 - FEATURE ENGINEERING")
    print("=" * 90)

    feature_success = run_script(
        "Feature Engineering",
        "feature_engineering.py"
    )

else:

    print()
    print(
        "⚠️ Feature Engineering skipped."
    )


# ============================================================
# 12. STEP 5 - ML MODEL
# ============================================================

ml_success = False


if feature_success:

    print()
    print("=" * 90)
    print("STEP 5 - MACHINE LEARNING MODEL")
    print("=" * 90)

    ml_success = run_script(
        "Urban Development ML Model",
        "scripts/ml_model.py"
    )

else:

    print()
    print(
        "⚠️ ML Model skipped."
    )


# ============================================================
# 13. STEP 6 - PREDICTION
# ============================================================

prediction_success = False


if ml_success:

    print()
    print("=" * 90)
    print("STEP 6 - PREDICTION")
    print("=" * 90)

    prediction_success = run_script(
        "Urban Growth Prediction",
        "scripts/predict.py"
    )

else:

    print()
    print(
        "⚠️ Prediction skipped."
    )


# ============================================================
# 14. STEP 7 - SAVE EVERYTHING TO HISTORY
# ============================================================

print()
print("=" * 90)
print("STEP 7 - HISTORICAL DATA UPDATE")
print("=" * 90)


history_success = (
    update_history()
)


# ============================================================
# 15. VERIFY HISTORY
# ============================================================

print()
print("=" * 90)
print("STEP 8 - VERIFYING HISTORY DATA")
print("=" * 90)


history_files = []


if os.path.exists(
    HISTORY_DIR
):

    for filename in os.listdir(
        HISTORY_DIR
    ):

        if (
            filename.endswith(".csv")
            and
            "_Clean" in filename
        ):

            history_files.append(
                filename
            )


print()
print(
    f"Historical Clean Files: "
    f"{len(history_files)}"
)


# ============================================================
# 16. CHECK CURRENT DATE EXISTS
# ============================================================

date_verified = 0
date_failed = 0


for filename in sorted(
    history_files
):

    path = os.path.join(
        HISTORY_DIR,
        filename
    )

    try:

        df = pd.read_csv(
            path,
            low_memory=False
        )

        if "Update_Date" not in df.columns:

            print(
                f"❌ Update_Date missing: "
                f"{filename}"
            )

            date_failed += 1

            continue


        current_rows = (
            df[
                df["Update_Date"]
                .astype(str)
                ==
                RUN_DATE
            ]
        )


        if len(current_rows) > 0:

            print(
                f"✅ DATE OK: "
                f"{filename}"
            )

            date_verified += 1

        else:

            print(
                f"⚠️ No rows for today: "
                f"{filename}"
            )

            date_failed += 1


    except Exception as e:

        print(
            f"❌ Verification failed: "
            f"{filename}"
        )

        print(e)

        date_failed += 1


# ============================================================
# 17. FINAL REPORT
# ============================================================

print()
print("=" * 90)
print("                  GEOTWINAI UPDATE COMPLETE")
print("=" * 90)

print()
print(
    f"Current Run Date       : {RUN_DATE}"
)

print(
    f"Current Run Time       : {RUN_TIMESTAMP}"
)

print()
print(
    f"Satellite Successful   : "
    f"{satellite_success}"
)

print(
    f"Satellite Failed      : "
    f"{satellite_failed}"
)

print()
print(
    f"History Files          : "
    f"{len(history_files)}"
)

print(
    f"Date Verified          : "
    f"{date_verified}"
)

print(
    f"Date Verification Fail : "
    f"{date_failed}"
)

print()
print("HISTORY FOLDER:")
print(HISTORY_DIR)


# ============================================================
# FINAL STATUS
# ============================================================

if (
    clean_success
    and
    history_success
    and
    date_failed == 0
):

    print()
    print("=" * 90)
    print("✅ SUCCESS")
    print("=" * 90)

    print()
    print(
        "New data has been added to historical files."
    )

    print()
    print(
        f"Snapshot Date = {RUN_DATE}"
    )

else:

    print()
    print("=" * 90)
    print("⚠️ COMPLETED WITH SOME ISSUES")
    print("=" * 90)


# ============================================================
# POWER BI
# ============================================================

print()
print("=" * 90)
print("POWER BI")
print("=" * 90)

print()
print(
    "Power BI should use CSV files from:"
)

print(
    HISTORY_DIR
)

print()
print(
    "After running this command:"
)

print(
    "Power BI Desktop → Home → Refresh"
)

print()
print("=" * 90)
print("                    DONE")
print("=" * 90)
