import os
import re
import pandas as pd
import numpy as np


# ============================================================
# GEOTWINAI - COMPLETE DATA CLEANING PIPELINE
# ============================================================
#
# This script automatically cleans ALL CSV files present inside:
#
#   output/
#   output/satellite/
#   output/processed/
#   data/
#
# It creates cleaned files with:
#
#   *_Clean.csv
#
# It does NOT modify original CSV files.
#
# PNG / JPG / TIF / PKL / PY files are ignored.
#
# ============================================================


# ============================================================
# 1. PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

PROCESSED_DIR = os.path.join(
    OUTPUT_DIR,
    "processed"
)

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# 2. REPORT STORAGE
# ============================================================

REPORT_ROWS = []


# ============================================================
# 3. PRINT HEADER
# ============================================================

print("=" * 75)
print("              GEOTWINAI - COMPLETE DATA CLEANING")
print("=" * 75)

print()
print(f"Project Directory : {BASE_DIR}")
print(f"Output Directory  : {OUTPUT_DIR}")
print(f"Data Directory    : {DATA_DIR}")
print(f"Cleaned Directory : {PROCESSED_DIR}")
print()


# ============================================================
# 4. FIND ALL CSV FILES
# ============================================================

def find_csv_files():

    csv_files = []

    search_directories = [
        OUTPUT_DIR,
        DATA_DIR
    ]

    for directory in search_directories:

        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):

            # Ignore folders that should not be processed
            dirs[:] = [
                d for d in dirs
                if d not in [
                    "venv",
                    "__pycache__",
                    ".git"
                ]
            ]

            for file in files:

                if not file.lower().endswith(".csv"):
                    continue

                # Do not clean already-cleaned files
                if "_Clean" in file:
                    continue

                full_path = os.path.join(root, file)

                csv_files.append(full_path)

    return sorted(
        list(set(csv_files))
    )


# ============================================================
# 5. STANDARDIZE COLUMN NAMES
# ============================================================

def clean_column_name(column):

    column = str(column).strip()

    # Remove unwanted characters
    column = re.sub(
        r"[^A-Za-z0-9_]+",
        "_",
        column
    )

    # Remove repeated underscores
    column = re.sub(
        r"_+",
        "_",
        column
    )

    # Remove leading/trailing underscores
    column = column.strip("_")

    # Avoid empty column name
    if column == "":
        column = "Unnamed_Column"

    return column


def standardize_columns(df):

    new_columns = []

    used_names = {}

    for column in df.columns:

        new_name = clean_column_name(column)

        # Handle duplicate column names
        if new_name in used_names:

            used_names[new_name] += 1

            new_name = (
                f"{new_name}_{used_names[new_name]}"
            )

        else:

            used_names[new_name] = 0

        new_columns.append(new_name)

    df.columns = new_columns

    return df


# ============================================================
# 6. CLEAN STRING VALUES
# ============================================================

def clean_string_values(df):

    for column in df.columns:

        if (
            df[column].dtype == "object"
            or pd.api.types.is_string_dtype(
                df[column]
            )
        ):

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

            # Replace common missing-value strings
            df[column] = df[column].replace(
                [
                    "",
                    " ",
                    "NA",
                    "N/A",
                    "na",
                    "n/a",
                    "NULL",
                    "null",
                    "None",
                    "none",
                    "-",
                    "--",
                    "nan",
                    "NaN"
                ],
                pd.NA
            )

    return df


# ============================================================
# 7. CLEAN NUMERIC VALUES
# ============================================================

def clean_numeric_values(df):

    for column in df.columns:

        if df[column].dtype == "object":

            series = (
                df[column]
                .astype("string")
                .str.strip()
            )

            # Detect columns which are likely numeric
            numeric_test = pd.to_numeric(
                series,
                errors="coerce"
            )

            non_null_count = series.notna().sum()

            if non_null_count == 0:
                continue

            numeric_count = numeric_test.notna().sum()

            numeric_ratio = (
                numeric_count /
                non_null_count
            )

            # If > 80% values are numeric,
            # convert entire column to numeric.
            if numeric_ratio >= 0.80:

                df[column] = pd.to_numeric(
                    series,
                    errors="coerce"
                )

    return df


# ============================================================
# 8. CLEAN INFINITY VALUES
# ============================================================

def clean_infinite_values(df):

    numeric_columns = df.select_dtypes(
        include=[np.number]
    ).columns

    for column in numeric_columns:

        df[column] = df[column].replace(
            [
                np.inf,
                -np.inf
            ],
            np.nan
        )

    return df


# ============================================================
# 9. REMOVE COMPLETELY EMPTY COLUMNS
# ============================================================

def remove_empty_columns(df):

    before = len(df.columns)

    df = df.dropna(
        axis=1,
        how="all"
    )

    removed = before - len(df.columns)

    return df, removed


