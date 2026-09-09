# ============================================================
# GEOTWINAI - FINAL STREAMLIT APPLICATION
# AI-Powered Digital Twin for Smart City Planning
# Study Area: Nagpur, Maharashtra
#
# Main concepts:
#   1. GeoTwinAI Overview
#   2. Five-Region City Analysis
#   3. Infrastructure Analysis
#   4. Environmental Analysis
#   5. Risk Analysis
#   6. Road / Traffic Infrastructure Analysis
#   7. AI Urban Priority Analysis
#   8. Interactive Digital Twin Map
#   9. Lightweight 3D City View
#  10. Regional Comparison
#  11. Project Report
#
# IMPORTANT:
# - Regional statistics are calculated from available files.
# - No regional values are hard-coded.
# - ML prediction is shown only when model/features can
#   be mapped safely.
# - No fake historical animation is generated.
# ============================================================

from pathlib import Path
import io
import re
import math
import base64
import warnings

import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GeoTwinAI | Nagpur Smart City",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = OUTPUT_DIR / "processed"
SATELLITE_DIR = OUTPUT_DIR / "satellite"
MODELS_DIR = BASE_DIR / "models"

MAP_FILE = OUTPUT_DIR / "Nagpur_Interactive_Map.html"

REGIONS = ["North", "South", "East", "West", "Central"]


# ============================================================
# NAGPUR STUDY AREA
# ============================================================

MIN_LON = 78.95
MIN_LAT = 21.05

MAX_LON = 79.20
MAX_LAT = 21.25

