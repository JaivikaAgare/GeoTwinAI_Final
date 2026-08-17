import os
import pandas as pd

# ============================================================
# GEOTWINAI - FEATURE ENGINEERING
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROCESSED_DIR = os.path.join(
    BASE_DIR,
    "output",
    "processed"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Feature_Dataset.csv"
)

# ============================================================
# REGIONS
# ============================================================

REGIONS = [
    "Central",
    "North",
    "South",
    "East",
    "West"
]

# ============================================================
# DATASET FILES
# ============================================================

FILES = {
    "Buildings": "Nagpur_Buildings_Clean.csv",
    "Roads": "Nagpur_Roads_Clean.csv",
    "Schools": "Nagpur_Schools_Clean.csv",
    "Hospitals": "Nagpur_Hospitals_Clean.csv",
    "Parks": "Nagpur_Parks_Clean.csv",
    "WaterBodies": "Nagpur_WaterBodies_Clean.csv"
}


# ============================================================
# LOAD DATA
# ============================================================

def load_dataset(name, filename):

    path = os.path.join(
        PROCESSED_DIR,
        filename
    )

    if not os.path.exists(path):

        print(
            f"WARNING: {filename} not found"
        )

        return pd.DataFrame()

    try:

        df = pd.read_csv(
            path,
            low_memory=False
        )

        print(
            f"{name}: {len(df)} records loaded"
        )

        return df

    except Exception as e:

        print(
            f"ERROR loading {filename}: {e}"
        )

        return pd.DataFrame()


# ============================================================
# COUNT RECORDS BY REGION
# ============================================================

def region_count(df):

    result = {
        region: 0
        for region in REGIONS
    }

    if df.empty:
        return result

    if "Region" not in df.columns:
        return result

    counts = (
        df["Region"]
        .value_counts()
        .to_dict()
    )

    for region in REGIONS:

        result[region] = int(
            counts.get(region, 0)
        )

    return result


# ============================================================
# MAIN
# ============================================================

print("\n")
print("=" * 65)
print("          GEOTWINAI FEATURE ENGINEERING")
print("=" * 65)

print(
    f"\nReading cleaned data from:\n{PROCESSED_DIR}"
)


datasets = {}

for name, filename in FILES.items():

    datasets[name] = load_dataset(
        name,
        filename
    )


# ============================================================
# CREATE REGION TABLE
# ============================================================

rows = []

for region in REGIONS:

    row = {
        "Region": region
    }

    # --------------------------------------------------------
    # Building features
    # --------------------------------------------------------

    building_counts = region_count(
        datasets["Buildings"]
    )

    row["Building_Count"] = (
        building_counts[region]
    )

    # --------------------------------------------------------
    # Road features
    # --------------------------------------------------------

    road_counts = region_count(
        datasets["Roads"]
    )

    row["Road_Count"] = (
        road_counts[region]
    )

    # --------------------------------------------------------
    # School features
    # --------------------------------------------------------

    school_counts = region_count(
        datasets["Schools"]
    )

    row["School_Count"] = (
        school_counts[region]
    )

    # --------------------------------------------------------
    # Hospital features
    # --------------------------------------------------------

    hospital_counts = region_count(
        datasets["Hospitals"]
    )

    row["Hospital_Count"] = (
        hospital_counts[region]
    )

    # --------------------------------------------------------
    # Park features
    # --------------------------------------------------------

    park_counts = region_count(
        datasets["Parks"]
    )

    row["Park_Count"] = (
        park_counts[region]
    )

    # --------------------------------------------------------
    # Water body features
    # --------------------------------------------------------

    water_counts = region_count(
        datasets["WaterBodies"]
    )

    row["WaterBody_Count"] = (
        water_counts[region]
    )

    rows.append(row)


# ============================================================
# CREATE DATAFRAME
# ============================================================

feature_df = pd.DataFrame(
    rows
)


# ============================================================
# DERIVED FEATURES
# ============================================================

# Total infrastructure records

feature_df["Total_Infrastructure"] = (
    feature_df["Building_Count"]
    + feature_df["Road_Count"]
    + feature_df["School_Count"]
    + feature_df["Hospital_Count"]
    + feature_df["Park_Count"]
    + feature_df["WaterBody_Count"]
)


# ------------------------------------------------------------
# Basic infrastructure indicators
# ------------------------------------------------------------

feature_df["Healthcare_Index"] = (
    feature_df["Hospital_Count"]
)

feature_df["Education_Index"] = (
    feature_df["School_Count"]
)

feature_df["Green_Space_Index"] = (
    feature_df["Park_Count"]
)

feature_df["Water_Availability_Index"] = (
    feature_df["WaterBody_Count"]
)


# ------------------------------------------------------------
# Building-to-road relationship
# ------------------------------------------------------------

feature_df["Building_Road_Ratio"] = (
    feature_df["Building_Count"]
    /
    feature_df["Road_Count"].replace(0, 1)
)


# ------------------------------------------------------------
# Building-to-school relationship
# ------------------------------------------------------------

feature_df["Building_School_Ratio"] = (
    feature_df["Building_Count"]
    /
    feature_df["School_Count"].replace(0, 1)
)


# ------------------------------------------------------------
# Building-to-hospital relationship
# ------------------------------------------------------------

feature_df["Building_Hospital_Ratio"] = (
    feature_df["Building_Count"]
    /
    feature_df["Hospital_Count"].replace(0, 1)
)


# ============================================================
# NORMALIZED FEATURES
# ============================================================

def normalize_column(df, column):

    maximum = df[column].max()

    if maximum == 0:

        return 0

    return (
        df[column] / maximum
    ) * 100


feature_df["Building_Density_Index"] = (
    normalize_column(
        feature_df,
        "Building_Count"
    )
)

feature_df["Road_Density_Index"] = (
    normalize_column(
        feature_df,
        "Road_Count"
    )
)

feature_df["Healthcare_Index"] = (
    normalize_column(
        feature_df,
        "Hospital_Count"
    )
)

feature_df["Education_Index"] = (
    normalize_column(
        feature_df,
        "School_Count"
    )
)

feature_df["Green_Space_Index"] = (
    normalize_column(
        feature_df,
        "Park_Count"
    )
)

feature_df["Water_Availability_Index"] = (
    normalize_column(
        feature_df,
        "WaterBody_Count"
    )
)


# ============================================================
# ROUND NUMERIC VALUES
# ============================================================

numeric_columns = feature_df.select_dtypes(
    include=["number"]
).columns

feature_df[numeric_columns] = (
    feature_df[numeric_columns]
    .round(2)
)


# ============================================================
# SAVE
# ============================================================

feature_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 65)
print("             FEATURE DATASET")
print("=" * 65)

print(
    feature_df.to_string(
        index=False
    )
)

print("\n")
print(
    f"Saved:\n{OUTPUT_FILE}"
)

print("\nColumns created:")

for column in feature_df.columns:

    print(
        f"  - {column}"
    )


print("\n")
print("=" * 65)
print("       FEATURE ENGINEERING COMPLETED")
print("=" * 65)

print("\nNext step:")
print("Inspect the feature dataset before ML training.")