# ============================================================
# 10. REMOVE COMPLETELY EMPTY ROWS
# ============================================================

def remove_empty_rows(df):

    before = len(df)

    df = df.dropna(
        axis=0,
        how="all"
    )

    removed = before - len(df)

    return df, removed


# ============================================================
# 11. REMOVE DUPLICATE ROWS
# ============================================================

def remove_duplicates(df):

    before = len(df)

    df = df.drop_duplicates(
        keep="first"
    )

    removed = before - len(df)

    return df, removed


# ============================================================
# 12. CLEAN LATITUDE / LONGITUDE
# ============================================================

def clean_coordinates(df):

    for column in df.columns:

        lower = column.lower()

        # Latitude
        if lower in [
            "lat",
            "latitude",
            "y"
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            # Valid latitude:
            # -90 to +90
            invalid = (
                (df[column] < -90) |
                (df[column] > 90)
            )

            df.loc[
                invalid,
                column
            ] = np.nan

        # Longitude
        elif lower in [
            "lon",
            "lng",
            "longitude",
            "x"
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            # Valid longitude:
            # -180 to +180
            invalid = (
                (df[column] < -180) |
                (df[column] > 180)
            )

            df.loc[
                invalid,
                column
            ] = np.nan

    return df


# ============================================================
# 13. CLEAN NUMERIC COLUMN NAMES
# ============================================================

def clean_special_numeric_columns(df):

    numeric_keywords = [
        "population",
        "density",
        "area",
        "score",
        "index",
        "distance",
        "length",
        "width",
        "height",
        "count",
        "ndvi",
        "green",
        "water",
        "built",
        "flood",
        "heat",
        "temperature",
        "latitude",
        "longitude",
        "lat",
        "lon",
        "lng",
        "percent",
        "percentage"
    ]

    for column in df.columns:

        lower = column.lower()

        if any(
            keyword in lower
            for keyword in numeric_keywords
        ):

            if (
                df[column].dtype == "object"
                or pd.api.types.is_string_dtype(
                    df[column]
                )
            ):

                cleaned = (
                    df[column]
                    .astype("string")
                    .str.replace(
                        ",",
                        "",
                        regex=False
                    )
                    .str.replace(
                        "%",
                        "",
                        regex=False
                    )
                    .str.strip()
                )

                numeric = pd.to_numeric(
                    cleaned,
                    errors="coerce"
                )

                valid_ratio = (
                    numeric.notna().sum() /
                    max(
                        df[column].notna().sum(),
                        1
                    )
                )

                if valid_ratio >= 0.60:

                    df[column] = numeric

    return df


# ============================================================
# 14. ROUND FLOAT VALUES
# ============================================================

def round_numeric_values(df):

    numeric_columns = df.select_dtypes(
        include=[np.number]
    ).columns

    for column in numeric_columns:

        # Keep coordinates reasonably precise
        lower = column.lower()

        if lower in [
            "latitude",
            "longitude",
            "lat",
            "lon",
            "lng"
        ]:

            df[column] = df[column].round(6)

        else:

            df[column] = df[column].round(6)

    return df


# ============================================================
# 15. REMOVE DUPLICATE COLUMN NAMES
# ============================================================

def remove_duplicate_columns(df):

    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    return df


# ============================================================
# 16. SORT DATA IF ID COLUMN EXISTS
# ============================================================

def sort_data(df):

    possible_id_columns = [
        "id",
        "ID",
        "object_id",
        "Object_ID",
        "fid",
        "FID"
    ]

    for column in possible_id_columns:

        if column in df.columns:

            try:

                df = df.sort_values(
                    by=column,
                    kind="stable"
                )

                break

            except Exception:
                pass

    return df


# ============================================================
# 17. MAIN CLEANING FUNCTION
# ============================================================

def clean_dataframe(df, file_name):

    original_rows = len(df)
    original_columns = len(df.columns)

    # --------------------------------------------------------
    # Standardize columns
    # --------------------------------------------------------

    df = standardize_columns(df)

    # --------------------------------------------------------
    # Remove duplicate column names
    # --------------------------------------------------------

    df = remove_duplicate_columns(df)

    # --------------------------------------------------------
    # Clean string data
    # --------------------------------------------------------

    df = clean_string_values(df)

    # --------------------------------------------------------
    # Clean special numeric columns
    # --------------------------------------------------------

    df = clean_special_numeric_columns(df)

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    df = clean_numeric_values(df)

    # --------------------------------------------------------
    # Remove infinity
    # --------------------------------------------------------

    df = clean_infinite_values(df)

    # --------------------------------------------------------
    # Remove empty columns
    # --------------------------------------------------------

    df, empty_columns_removed = (
        remove_empty_columns(df)
    )

    # --------------------------------------------------------
    # Remove empty rows
    # --------------------------------------------------------

    df, empty_rows_removed = (
        remove_empty_rows(df)
    )

    # --------------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------------

    df, duplicate_rows_removed = (
        remove_duplicates(df)
    )

    # --------------------------------------------------------
    # Coordinate validation
    # --------------------------------------------------------

    df = clean_coordinates(df)

    # --------------------------------------------------------
    # Round numeric values
    # --------------------------------------------------------

    df = round_numeric_values(df)

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = sort_data(df)

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    final_rows = len(df)
    final_columns = len(df.columns)

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    REPORT_ROWS.append({

        "File_Name": file_name,

        "Original_Rows": original_rows,

        "Clean_Rows": final_rows,

        "Rows_Removed":
            original_rows - final_rows,

        "Original_Columns":
            original_columns,

        "Clean_Columns":
            final_columns,

        "Empty_Rows_Removed":
            empty_rows_removed,

        "Empty_Columns_Removed":
            empty_columns_removed,

        "Duplicate_Rows_Removed":
            duplicate_rows_removed,

        "Status": "SUCCESS"

    })

    return df


# ============================================================
# 18. GENERATE CLEAN FILE NAME
# ============================================================

def get_clean_filename(file_path):

    base_name = os.path.basename(
        file_path
    )

    name = os.path.splitext(
        base_name
    )[0]

    return f"{name}_Clean.csv"


# ============================================================
# 19. PROCESS ONE CSV FILE
# ============================================================

def process_csv(file_path):

    file_name = os.path.basename(
        file_path
    )

    print()
    print("-" * 75)
    print(f"Processing : {file_name}")
    print(f"Location   : {file_path}")

    try:

        # ----------------------------------------------------
        # Read CSV
        # ----------------------------------------------------

        df = pd.read_csv(
            file_path,
            low_memory=False
        )

        print(
            f"Original   : "
            f"{len(df)} rows x "
            f"{len(df.columns)} columns"
        )

        # ----------------------------------------------------
        # Clean
        # ----------------------------------------------------

        cleaned_df = clean_dataframe(
            df,
            file_name
        )

        # ----------------------------------------------------
        # Save ALL cleaned files to output/processed
        # ----------------------------------------------------

        clean_filename = (
            get_clean_filename(file_path)
        )

        output_path = os.path.join(
            PROCESSED_DIR,
            clean_filename
        )

        cleaned_df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"Cleaned    : "
            f"{len(cleaned_df)} rows x "
            f"{len(cleaned_df.columns)} columns"
        )

        print(
            f"Saved      : "
            f"{output_path}"
        )

        print("Status     : SUCCESS")

    except Exception as e:

        print(
            f"Status     : ERROR"
        )

        print(
            f"Error      : {e}"
        )

        REPORT_ROWS.append({

            "File_Name": file_name,

            "Original_Rows": 0,

            "Clean_Rows": 0,

            "Rows_Removed": 0,

            "Original_Columns": 0,

            "Clean_Columns": 0,

            "Empty_Rows_Removed": 0,

            "Empty_Columns_Removed": 0,

            "Duplicate_Rows_Removed": 0,

            "Status": f"ERROR: {e}"

        })


# ============================================================
# 20. SAVE CLEANING REPORT
# ============================================================

def save_report():

    if not REPORT_ROWS:

        print()
        print(
            "No cleaning report generated."
        )

        return

    report_df = pd.DataFrame(
        REPORT_ROWS
    )

    report_path = os.path.join(
        PROCESSED_DIR,
        "Data_Cleaning_Report.csv"
    )

    report_df.to_csv(
        report_path,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("=" * 75)
    print("CLEANING REPORT")
    print("=" * 75)

    print(
        report_df.to_string(
            index=False
        )
    )

    print()
    print(
        f"Report saved to:"
    )

    print(
        report_path
    )


# ============================================================
# 21. MAIN
# ============================================================

def main():

    csv_files = find_csv_files()

    print(
        f"CSV files found : {len(csv_files)}"
    )

    if len(csv_files) == 0:

        print()
        print(
            "No CSV files found."
        )

        print(
            "Please check output/ and data/ folders."
        )

        return

    print()
    print(
        "The following CSV files will be cleaned:"
    )

    for file in csv_files:

        print(
            f"  -> {os.path.basename(file)}"
        )

    # --------------------------------------------------------
    # Process every CSV
    # --------------------------------------------------------

    for file_path in csv_files:

        process_csv(
            file_path
        )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    save_report()

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print()
    print("=" * 75)
    print(
        "        DATA CLEANING COMPLETED SUCCESSFULLY"
    )
    print("=" * 75)

    print()
    print(
        "All cleaned datasets are available here:"
    )

    print(
        PROCESSED_DIR
    )

    print()
    print(
        "Original CSV files were NOT modified."
    )

    print(
        "Cleaned files were created separately."
    )

    print()
    print("=" * 75)


# ============================================================
# 22. RUN
# ============================================================

if __name__ == "__main__":
    main()