CENTRAL_LEFT = 79.05
CENTRAL_RIGHT = 79.13
CENTRAL_BOTTOM = 21.11
CENTRAL_TOP = 21.18


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 750;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .info-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 12px;
    }

    .small-note {
        font-size: 13px;
        opacity: 0.7;
    }

    .region-card {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        min-height: 130px;
    }

    .big-number {
        font-size: 30px;
        font-weight: 750;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_name(value):
    """Normalize a column/file name for matching."""
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def existing_files(folder, patterns):
    """Return matching files from a folder."""
    if not folder.exists():
        return []

    result = []

    for pattern in patterns:
        result.extend(folder.glob(pattern))

    return sorted(set(result))


def find_file(patterns, folders=None):
    """
    Search multiple project folders for the first matching file.
    """
    if folders is None:
        folders = [
            PROCESSED_DIR,
            SATELLITE_DIR,
            OUTPUT_DIR,
        ]

    for folder in folders:
        files = existing_files(folder, patterns)
        if files:
            return files[0]

    return None


def find_all_files(patterns, folders=None):
    """
    Search multiple folders and return all unique matches.
    """
    if folders is None:
        folders = [
            PROCESSED_DIR,
            SATELLITE_DIR,
            OUTPUT_DIR,
        ]

    result = []

    for folder in folders:
        result.extend(existing_files(folder, patterns))

    return sorted(set(result))


def safe_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def fmt_number(value, decimals=2):
    if value is None:
        return "—"

    try:
        if pd.isna(value):
            return "—"

        if abs(float(value)) >= 1000000:
            return f"{float(value):,.{decimals}f}"

        return f"{float(value):,.{decimals}f}"

    except Exception:
        return str(value)


def first_existing_column(df, aliases):
    """
    Find a column using normalized aliases.
    """
    if df is None or df.empty:
        return None

    normalized = {
        clean_name(col): col
        for col in df.columns
    }

    for alias in aliases:
        key = clean_name(alias)

        if key in normalized:
            return normalized[key]

    # Partial matching
    for col in df.columns:
        c = clean_name(col)

        for alias in aliases:
            a = clean_name(alias)

            if a in c or c in a:
                return col

    return None


# ============================================================
# REGION LOGIC
# ============================================================

def assign_region(lat, lon):
    """
    Assign each coordinate to one of the five GeoTwinAI regions.

    Central is checked first because it is the defined central
    study polygon.
    """

    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return None

    if not (
        MIN_LAT <= lat <= MAX_LAT
        and MIN_LON <= lon <= MAX_LON
    ):
        return None

    # Central region
    if (
        CENTRAL_LEFT <= lon <= CENTRAL_RIGHT
        and CENTRAL_BOTTOM <= lat <= CENTRAL_TOP
    ):
        return "Central"

    # North / South based on latitude
    if lat >= CENTRAL_TOP:
        return "North"

    if lat <= CENTRAL_BOTTOM:
        return "South"

    # Remaining middle area divided by longitude
    mid_lon = (MIN_LON + MAX_LON) / 2

    if lon < mid_lon:
        return "West"

    return "East"


def add_region_column(df):
    """
    Add GeoTwinAI five-region classification to a dataframe
    containing latitude and longitude.
    """

    if df is None or df.empty:
        return df

    existing_region = first_existing_column(
        df,
        [
            "region",
            "cluster",
            "zone",
            "area",
            "direction",
        ],
    )

    lat_col = first_existing_column(
        df,
        [
            "latitude",
            "lat",
            "y",
            "center_lat",
            "centroid_lat",
            "geometry_lat",
        ],
    )

    lon_col = first_existing_column(
        df,
        [
            "longitude",
            "lon",
            "lng",
            "long",
            "x",
            "center_lon",
            "centroid_lon",
            "geometry_lon",
        ],
    )

    result = df.copy()

    if existing_region:
        result["GeoTwinAI_Region"] = (
            result[existing_region]
            .astype(str)
            .str.strip()
            .str.title()
        )

        # Keep only the five official project regions.
        result.loc[
            ~result["GeoTwinAI_Region"].isin(REGIONS),
            "GeoTwinAI_Region"
        ] = None

        # Fill missing regions from coordinates if available.
        if lat_col and lon_col:
            missing = result["GeoTwinAI_Region"].isna()

            result.loc[missing, "GeoTwinAI_Region"] = [
                assign_region(lat, lon)
                for lat, lon in zip(
                    result.loc[missing, lat_col],
                    result.loc[missing, lon_col],
                )
            ]

        return result

    if lat_col and lon_col:
        result["GeoTwinAI_Region"] = [
            assign_region(lat, lon)
            for lat, lon in zip(
                result[lat_col],
                result[lon_col],
            )
        ]

    else:
        result["GeoTwinAI_Region"] = None

    return result


# ============================================================
# CSV LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def read_csv_safe(path, nrows=None):
    """
    Read CSV safely.

    For large files, callers should use chunk processing instead.
    """

    try:
        return pd.read_csv(
            path,
            nrows=nrows,
            low_memory=False,
        )

    except UnicodeDecodeError:
        try:
            return pd.read_csv(
                path,
                nrows=nrows,
                encoding="latin1",
                low_memory=False,
            )
        except Exception:
            return pd.DataFrame()

    except Exception:
        return pd.DataFrame()


def get_csv_columns(path):
    """
    Read only CSV header.
    """
    try:
        return pd.read_csv(
            path,
            nrows=0,
        ).columns.tolist()

    except Exception:
        return []


# ============================================================
# INFRASTRUCTURE FILE DISCOVERY
# ============================================================

INFRA_FILES = {
    "Buildings": [
        "*Buildings*Clean*.csv",
        "*Building*Clean*.csv",
        "*Buildings*.csv",
        "*Building*.csv",
    ],

    "Hospitals": [
        "*Hospitals*Clean*.csv",
        "*Hospital*Clean*.csv",
        "*Hospitals*.csv",
        "*Hospital*.csv",
    ],

    "Schools": [
        "*Schools*Clean*.csv",
        "*School*Clean*.csv",
        "*Schools*.csv",
        "*School*.csv",
    ],

    "Parks": [
        "*Parks*Clean*.csv",
        "*Park*Clean*.csv",
        "*Parks*.csv",
        "*Park*.csv",
    ],

    "Roads": [
        "*Roads*Clean*.csv",
        "*Road*Clean*.csv",
        "*Roads*.csv",
        "*Road*.csv",
    ],

    "Water Bodies": [
        "*WaterBodies*Clean*.csv",
        "*Water_Bodies*Clean*.csv",
        "*WaterBodies*.csv",
        "*Water*.csv",
    ],
}


@st.cache_data(show_spinner=False)
def discover_infrastructure_files():
    result = {}

    for category, patterns in INFRA_FILES.items():
        result[category] = find_file(patterns)

    return result


INFRA_PATHS = discover_infrastructure_files()


# ============================================================
# INFRASTRUCTURE DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_infrastructure(category):
    path = INFRA_PATHS.get(category)

    if path is None:
        return pd.DataFrame()

    df = read_csv_safe(path)

    if df.empty:
        return df

    return add_region_column(df)


def infrastructure_counts():
    """
    Count infrastructure features by five regions.
    """

    result = pd.DataFrame(
        index=REGIONS
    )

    for category in INFRA_FILES.keys():

        df = load_infrastructure(category)

        if df.empty or "GeoTwinAI_Region" not in df.columns:
            result[category] = 0
            continue

        counts = (
            df["GeoTwinAI_Region"]
            .value_counts()
            .reindex(REGIONS)
            .fillna(0)
            .astype(int)
        )

        result[category] = counts

    return result


# ============================================================
# SPATIAL SATELLITE DATA DISCOVERY
# ============================================================

ENV_FILE_PATTERNS = {

    "NDVI": [
        "*NDVI*Spatial*.csv",
        "*NDVI*.csv",
    ],

    "NDBI": [
        "*NDBI*Spatial*.csv",
        "*NDBI*.csv",
    ],

    "NDWI": [
        "*NDWI*Spatial*.csv",
        "*NDWI*.csv",
    ],

    "Green Cover": [
        "*Green*Cover*Spatial*.csv",
        "*Green*Cover*.csv",
    ],

    "LULC": [
        "*LULC*Spatial*.csv",
        "*LULC*.csv",
    ],

    "Flood Risk": [
        "*Flood*Spatial*.csv",
        "*Flood*Risk*.csv",
        "*Flood*.csv",
    ],

    "Urban Heat": [
        "*Heat*Spatial*.csv",
        "*Urban*Heat*.csv",
        "*Heat*.csv",
    ],

    "Carbon": [
        "*Carbon*Spatial*.csv",
        "*Carbon*.csv",
    ],
}


@st.cache_data(show_spinner=False)
def discover_environment_files():
    result = {}

    for name, patterns in ENV_FILE_PATTERNS.items():

        matches = find_all_files(
            patterns,
            folders=[
                SATELLITE_DIR,
                PROCESSED_DIR,
                OUTPUT_DIR,
            ],
        )

        result[name] = matches

    return result


ENV_PATHS = discover_environment_files()


# ============================================================
# ENVIRONMENT COLUMN DETECTION
# ============================================================

ENV_ALIASES = {

    "NDVI": [
        "ndvi",
        "mean_ndvi",
        "ndvi_mean",
        "value",
    ],

    "NDBI": [
        "ndbi",
        "mean_ndbi",
        "ndbi_mean",
        "value",
    ],

    "NDWI": [
        "ndwi",
        "mean_ndwi",
        "ndwi_mean",
        "value",
    ],

    "Green Cover": [
        "green_cover",
        "green_cover_percent",
        "green_percent",
        "green",
        "vegetation_percent",
        "percentage",
        "value",
    ],

    "Flood Risk": [
        "flood_risk",
        "flood",
        "risk",
        "change",
        "value",
    ],

    "Urban Heat": [
        "urban_heat",
        "heat",
        "lst",
        "temperature",
        "land_surface_temperature",
        "value",
    ],

    "Carbon": [
        "carbon",
        "carbon_stock",
        "value",
    ],
}


# ============================================================
# LARGE CSV SPATIAL AGGREGATION
# ============================================================

def detect_spatial_columns(columns):

    lat_col = first_existing_column(
        pd.DataFrame(columns=columns),
        [
            "latitude",
            "lat",
            "y",
            "center_lat",
            "centroid_lat",
            "geometry_lat",
        ],
    )

    lon_col = first_existing_column(
        pd.DataFrame(columns=columns),
        [
            "longitude",
            "lon",
            "lng",
            "long",
            "x",
            "center_lon",
            "centroid_lon",
            "geometry_lon",
        ],
    )

    return lat_col, lon_col


def choose_value_column(columns, indicator):

    fake_df = pd.DataFrame(columns=columns)

    candidates = ENV_ALIASES.get(
        indicator,
        ["value"],
    )

    col = first_existing_column(
        fake_df,
        candidates,
    )

    if col:
        return col

    # Try indicator name itself
    col = first_existing_column(
        fake_df,
        [indicator],
    )

    if col:
        return col

    # Last numeric-looking semantic candidate
    for c in columns:
        n = clean_name(c)

        if indicator.lower().replace(" ", "") in n:
            return c

    return None


def aggregate_spatial_csv(path, indicator, chunksize=100000):

    if path is None or not Path(path).exists():
        return {}

    columns = get_csv_columns(path)

    if not columns:
        return {}

    lat_col, lon_col = detect_spatial_columns(columns)

    value_col = choose_value_column(
        columns,
        indicator,
    )

    # If coordinates are unavailable, try a region column.
    region_col = first_existing_column(
        pd.DataFrame(columns=columns),
        [
            "region",
            "cluster",
            "zone",
        ],
    )

    # LULC may contain categorical classes rather than
    # a single numeric value.
    if indicator == "LULC":
        return aggregate_lulc(path, chunksize=chunksize)

    if not value_col:
        return {}

    required = []

    if lat_col:
        required.append(lat_col)

    if lon_col:
        required.append(lon_col)

    if region_col and region_col not in required:
        required.append(region_col)

    if value_col not in required:
        required.append(value_col)

    # Avoid accidental duplicate columns.
    required = list(dict.fromkeys(required))

    sums = {r: 0.0 for r in REGIONS}
    counts = {r: 0 for r in REGIONS}

    try:

        for chunk in pd.read_csv(
            path,
            usecols=required,
            chunksize=chunksize,
            low_memory=False,
        ):

            if region_col:

                regions = (
                    chunk[region_col]
                    .astype(str)
                    .str.strip()
                    .str.title()
                )

                valid_region = regions.isin(REGIONS)

            elif lat_col and lon_col:

                lat_values = pd.to_numeric(
                    chunk[lat_col],
                    errors="coerce",
                )

                lon_values = pd.to_numeric(
                    chunk[lon_col],
                    errors="coerce",
                )

                regions = [
                    assign_region(lat, lon)
                    for lat, lon in zip(
                        lat_values,
                        lon_values,
                    )
                ]

                regions = pd.Series(
                    regions,
                    index=chunk.index,
                )

                valid_region = regions.isin(REGIONS)

            else:
                continue

            values = pd.to_numeric(
                chunk[value_col],
                errors="coerce",
            )

            temp = pd.DataFrame(
                {
                    "region": regions,
                    "value": values,
                }
            )

            temp = temp[
                valid_region
                & temp["value"].notna()
            ]

            if temp.empty:
                continue

            grouped = (
                temp.groupby("region")["value"]
                .agg(["sum", "count"])
            )

            for region in REGIONS:

                if region in grouped.index:

                    sums[region] += float(
                        grouped.loc[region, "sum"]
                    )

                    counts[region] += int(
                        grouped.loc[region, "count"]
                    )

    except Exception:
        return {}

    result = {}

    for region in REGIONS:

        if counts[region] > 0:
            result[region] = (
                sums[region] / counts[region]
            )
        else:
            result[region] = np.nan

    return result


# ============================================================
# LULC AGGREGATION
# ============================================================

def aggregate_lulc(path, chunksize=100000):

    columns = get_csv_columns(path)

    if not columns:
        return {}

    lat_col, lon_col = detect_spatial_columns(columns)

    region_col = first_existing_column(
        pd.DataFrame(columns=columns),
        [
            "region",
            "cluster",
            "zone",
        ],
    )

    class_col = first_existing_column(
        pd.DataFrame(columns=columns),
        [
            "lulc",
            "land_cover",
            "landuse",
            "land_use",
            "class",
            "class_name",
            "label",
            "category",
        ],
    )

    if not class_col:
        return {}

    required = [class_col]

    if region_col:
        required.append(region_col)

    if lat_col:
        required.append(lat_col)

    if lon_col:
        required.append(lon_col)

    required = list(dict.fromkeys(required))

    region_class_counts = {
        region: {}
        for region in REGIONS
    }

    try:

        for chunk in pd.read_csv(
            path,
            usecols=required,
            chunksize=chunksize,
            low_memory=False,
        ):

            if region_col:

                regions = (
                    chunk[region_col]
                    .astype(str)
                    .str.strip()
                    .str.title()
                )

            elif lat_col and lon_col:

                lat_values = pd.to_numeric(
                    chunk[lat_col],
                    errors="coerce",
                )

                lon_values = pd.to_numeric(
                    chunk[lon_col],
                    errors="coerce",
                )

                regions = pd.Series(
                    [
                        assign_region(lat, lon)
                        for lat, lon in zip(
                            lat_values,
                            lon_values,
                        )
                    ],
                    index=chunk.index,
                )

            else:
                continue

            classes = (
                chunk[class_col]
                .astype(str)
                .str.strip()
            )

            temp = pd.DataFrame(
                {
                    "region": regions,
                    "class": classes,
                }
            )

            temp = temp[
                temp["region"].isin(REGIONS)
                & temp["class"].notna()
            ]

            for region in REGIONS:

                subset = temp[
                    temp["region"] == region
                ]

                if subset.empty:
                    continue

                counts = subset["class"].value_counts()

                for cls, count in counts.items():

                    region_class_counts[
                        region
                    ][cls] = (
                        region_class_counts[
                            region
                        ].get(cls, 0)
                        + int(count)
                    )

    except Exception:
        return {}

    return region_class_counts


# ============================================================
# ENVIRONMENT SUMMARY
# ============================================================

@st.cache_data(show_spinner=False)
def build_environment_summary():

    summary = pd.DataFrame(
        index=REGIONS
    )

    for indicator, paths in ENV_PATHS.items():

        if not paths:
            summary[indicator] = np.nan
            continue

        # Prefer a spatial CSV.
        path = paths[0]

        values = aggregate_spatial_csv(
            path,
            indicator,
        )

        summary[indicator] = [
            values.get(region, np.nan)
            for region in REGIONS
        ]

    return summary


ENV_SUMMARY = build_environment_summary()


# ============================================================
# COMBINED REGIONAL TABLE
# ============================================================

@st.cache_data(show_spinner=False)
def build_regional_table():

    infra = infrastructure_counts()

    table = pd.DataFrame(
        index=REGIONS
    )

    # Infrastructure
    for col in infra.columns:
        table[col] = infra[col]

    # Environment
    for col in ENV_SUMMARY.columns:
        table[col] = ENV_SUMMARY[col]

    return table.reset_index().rename(
        columns={"index": "Region"}
    )


REGIONAL_TABLE = build_regional_table()


# ============================================================
# MODEL DISCOVERY
# ============================================================

def find_model():

    if not MODELS_DIR.exists():
        return None

    patterns = [
        "*.pkl",
        "*.joblib",
    ]

    files = []

    for pattern in patterns:
        files.extend(MODELS_DIR.glob(pattern))

    # Also search project root.
    for pattern in patterns:
        files.extend(BASE_DIR.glob(pattern))

    files = sorted(
        set(files),
        key=lambda p: p.name.lower()
    )

    if not files:
        return None

    # Prefer urban/nagpur model names.
    preferred = [
        f for f in files
        if (
            "urban" in f.name.lower()
            or "nagpur" in f.name.lower()
            or "model" in f.name.lower()
        )
    ]

    if preferred:
        return preferred[0]

    return files[0]


MODEL_PATH = find_model()


@st.cache_resource(show_spinner=False)
def load_model(path_string):

    if not path_string:
        return None

    try:
        import joblib

        return joblib.load(path_string)

    except Exception:
        return None


MODEL = load_model(
    str(MODEL_PATH)
    if MODEL_PATH
    else None
)


# ============================================================
# MODEL FEATURE EXTRACTION
# ============================================================

def get_model_feature_names(model):

    if model is None:
        return None

    # Most sklearn estimators expose this.
    if hasattr(model, "feature_names_in_"):

        try:
            return [
                str(x)
                for x in model.feature_names_in_
            ]
        except Exception:
            pass

    # Pipeline may contain the actual estimator.
    if hasattr(model, "named_steps"):

        try:

            for _, step in model.named_steps.items():

                if hasattr(
                    step,
                    "feature_names_in_",
                ):

                    return [
                        str(x)
                        for x in step.feature_names_in_
                    ]

        except Exception:
            pass

    return None


def normalized_feature_mapping(regional_df):

    """
    Create a normalized lookup between common feature
    names and the regional dataframe columns.
    """

    mapping = {}

    for col in regional_df.columns:

        mapping[clean_name(col)] = col

    aliases = {

        "buildings":
            ["buildings", "building_count"],

        "hospitals":
            ["hospitals", "hospital_count"],

        "schools":
            ["schools", "school_count"],

        "parks":
            ["parks", "park_count"],

        "waterbodies":
            [
                "waterbodies",
                "water_bodies",
                "waterbody_count",
                "water_count",
            ],

        "roads":
            [
                "roads",
                "road_count",
                "road_network",
            ],

        "ndvi":
            ["ndvi"],

        "ndbi":
            ["ndbi"],

        "ndwi":
            ["ndwi"],

        "greencover":
            [
                "green_cover",
                "greencover",
            ],

        "floodrisk":
            [
                "flood_risk",
                "floodrisk",
            ],

        "urbanheat":
            [
                "urban_heat",
                "urbanheat",
                "heat",
            ],

        "carbon":
            ["carbon"],
    }

    result = {}

    for canonical, names in aliases.items():

        for name in names:

            key = clean_name(name)

            if key in mapping:
                result[canonical] = mapping[key]
                break

    return result


def prepare_model_input(region_name):

    if MODEL is None:
        return None, "No compatible model file was found."

    feature_names = get_model_feature_names(
        MODEL
    )

    if not feature_names:
        return (
            None,
            "The model was found, but its expected feature names "
            "could not be identified safely."
        )

    row = REGIONAL_TABLE[
        REGIONAL_TABLE["Region"] == region_name
    ]

    if row.empty:
        return None, "Selected region was not found."

    row = row.iloc[0]

    lookup = normalized_feature_mapping(
        REGIONAL_TABLE
    )

    values = []

    missing = []

    for feature in feature_names:

        key = clean_name(feature)

        if key in lookup:

            col = lookup[key]
            value = row[col]

            try:
                value = float(value)

            except Exception:
                value = np.nan

            values.append(value)

        else:
            missing.append(feature)
            values.append(np.nan)

    if missing:
        return (
            None,
            "Required model features are missing from "
            "the available project data: "
            + ", ".join(missing)
        )

    X = pd.DataFrame(
        [values],
        columns=feature_names,
    )

    if X.isna().any().any():
        missing_values = list(
            X.columns[
                X.isna().iloc[0]
            ]
        )

        return (
            None,
            "Some required model features do not have "
            "valid regional values: "
            + ", ".join(missing_values)
        )

    return X, None


def model_predict(region_name):

    X, error = prepare_model_input(
        region_name
    )

    if error:
        return None, error

    try:

        prediction = MODEL.predict(X)

        value = prediction[0]

        # Convert numpy scalar.
        try:
            value = value.item()
        except Exception:
            pass

        return value, None

    except Exception as e:

        return (
            None,
            "Model prediction could not be executed: "
            + str(e)
        )


def priority_label(value):

    if value is None:
        return "Unavailable"

    try:
        value = float(value)
    except Exception:
        return str(value)

    # If model is a regression model, we do NOT invent
    # arbitrary High/Medium/Low thresholds.
    return f"{value:.4f}"


# ============================================================
# MAP
# ============================================================

def display_existing_map():

    if not MAP_FILE.exists():

        st.warning(
            "Interactive map file was not found at:"
        )

        st.code(
            str(MAP_FILE)
        )

        st.info(
            "Run your map-generation script first. "
            "The Streamlit app will automatically display "
            "Nagpur_Interactive_Map.html when it exists."
        )

        return

    try:

        from streamlit.components.v1 import html

        map_html = MAP_FILE.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        html(
            map_html,
            height=720,
            scrolling=True,
        )

    except Exception as e:

        st.error(
            f"Unable to display the interactive map: {e}"
        )


# ============================================================
# 3D CITY VIEW
# ============================================================

def find_lat_lon(df):

    lat_col = first_existing_column(
        df,
        [
            "latitude",
            "lat",
            "y",
            "center_lat",
            "centroid_lat",
        ],
    )

    lon_col = first_existing_column(
        df,
        [
            "longitude",
            "lon",
            "lng",
            "long",
            "x",
            "center_lon",
            "centroid_lon",
        ],
    )

    return lat_col, lon_col


def create_3d_building_data(max_points=3500):

    df = load_infrastructure(
        "Buildings"
    )

    if df.empty:
        return pd.DataFrame()

    lat_col, lon_col = find_lat_lon(df)

    if not lat_col or not lon_col:
        return pd.DataFrame()

    temp = df[
        [lat_col, lon_col]
    ].copy()

    temp["lat"] = pd.to_numeric(
        temp[lat_col],
        errors="coerce",
    )

    temp["lon"] = pd.to_numeric(
        temp[lon_col],
        errors="coerce",
    )

    temp = temp.dropna(
        subset=["lat", "lon"]
    )

    temp = temp[
        temp["lat"].between(
            MIN_LAT,
            MAX_LAT,
        )
        & temp["lon"].between(
            MIN_LON,
            MAX_LON,
        )
    ]

    if temp.empty:
        return pd.DataFrame()

    # Detect actual building height if present.
    height_col = first_existing_column(
        df,
        [
            "height",
            "building_height",
            "height_m",
            "levels",
            "building_levels",
        ],
    )

    if height_col:

        temp["height"] = pd.to_numeric(
            df.loc[temp.index, height_col],
            errors="coerce",
        )

        # If "levels" was detected, convert levels
        # approximately to metres for visualization.
        if "level" in clean_name(height_col):
            temp["height"] = (
                temp["height"] * 3.0
            )

        temp["height"] = (
            temp["height"]
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(8.0)
            .clip(
                lower=3,
                upper=100,
            )
        )

        height_note = "Available height/level field used where possible."

    else:

        # IMPORTANT:
        # This is only a visualization extrusion.
        # It is NOT a measured building height.
        temp["height"] = 8.0

        height_note = (
            "No building-height field was available; "
            "8 m is used only as a visual extrusion."
        )

    temp["region"] = [
        assign_region(
            lat,
            lon,
        )
        for lat, lon in zip(
            temp["lat"],
            temp["lon"],
        )
    ]

    temp = temp[
        temp["region"].isin(REGIONS)
    ]

    if len(temp) > max_points:

        # Deterministic sampling.
        temp = temp.sample(
            n=max_points,
            random_state=42,
        )

    temp.attrs[
        "height_note"
    ] = height_note

    return temp[
        [
            "lat",
            "lon",
            "height",
            "region",
        ]
    ]


def display_3d_view():

    st.markdown(
        '<div class="section-title">🏙️ Lightweight 3D City View</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "This visualization displays building footprints as "
        "lightweight 3D extrusions so the browser does not have "
        "to load a very large 3D city model."
    )

    data = create_3d_building_data()

    if data.empty:

        st.warning(
            "Building latitude/longitude data could not be "
            "detected for the 3D view."
        )

        return

    try:

        import pydeck as pdk

        center_lat = data["lat"].mean()
        center_lon = data["lon"].mean()

        layer = pdk.Layer(
            "ColumnLayer",
            data=data,
            get_position="[lon, lat]",
            get_elevation="height",
            elevation_scale=1,
            radius=35,
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11.3,
            pitch=55,
            bearing=0,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": (
                    "<b>Region:</b> {region}<br>"
                    "<b>Height:</b> {height} m"
                )
            },
        )

        st.pydeck_chart(
            deck,
            use_container_width=True,
        )

        st.caption(
            data.attrs.get(
                "height_note",
                "",
            )
        )

    except ImportError:

        st.error(
            "PyDeck is not installed."
        )

        st.code(
            "pip install pydeck"
        )


