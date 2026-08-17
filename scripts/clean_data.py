import os
import pandas as pd

# ============================================================
# GEOTWINAI - DATA CLEANING
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

INPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

PROCESSED_DIR = os.path.join(
    INPUT_DIR,
    "processed"
)

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# DATASETS
# ============================================================

DATASETS = [
    "Nagpur_Roads.csv",
    "Nagpur_Buildings.csv",
    "Nagpur_Schools.csv",
    "Nagpur_Hospitals.csv",
    "Nagpur_Parks.csv",
    "Nagpur_WaterBodies.csv"
]


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_column_names(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(":", "_")
        .str.replace("-", "_")
    )

    return df


# ============================================================
# CLEAN ONE DATASET
# ============================================================

def clean_dataset(filename):

    input_path = os.path.join(
        INPUT_DIR,
        filename
    )

    if not os.path.exists(input_path):

        print(
            f"\nWARNING: File not found -> {filename}"
        )

        return

    print("\n" + "-" * 60)
    print(f"Cleaning: {filename}")
    print("-" * 60)

    try:

        df = pd.read_csv(
            input_path,
            low_memory=False
        )

        print(
            f"Original records: {len(df)}"
        )

        # ----------------------------------------------------
        # 1. Clean column names
        # ----------------------------------------------------

        df = clean_column_names(df)

        # ----------------------------------------------------
        # 2. Remove completely empty columns
        # ----------------------------------------------------

        df = df.dropna(
            axis=1,
            how="all"
        )

        # ----------------------------------------------------
        # 3. Remove duplicate rows
        # ----------------------------------------------------

        df = df.drop_duplicates()

        # ----------------------------------------------------
        # 4. Clean Latitude / Longitude
        # ----------------------------------------------------

        if "Latitude" in df.columns:

            df["Latitude"] = pd.to_numeric(
                df["Latitude"],
                errors="coerce"
            )

        if "Longitude" in df.columns:

            df["Longitude"] = pd.to_numeric(
                df["Longitude"],
                errors="coerce"
            )

        # ----------------------------------------------------
        # 5. Remove invalid coordinates
        # ----------------------------------------------------

        if (
            "Latitude" in df.columns
            and "Longitude" in df.columns
        ):

            df = df[
                df["Latitude"].between(20, 22)
                &
                df["Longitude"].between(78, 80)
            ]

        # ----------------------------------------------------
        # 6. Clean Region
        # ----------------------------------------------------

        if "Region" in df.columns:

            df["Region"] = (
                df["Region"]
                .astype(str)
                .str.strip()
                .str.title()
            )

            valid_regions = [
                "Central",
                "North",
                "South",
                "East",
                "West"
            ]

            df.loc[
                ~df["Region"].isin(valid_regions),
                "Region"
            ] = "Unknown"

        # ----------------------------------------------------
        # 7. Remove rows where all useful data is empty
        # ----------------------------------------------------

        df = df.dropna(
            how="all"
        )

        # ----------------------------------------------------
        # 8. Reset index
        # ----------------------------------------------------

        df = df.reset_index(
            drop=True
        )

        # ----------------------------------------------------
        # 9. Save cleaned dataset
        # ----------------------------------------------------

        output_filename = (
            filename
            .replace(".csv", "_Clean.csv")
        )

        output_path = os.path.join(
            PROCESSED_DIR,
            output_filename
        )

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"Cleaned records: {len(df)}"
        )

        print(
            f"Saved: {output_path}"
        )

        # ----------------------------------------------------
        # 10. Region summary
        # ----------------------------------------------------

        if "Region" in df.columns:

            print("\nRegion distribution:")

            print(
                df["Region"]
                .value_counts()
            )

    except Exception as e:

        print(
            f"\nERROR while cleaning {filename}:"
        )

        print(e)


# ============================================================
# MAIN
# ============================================================

print("\n")
print("=" * 60)
print("        GEOTWINAI DATA CLEANING")
print("=" * 60)

print(
    f"\nInput folder:\n{INPUT_DIR}"
)

print(
    f"\nProcessed folder:\n{PROCESSED_DIR}"
)


for dataset in DATASETS:

    clean_dataset(dataset)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n")
print("=" * 60)
print("       DATA CLEANING COMPLETED")
print("=" * 60)

print("\nCleaned files are available in:")

print(PROCESSED_DIR)

print("\nNext step:")
print("Feature Engineering")