# ============================================================
# CHART HELPERS
# ============================================================

def regional_bar_chart(
    df,
    column,
    title,
):

    if column not in df.columns:
        return

    chart_df = df[
        ["Region", column]
    ].copy()

    chart_df[column] = pd.to_numeric(
        chart_df[column],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=[column]
    )

    if chart_df.empty:
        st.info(
            f"No data available for {title}."
        )
        return

    chart_df = chart_df.set_index(
        "Region"
    )

    st.bar_chart(
        chart_df,
        use_container_width=True,
    )

    st.caption(title)


# ============================================================
# PROJECT REPORT TEXT
# ============================================================

def project_report_text():

    infra = infrastructure_counts()

    available_infra = [
        category
        for category in INFRA_FILES
        if INFRA_PATHS.get(category)
    ]

    available_env = [
        indicator
        for indicator in ENV_PATHS
        if ENV_PATHS[indicator]
    ]

    model_status = (
        "A model file was detected."
        if MODEL_PATH
        else
        "No model file was detected."
    )

    report = f"""
GEOTWINAI
AI-POWERED DIGITAL TWIN FOR SMART CITY PLANNING

Study Area:
Nagpur, Maharashtra

============================================================
1. ABSTRACT
============================================================

GeoTwinAI is a geospatial decision-support application designed
to combine infrastructure information, satellite-derived
environmental indicators, risk analysis and machine-learning
capabilities for smart-city planning.

The system organizes the Nagpur study area into five analytical
regions:

1. North
2. South
3. East
4. West
5. Central

The purpose is to understand how infrastructure, environmental
conditions and urban risks vary across the five regions.

============================================================
2. INTRODUCTION
============================================================

Cities contain large amounts of spatial information. Roads,
buildings, schools, hospitals, parks and water bodies exist at
different locations, while satellite imagery provides information
about vegetation, built-up surfaces, water/moisture and land cover.

GeoTwinAI brings these datasets into one analytical framework.

The system does not treat the map as only a visualization.
Instead, the map is connected to regional analysis, environmental
analysis, risk analysis and AI-supported decision making.

============================================================
3. PROBLEM STATEMENT
============================================================

Urban planning information is often distributed across different
datasets and systems.

A planner may need to separately examine:

- Buildings
- Roads
- Hospitals
- Schools
- Parks
- Water bodies
- Vegetation
- Built-up areas
- Water/moisture indicators
- Land use/land cover
- Heat
- Flood-related information

GeoTwinAI attempts to combine these spatial datasets so that
different regions of Nagpur can be compared using one platform.

============================================================
4. OBJECTIVES
============================================================

The major objectives are:

- Integrate infrastructure datasets.
- Integrate satellite-derived environmental indicators.
- Divide the study area into five analytical regions.
- Compare regional infrastructure availability.
- Analyse vegetation and built-up characteristics.
- Analyse water/moisture indicators.
- Analyse land-use/land-cover information.
- Include flood and urban-heat analysis where data are available.
- Provide AI/ML-based urban priority analysis where the trained
  model and required features are available.
- Provide an interactive GIS visualization.
- Provide a foundation for future dashboard and digital-twin
  development.

============================================================
5. FIVE-REGION ANALYSIS
============================================================

The application uses five project-defined analytical regions:

North
South
East
West
Central

These regions are used as the common unit for comparing
infrastructure, environmental and risk information.

IMPORTANT:
The five regions are analytical regions defined for this project.
They should not be interpreted as official administrative
boundaries.

============================================================
6. INFRASTRUCTURE ANALYSIS
============================================================

The application attempts to analyse:

- Buildings
- Hospitals
- Schools
- Parks
- Water Bodies
- Roads

Available infrastructure files in the current project:

{", ".join(available_infra) if available_infra else "No infrastructure CSV files detected."}

============================================================
7. ENVIRONMENTAL ANALYSIS
============================================================

The application searches for available spatial datasets for:

- NDVI
- NDBI
- NDWI
- Green Cover
- LULC
- Carbon

Available environmental/risk datasets detected:

{", ".join(available_env) if available_env else "No environmental CSV files detected."}

NDVI is used to understand vegetation characteristics.

NDBI is used to examine built-up characteristics.

NDWI is used to examine water/moisture-related characteristics.

Green Cover is used to understand vegetation coverage.

LULC is used to examine land-use/land-cover classes.

============================================================
8. RISK ANALYSIS
============================================================

Where the corresponding datasets are available, GeoTwinAI
presents:

- Urban Heat
- Flood Risk

The application does not create fake risk values when the
required spatial data are unavailable.

============================================================
9. ROAD ANALYSIS
============================================================

Road infrastructure is analysed separately because roads are
important for urban connectivity and planning.

The application can show available road counts and regional
distribution.

Real-time traffic congestion is not claimed unless real-time
traffic data are integrated into the project.

============================================================
10. AI / MACHINE LEARNING
============================================================

GeoTwinAI provides an AI analysis section that attempts to load
the trained model available in the project's models directory.

Current model status:

{model_status}

The model is only used for prediction when its expected feature
names can be matched to available project features.

The application does not fabricate an AI prediction when the
required model-feature mapping is unavailable.

============================================================
11. DIGITAL TWIN VISUALIZATION
============================================================

The application includes:

- Interactive GIS map
- Infrastructure layers
- Five-region analysis
- Environmental information
- Lightweight 3D building visualization

The 3D visualization is intended as a lightweight visual
representation of building footprints.

If actual building heights are unavailable, the application uses
a fixed visual extrusion and clearly labels it as visualization
rather than measured height.

============================================================
12. DATA PROCESSING WORKFLOW
============================================================

Data Collection
       |
       v
Data Cleaning
       |
       v
Geospatial Processing
       |
       +----------------------+
       |                      |
       v                      v
Infrastructure          Satellite Data
       |                      |
       |                 NDVI / NDBI
       |                 NDWI / LULC
       |                 Green Cover
       |                 Heat / Flood
       |                      |
       +----------+-----------+
                  |
                  v
          Five-Region Analysis
                  |
                  v
          Feature Engineering
                  |
                  v
              AI / ML
                  |
                  v
       Visualization & Dashboard
                  |
                  v
        Smart-City Decision Support

============================================================
13. TECHNOLOGIES
============================================================

Main technologies used by the project include:

Python
Pandas
NumPy
GeoPandas
Shapely
OSMnx
Folium
Streamlit
Scikit-learn
Joblib
Sentinel-2
Microsoft Planetary Computer
Remote sensing indices
GIS / spatial analysis

============================================================
14. APPLICATIONS
============================================================

Potential applications include:

- Infrastructure planning
- Regional comparison
- Urban development analysis
- Environmental monitoring
- Green-cover assessment
- Built-up area analysis
- Road planning
- Heat-risk assessment
- Flood-risk assessment
- Smart-city planning
- Decision support

============================================================
15. LIMITATIONS
============================================================

The quality of the results depends on the available datasets.

The current system should not be interpreted as a complete
real-time city digital twin.

Real-time IoT feeds, continuously updated city infrastructure,
complete time-series data and validated 3D building heights can
be integrated in future versions.

The five-region boundaries are project-defined analytical
boundaries and are not official administrative boundaries.

============================================================
16. FUTURE SCOPE
============================================================

Future development can include:

- Real-time IoT integration
- Live traffic data
- Real-time weather
- More detailed 3D buildings
- LiDAR integration
- UAV data
- Time-series satellite monitoring
- Change detection
- Predictive urban growth
- Advanced AI models
- Automated alerts
- Power BI dashboard
- Web GIS deployment
- Cloud deployment
- Scenario simulation

============================================================
17. CONCLUSION
============================================================

GeoTwinAI provides a unified framework for analysing Nagpur using
geospatial infrastructure information, remote sensing indicators,
risk information and AI-supported analysis.

Its main contribution is the integration of multiple spatial
datasets into a common five-region framework.

The system can therefore help answer questions such as:

- Which region has more infrastructure?
- Which region has comparatively less green cover?
- Which regions have higher built-up characteristics?
- How do environmental indicators vary across regions?
- Which regions require further investigation?
- How can AI support future urban planning?

============================================================

Generated by GeoTwinAI
Study Area: Nagpur, Maharashtra
"""


    return report.strip()


# ============================================================
# PDF REPORT
# ============================================================

def generate_pdf_report():

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            PageBreak,
        )

    except ImportError:
        return None

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    text = project_report_text()

    sections = text.split(
        "============================================================"
    )

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                story.append(
                    Spacer(
                        1,
                        5,
                    )
                )

                continue

            safe = (
                line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            if line.startswith(
                "GEOTWINAI"
            ):

                story.append(
                    Paragraph(
                        safe,
                        title_style,
                    )
                )

            elif re.match(
                r"^\d+\.",
                line,
            ):

                story.append(
                    Paragraph(
                        safe,
                        heading_style,
                    )
                )

            else:

                story.append(
                    Paragraph(
                        safe,
                        body_style,
                    )
                )

            story.append(
                Spacer(
                    1,
                    3,
                )
            )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 🌐 GeoTwinAI"
)

st.sidebar.caption(
    "AI-Powered Digital Twin for Smart City Planning"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Overview",
        "📍 Five-Region Analysis",
        "🏢 Infrastructure Analysis",
        "🌱 Environmental Analysis",
        "⚠️ Risk Analysis",
        "🛣️ Road Analysis",
        "🤖 AI Urban Priority",
        "🗺️ Interactive Digital Twin Map",
        "🏙️ 3D City View",
        "📊 Regional Comparison",
        "📄 Project Report",
    ],
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 📌 Study Area"
)

st.sidebar.write(
    "Nagpur, Maharashtra"
)

st.sidebar.markdown(
    "### 📍 Analytical Regions"
)

for region in REGIONS:
    st.sidebar.write(
        f"• {region}"
    )

st.sidebar.markdown("---")

st.sidebar.caption(
    "GeoTwinAI Project"
)


# ============================================================
# PAGE 1 - OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.markdown(
        '<div class="main-title">🌐 GeoTwinAI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "AI-Powered Digital Twin for Smart City Planning"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### 🏙️ What is GeoTwinAI?

        GeoTwinAI is a geospatial smart-city analysis platform
        that combines **infrastructure data, satellite-derived
        environmental information, risk analysis and AI/ML**
        within one system.

        Instead of looking at every dataset separately, GeoTwinAI
        brings them together and compares the **North, South,
        East, West and Central regions of Nagpur**.
        """
    )

    st.markdown("---")

    # Main metrics
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "📍 Study Area",
        "Nagpur",
    )

    c2.metric(
        "🗺️ Regions",
        "5",
    )

    c3.metric(
        "🏢 Infrastructure",
        str(len([
            x for x in INFRA_FILES
            if INFRA_PATHS.get(x)
        ])),
    )

    c4.metric(
        "🌱 Environmental",
        str(len([
            x for x in ENV_PATHS
            if ENV_PATHS[x]
        ])),
    )

    c5.metric(
        "🤖 AI Model",
        "Detected"
        if MODEL_PATH
        else "Not Found",
    )

    st.markdown("---")

    st.markdown(
        "## 🔄 How GeoTwinAI works"
    )

    st.markdown(
        """
        ```text
        Data Collection
               ↓
        Data Cleaning
               ↓
        Geospatial + Satellite Processing
               ↓
        ┌──────────────────────────────┐
        │      FIVE REGIONS            │
        │ North / South / East / West  │
        │          / Central           │
        └──────────────────────────────┘
               ↓
        Infrastructure + Environment + Risk
               ↓
        Feature Engineering
               ↓
        AI / ML Analysis
               ↓
        Interactive GIS + 3D Visualization
               ↓
        Smart-City Decision Support
        ```
        """
    )

    st.markdown("---")

    st.markdown(
        "## ⭐ Why is GeoTwinAI useful for OUR project?"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            ### 🏢 Infrastructure

            GeoTwinAI combines:

            - Buildings
            - Hospitals
            - Schools
            - Parks
            - Roads
            - Water Bodies
            """
        )

    with col2:

        st.markdown(
            """
            ### 🌱 Environment

            It combines satellite-derived:

            - NDVI
            - NDBI
            - NDWI
            - Green Cover
            - LULC
            """
        )

    with col3:

        st.markdown(
            """
            ### 🤖 Decision Support

            The combined information can support:

            - Regional comparison
            - Risk investigation
            - Urban priority analysis
            - Future planning
            """
        )

    st.markdown("---")

    st.markdown(
        "## 📍 Five regions of Nagpur"
    )

    cols = st.columns(5)

    for col, region in zip(
        cols,
        REGIONS,
    ):

        with col:

            st.markdown(
                f"""
                <div class="region-card">
                    <b>📍 {region}</b><br><br>
                    Regional infrastructure,
                    environmental and risk analysis.
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# PAGE 2 - FIVE REGION ANALYSIS
# ============================================================

elif page == "📍 Five-Region Analysis":

    st.markdown(
        "## 📍 Five-Region City Analysis"
    )

    st.write(
        "Select a region to examine its infrastructure, "
        "environmental indicators and available risk information."
    )

    selected_region = st.selectbox(
        "Select Region",
        REGIONS,
    )

    row = REGIONAL_TABLE[
        REGIONAL_TABLE["Region"]
        == selected_region
    ]

    if row.empty:

        st.error(
            "No regional record available."
        )

    else:

        row = row.iloc[0]

        st.markdown(
            f"### 📍 {selected_region} Region"
        )

        # Infrastructure
        st.markdown(
            "#### 🏢 Infrastructure"
        )

        infra_cols = [
            c for c in [
                "Buildings",
                "Hospitals",
                "Schools",
                "Parks",
                "Water Bodies",
                "Roads",
            ]
            if c in row.index
        ]

        cols = st.columns(
            max(1, len(infra_cols))
        )

        for col, name in zip(
            cols,
            infra_cols,
        ):

            with col:

                st.metric(
                    name,
                    fmt_number(
                        row[name],
                        0,
                    ),
                )

        # Environment
        st.markdown(
            "#### 🌱 Environment"
        )

        env_cols = [
            c for c in [
                "NDVI",
                "NDBI",
                "NDWI",
                "Green Cover",
                "LULC",
            ]
            if c in row.index
        ]

        cols = st.columns(
            max(1, len(env_cols))
        )

        for col, name in zip(
            cols,
            env_cols,
        ):

            with col:

                value = row[name]

                if name == "LULC":

                    st.metric(
                        name,
                        "Available"
                        if not pd.isna(value)
                        else "—",
                    )

                else:

                    st.metric(
                        name,
                        fmt_number(
                            value,
                            4,
                        ),
                    )

        # Risk
        st.markdown(
            "#### ⚠️ Risk"
        )

        risk_cols = [
            c for c in [
                "Urban Heat",
                "Flood Risk",
            ]
            if c in row.index
        ]

        cols = st.columns(
            max(1, len(risk_cols))
        )

        for col, name in zip(
            cols,
            risk_cols,
        ):

            with col:

                st.metric(
                    name,
                    fmt_number(
                        row[name],
                        3,
                    ),
                )

        st.markdown("---")

        st.markdown(
            "### 📋 Complete Regional Record"
        )

        st.dataframe(
            row.to_frame(
                name=selected_region
            ),
            use_container_width=True,
        )


# ============================================================
# PAGE 3 - INFRASTRUCTURE
# ============================================================

elif page == "🏢 Infrastructure Analysis":

    st.markdown(
        "## 🏢 Infrastructure Analysis"
    )

    st.write(
        "Infrastructure is analysed region-wise across the "
        "five GeoTwinAI regions."
    )

    infra = infrastructure_counts()

    st.dataframe(
        infra,
        use_container_width=True,
    )

    st.markdown(
        "### 📊 Regional Infrastructure Comparison"
    )

    selected_layer = st.selectbox(
        "Choose infrastructure layer",
        [
            c for c in infra.columns
        ],
    )

    regional_bar_chart(
        infra.reset_index().rename(
            columns={"index": "Region"}
        ),
        selected_layer,
        f"{selected_layer} by Region",
    )

    st.markdown("---")

    selected_infra = st.selectbox(
        "Explore dataset",
        list(INFRA_FILES.keys()),
    )

    df = load_infrastructure(
        selected_infra
    )

    if df.empty:

        st.warning(
            f"No dataset was found for {selected_infra}."
        )

    else:

        st.write(
            f"**Dataset:** {INFRA_PATHS[selected_infra].name}"
        )

        st.write(
            f"**Records:** {len(df):,}"
        )

        if "GeoTwinAI_Region" in df.columns:

            region_counts = (
                df["GeoTwinAI_Region"]
                .value_counts()
                .reindex(REGIONS)
                .fillna(0)
                .astype(int)
            )

            st.bar_chart(
                region_counts
            )

        st.dataframe(
            df.head(100),
            use_container_width=True,
        )


# ============================================================
# PAGE 4 - ENVIRONMENT
# ============================================================

elif page == "🌱 Environmental Analysis":

    st.markdown(
        "## 🌱 Environmental Analysis"
    )

    st.write(
        "Satellite-derived environmental indicators are "
        "aggregated into the five project regions."
    )

    available = [
        c for c in [
            "NDVI",
            "NDBI",
            "NDWI",
            "Green Cover",
            "LULC",
        ]
        if c in ENV_SUMMARY.columns
    ]

    if not available:

        st.warning(
            "No environmental spatial CSV could be detected."
        )

    else:

        selected = st.selectbox(
            "Select environmental indicator",
            available,
        )

        chart_df = pd.DataFrame(
            {
                "Region": REGIONS,
                selected: ENV_SUMMARY[
                    selected
                ].values,
            }
        )

        regional_bar_chart(
            chart_df,
            selected,
            f"{selected} comparison",
        )

        st.markdown(
            "### 📋 Environmental Regional Table"
        )

        display_df = pd.DataFrame(
            {
                "Region": REGIONS
            }
        )

        for indicator in available:

            display_df[indicator] = ENV_SUMMARY[
                indicator
            ].values

        st.dataframe(
            display_df,
            use_container_width=True,
        )

        st.markdown("---")

        if selected == "NDVI":

            st.info(
                "NDVI is used in the project as a vegetation "
                "indicator. Higher values generally represent "
                "stronger vegetation characteristics."
            )

        elif selected == "NDBI":

            st.info(
                "NDBI is used to examine built-up characteristics."
            )

        elif selected == "NDWI":

            st.info(
                "NDWI is used to examine water/moisture-related "
                "characteristics."
            )

        elif selected == "Green Cover":

            st.info(
                "Green Cover represents the vegetation coverage "
                "available in the processed dataset."
            )

        elif selected == "LULC":

            st.info(
                "LULC represents land-use/land-cover information "
                "available in the project dataset."
            )


# ============================================================
# PAGE 5 - RISK
# ============================================================

elif page == "⚠️ Risk Analysis":

    st.markdown(
        "## ⚠️ Risk Analysis"
    )

    st.write(
        "The application presents available urban-heat and "
        "flood-risk information by region."
    )

    risk_available = [
        c for c in [
            "Urban Heat",
            "Flood Risk",
        ]
        if c in ENV_SUMMARY.columns
    ]

    if not risk_available:

        st.warning(
            "No risk-analysis spatial CSV was detected."
        )

    else:

        selected = st.selectbox(
            "Select risk layer",
            risk_available,
        )

        chart_df = pd.DataFrame(
            {
                "Region": REGIONS,
                selected: ENV_SUMMARY[
                    selected
                ].values,
            }
        )

        regional_bar_chart(
            chart_df,
            selected,
            f"{selected} by region",
        )

        st.dataframe(
            chart_df,
            use_container_width=True,
        )

        if selected == "Urban Heat":

            st.info(
                "Urban heat values are displayed from the "
                "available processed project data."
            )

        if selected == "Flood Risk":

            st.info(
                "Flood-risk values are displayed from the "
                "available processed project data."
            )

        st.warning(
            "These results should be interpreted according to "
            "the methodology and limitations of the underlying "
            "remote-sensing/risk dataset."
        )


# ============================================================
# PAGE 6 - ROAD ANALYSIS
# ============================================================

elif page == "🛣️ Road Analysis":

    st.markdown(
        "## 🛣️ Road / Traffic Infrastructure Analysis"
    )

    roads = load_infrastructure(
        "Roads"
    )

    if roads.empty:

        st.warning(
            "Road dataset was not found."
        )

    else:

        st.metric(
            "Total Road Records",
            f"{len(roads):,}",
        )

        if "GeoTwinAI_Region" in roads.columns:

            regional_roads = (
                roads["GeoTwinAI_Region"]
                .value_counts()
                .reindex(REGIONS)
                .fillna(0)
                .astype(int)
            )

            st.markdown(
                "### Regional Road Distribution"
            )

            st.bar_chart(
                regional_roads
            )

            st.dataframe(
                regional_roads.rename(
                    "Road Records"
                ).to_frame(),
                use_container_width=True,
            )

        length_col = first_existing_column(
            roads,
            [
                "length",
                "road_length",
                "length_m",
                "meters",
                "distance",
            ],
        )

        if length_col:

            roads[length_col] = pd.to_numeric(
                roads[length_col],
                errors="coerce",
            )

            st.markdown(
                "### 📏 Road Length"
            )

            length_by_region = (
                roads.groupby(
                    "GeoTwinAI_Region"
                )[length_col]
                .sum()
                .reindex(REGIONS)
            )

            st.bar_chart(
                length_by_region
            )

        st.markdown("---")

        st.info(
            "The current application analyses road infrastructure. "
            "It does not claim real-time traffic congestion unless "
            "live traffic-volume data are connected."
        )

        st.dataframe(
            roads.head(100),
            use_container_width=True,
        )


# ============================================================
# PAGE 7 - AI
# ============================================================

elif page == "🤖 AI Urban Priority":

    st.markdown(
        "## 🤖 AI Urban Priority Analysis"
    )

    st.write(
        """
        The AI module uses the trained model available in the
        project when its required feature names can be safely
        matched to the regional GeoTwinAI dataset.
        """
    )

    if MODEL_PATH:

        st.success(
            f"Model detected: {MODEL_PATH.name}"
        )

    else:

        st.warning(
            "No .pkl or .joblib model was found in the models folder."
        )

    if MODEL is not None:

        feature_names = get_model_feature_names(
            MODEL
        )

        st.markdown(
            "### 🧠 Model Information"
        )

        if feature_names:

            st.write(
                "**Detected model features:**"
            )

            st.write(
                ", ".join(feature_names)
            )

        else:

            st.warning(
                "The model does not expose feature names. "
                "Prediction is therefore disabled rather than "
                "using an unsafe assumed feature order."
            )

    st.markdown("---")

    selected_region = st.selectbox(
        "Select region for AI analysis",
        REGIONS,
        key="ai_region",
    )

    prediction, error = model_predict(
        selected_region
    )

    if error:

        st.warning(
            error
        )

        st.info(
            """
            This is intentional. The application does not
            manufacture a High/Medium/Low result when the
            trained model cannot be matched to the available
            project features.
            """
        )

    else:

        st.success(
            "AI prediction successfully generated "
            "using the detected trained model."
        )

        st.metric(
            "Model Prediction",
            priority_label(
                prediction
            ),
        )

        st.markdown(
            "### 📊 Input Regional Data"
        )

        row = REGIONAL_TABLE[
            REGIONAL_TABLE["Region"]
            == selected_region
        ]

        st.dataframe(
            row,
            use_container_width=True,
        )

    st.markdown("---")

    st.markdown(
        "### 🔄 AI Workflow"
    )

    st.code(
        """
Regional Infrastructure
        +
Environmental Indicators
        +
Risk Indicators
        ↓
Feature Engineering
        ↓
Trained ML Model
        ↓
Regional Prediction
        ↓
Urban Planning Decision Support
        """,
        language="text",
    )


# ============================================================
# PAGE 8 - INTERACTIVE MAP
# ============================================================

elif page == "🗺️ Interactive Digital Twin Map":

    st.markdown(
        "## 🗺️ Interactive Digital Twin Map"
    )

    st.write(
        """
        The interactive map is the spatial visualization layer
        of GeoTwinAI. It connects infrastructure features with
        the five-region analytical framework.
        """
    )

    if MAP_FILE.exists():

        st.success(
            "Interactive Nagpur map detected."
        )

        display_existing_map()

        st.markdown("---")

        st.markdown(
            "### 📌 Recommended Map Layers"
        )

        cols = st.columns(3)

        with cols[0]:

            st.checkbox(
                "🏢 Buildings",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "🏥 Hospitals",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "🏫 Schools",
                value=True,
                disabled=True,
            )

        with cols[1]:

            st.checkbox(
                "🌳 Parks",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "💧 Water Bodies",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "🛣️ Roads",
                value=True,
                disabled=True,
            )

        with cols[2]:

            st.checkbox(
                "🌱 NDVI",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "🏙️ NDBI",
                value=True,
                disabled=True,
            )

            st.checkbox(
                "💧 NDWI",
                value=True,
                disabled=True,
            )

    else:

        display_existing_map()


# ============================================================
# PAGE 9 - 3D CITY
# ============================================================

elif page == "🏙️ 3D City View":

    display_3d_view()

    st.markdown("---")

    st.markdown(
        "### 💡 Important"
    )

    st.write(
        """
        This is a lightweight 3D visualization of building
        locations. It is not presented as a fully surveyed
        engineering-grade 3D city model.

        If actual LiDAR/UAV-derived building heights become
        available later, this module can be upgraded to use
        measured building elevations.
        """
    )


# ============================================================
# PAGE 10 - REGIONAL COMPARISON
# ============================================================

elif page == "📊 Regional Comparison":

    st.markdown(
        "## 📊 Regional Comparison"
    )

    st.write(
        "This is the main comparison dashboard of GeoTwinAI."
    )

    if REGIONAL_TABLE.empty:

        st.warning(
            "Regional data could not be generated."
        )

    else:

        st.markdown(
            "### 🏢 Infrastructure"
        )

        infra_cols = [
            c for c in [
                "Buildings",
                "Hospitals",
                "Schools",
                "Parks",
                "Water Bodies",
                "Roads",
            ]
            if c in REGIONAL_TABLE.columns
        ]

        if infra_cols:

            st.dataframe(
                REGIONAL_TABLE[
                    ["Region"] + infra_cols
                ],
                use_container_width=True,
            )

        st.markdown(
            "### 🌱 Environmental Indicators"
        )

        env_cols = [
            c for c in [
                "NDVI",
                "NDBI",
                "NDWI",
                "Green Cover",
            ]
            if c in REGIONAL_TABLE.columns
        ]

        if env_cols:

            st.dataframe(
                REGIONAL_TABLE[
                    ["Region"] + env_cols
                ],
                use_container_width=True,
            )

        st.markdown(
            "### ⚠️ Risk"
        )

        risk_cols = [
            c for c in [
                "Urban Heat",
                "Flood Risk",
            ]
            if c in REGIONAL_TABLE.columns
        ]

        if risk_cols:

            st.dataframe(
                REGIONAL_TABLE[
                    ["Region"] + risk_cols
                ],
                use_container_width=True,
            )

        st.markdown("---")

        st.markdown(
            "### 📈 Choose a metric to compare"
        )

        comparison_columns = [
            c for c in REGIONAL_TABLE.columns
            if c != "Region"
            and c != "LULC"
        ]

        if comparison_columns:

            metric = st.selectbox(
                "Metric",
                comparison_columns,
            )

            regional_bar_chart(
                REGIONAL_TABLE,
                metric,
                f"{metric} comparison across Nagpur regions",
            )

        st.markdown("---")

        st.markdown(
            "### 📥 Download Regional Analysis"
        )

        csv_data = REGIONAL_TABLE.to_csv(
            index=False
        ).encode(
            "utf-8"
        )

        st.download_button(
            "Download Regional CSV",
            data=csv_data,
            file_name="GeoTwinAI_Regional_Analysis.csv",
            mime="text/csv",
        )


# ============================================================
# PAGE 11 - PROJECT REPORT
# ============================================================

elif page == "📄 Project Report":

    st.markdown(
        "## 📄 GeoTwinAI Project Report"
    )

    st.write(
        """
        This section provides a project-report version of the
        GeoTwinAI system, including its purpose, methodology,
        datasets, analysis modules, limitations and future scope.
        """
    )

    st.markdown("---")

    st.markdown(
        "### 📑 Report Preview"
    )

    report_text = project_report_text()

    st.text_area(
        "Project Report",
        report_text,
        height=650,
    )

    st.markdown("---")

    st.markdown(
        "### 📥 Download Report"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📄 Download TXT Report",
            data=report_text.encode(
                "utf-8"
            ),
            file_name="GeoTwinAI_Project_Report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:

        pdf_bytes = generate_pdf_report()

        if pdf_bytes:

            st.download_button(
                "📕 Download PDF Report",
                data=pdf_bytes,
                file_name="GeoTwinAI_Project_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        else:

            st.warning(
                "Install reportlab to enable PDF generation."
            )

            st.code(
                "pip install reportlab"
            )

    st.markdown("---")

    st.markdown(
        "### 📊 Current Project Data Status"
    )

    status_rows = []

    for category, path in INFRA_PATHS.items():

        status_rows.append(
            {
                "Category": category,
                "Status":
                    "Available"
                    if path
                    else "Not Found",
                "File":
                    path.name
                    if path
                    else "—",
            }
        )

    for category, paths in ENV_PATHS.items():

        status_rows.append(
            {
                "Category": category,
                "Status":
                    "Available"
                    if paths
                    else "Not Found",
                "File":
                    paths[0].name
                    if paths
                    else "—",
            }
        )

    status_df = pd.DataFrame(
        status_rows
    )

    st.dataframe(
        status_df,
        use_container_width=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "GeoTwinAI • AI-Powered Digital Twin for Smart City Planning • "
    "Nagpur, Maharashtra"
)