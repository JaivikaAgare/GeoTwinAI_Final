# ============================================================
# GEOTWINAI
<<<<<<< HEAD
# PROFESSIONAL SMART CITY REPORT GENERATOR
=======
# PROFESSIONAL REPORT GENERATOR
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
#
# Project:
# AI-Powered Digital Twin for Smart Cities
#
# Study Area:
# Nagpur, Maharashtra
#
<<<<<<< HEAD
# Includes:
# Infrastructure
# Sentinel-2
# All Bands
# NDVI
# NDBI
# NDWI
# LULC
# Built-up Area
# Green Cover
# Flood Risk
# Heatmap
# Machine Learning
# Interactive GIS
# Power BI
#
# Output:
# output/reports/
# GeoTwinAI_Nagpur_Professional_Report.pdf
# ============================================================

import os
import glob
import warnings

=======
# Output:
# output/reports/GeoTwinAI_Nagpur_Professional_Report.pdf
# ============================================================

import os
import warnings

import numpy as np
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
<<<<<<< HEAD
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm

=======
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
<<<<<<< HEAD
    Image,
    KeepTogether
=======
    Image
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
)

warnings.filterwarnings("ignore")


# ============================================================
<<<<<<< HEAD
# 1. PATHS
=======
# 1. PROJECT PATHS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

<<<<<<< HEAD
OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)
=======
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

PROCESSED_DIR = os.path.join(
    OUTPUT_DIR,
    "processed"
)

SATELLITE_DIR = os.path.join(
    OUTPUT_DIR,
    "satellite"
)

REPORT_DIR = os.path.join(
    OUTPUT_DIR,
    "reports"
)

CHART_DIR = os.path.join(
    OUTPUT_DIR,
    "report_charts"
)

<<<<<<< HEAD
MAP_DIR = os.path.join(
    OUTPUT_DIR,
    "maps"
)


os.makedirs(
    REPORT_DIR,
    exist_ok=True
)

os.makedirs(
    CHART_DIR,
    exist_ok=True
)

=======
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "GeoTwinAI_Nagpur_Professional_Report.pdf"
)


# ============================================================
<<<<<<< HEAD
# 2. HELPERS
=======
# 2. HELPER FUNCTIONS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

def find_file(folder, names):

    if not os.path.exists(folder):
        return None

    for name in names:

<<<<<<< HEAD
        path = os.path.join(
            folder,
            name
        )
=======
        path = os.path.join(folder, name)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        if os.path.exists(path):
            return path

    return None


<<<<<<< HEAD
def find_keyword_file(
    keywords
):

    folders = [
        PROCESSED_DIR,
        SATELLITE_DIR,
        OUTPUT_DIR
    ]

    for folder in folders:

        if not os.path.exists(folder):
            continue

        files = glob.glob(
            os.path.join(
                folder,
                "*.csv"
            )
        )

        for file in files:

            filename = os.path.basename(
                file
            ).lower()

            if all(
                keyword.lower() in filename
                for keyword in keywords
            ):

                return file

    return None


=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
def safe_read_csv(path):

    if path is None:
        return None

    try:
<<<<<<< HEAD

        return pd.read_csv(
            path
        )

    except Exception as e:

        print(
            "Could not read:",
            path
        )

        print(
            "Reason:",
            e
        )
=======
        return pd.read_csv(path)

    except Exception as e:

        print("Could not read:")
        print(path)
        print("Reason:", e)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

        return None


<<<<<<< HEAD
=======
def fmt(value, digits=2):

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):.{digits}f}"

    except Exception:
        return "N/A"


>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
def count_rows(df):

    if df is None:
        return 0

    return len(df)


<<<<<<< HEAD
def fmt(
    value,
    digits=2
):

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):.{digits}f}"

    except Exception:

        return "N/A"


def safe_mean(
    df,
    column
):
=======
def safe_mean(df, column):
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    if df is None:
        return None

    if column not in df.columns:
        return None

    try:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        ).dropna()

        if len(values) == 0:
            return None

        return values.mean()

    except Exception:
<<<<<<< HEAD

        return None


def find_images(
    keywords
):

    results = []

    folders = [
        OUTPUT_DIR,
        SATELLITE_DIR,
        CHART_DIR,
        MAP_DIR
    ]

    extensions = [
        "*.png",
        "*.jpg",
        "*.jpeg"
    ]

    for folder in folders:

        if not os.path.exists(folder):
            continue

        for extension in extensions:

            files = glob.glob(
                os.path.join(
                    folder,
                    extension
                )
            )

            for file in files:

                filename = os.path.basename(
                    file
                ).lower()

                if any(
                    keyword.lower()
                    in filename
                    for keyword in keywords
                ):

                    results.append(
                        file
                    )

    return results


def make_chart(
    categories,
    values,
    title,
    filename
):

    path = os.path.join(
        CHART_DIR,
        filename
    )

    plt.figure(
        figsize=(10, 5.5)
    )

    plt.bar(
        categories,
        values
    )

    plt.title(
        title,
        fontsize=14
    )

    plt.ylabel(
        "Number of Records"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    return path


=======
        return None


>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================
# 3. START
# ============================================================

print()
print("=" * 70)
<<<<<<< HEAD
print("       GEOTWINAI PROFESSIONAL REPORT GENERATOR")
print("=" * 70)
print()

print(
    "Project:",
    BASE_DIR
)


# ============================================================
# 4. LOCATE INFRASTRUCTURE
# ============================================================

=======
print("        GEOTWINAI PROFESSIONAL REPORT GENERATOR")
print("=" * 70)
print()

print("Project:")
print(BASE_DIR)

print()
print("Output:")
print(REPORT_FILE)


# ============================================================
# 4. LOCATE INFRASTRUCTURE DATASETS
# ============================================================

print()
print("Locating datasets...")


>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
building_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Building_Clean.csv",
        "Nagpur_Buildings_Clean.csv",
<<<<<<< HEAD
        "Nagpur_Building_clean.csv"
=======
        "Nagpur_Building_clean.csv",
        "Nagpur_building_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


hospital_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Hospital_Clean.csv",
        "Nagpur_Hospitals_Clean.csv",
<<<<<<< HEAD
        "Nagpur_Hospital_clean.csv"
=======
        "Nagpur_Hospital_clean.csv",
        "Nagpur_hospital_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


school_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_School_Clean.csv",
        "Nagpur_Schools_Clean.csv",
<<<<<<< HEAD
        "Nagpur_School_clean.csv"
=======
        "Nagpur_School_clean.csv",
        "Nagpur_school_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


park_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Park_Clean.csv",
        "Nagpur_Parks_Clean.csv",
<<<<<<< HEAD
        "Nagpur_Park_clean.csv"
=======
        "Nagpur_Park_clean.csv",
        "Nagpur_park_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


road_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Road_Clean.csv",
        "Nagpur_Roads_Clean.csv",
<<<<<<< HEAD
        "Nagpur_Road_clean.csv"
=======
        "Nagpur_Road_clean.csv",
        "Nagpur_road_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


water_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Water_Bodies_Clean.csv",
        "Nagpur_Water_Body_Clean.csv",
<<<<<<< HEAD
        "Nagpur_Water_Bodies_clean.csv"
=======
        "Nagpur_Water_Bodies_clean.csv",
        "Nagpur_water_bodies_clean.csv"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]
)


# ============================================================
<<<<<<< HEAD
# 5. SATELLITE FILES
=======
# 5. LOCATE SATELLITE DATASETS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

all_bands_file = find_file(
    SATELLITE_DIR,
    [
        "Nagpur_Sentinel2_AllBands_Summary.csv",
        "Nagpur_Sentinel-2_AllBands_Summary.csv"
    ]
)


all_bands_spatial_file = find_file(
    SATELLITE_DIR,
    [
        "Nagpur_Sentinel2_AllBands_Spatial.csv",
        "Nagpur_Sentinel-2_AllBands_Spatial.csv"
    ]
)


<<<<<<< HEAD
=======
# ============================================================
# 6. LOCATE SATELLITE INDEX FILES
# ============================================================

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
builtup_summary_file = find_file(
    SATELLITE_DIR,
    [
        "Nagpur_Built-up_Summary.csv",
        "Nagpur_Built_Up_Summary.csv",
        "Nagpur_BuiltUp_Summary.csv"
    ]
)


green_summary_file = find_file(
    SATELLITE_DIR,
    [
        "Nagpur_Green_Cover_Summary.csv",
        "Nagpur_GreenCover_Summary.csv"
    ]
)


lulc_summary_file = find_file(
    SATELLITE_DIR,
    [
        "Nagpur_LULC_Summary.csv",
        "Nagpur_Land_Use_Summary.csv"
    ]
)


# ============================================================
<<<<<<< HEAD
# 6. NEW FLOOD + HEATMAP DATA
# ============================================================

flood_file = find_keyword_file(
    ["flood"]
)


heatmap_file = find_keyword_file(
    ["heat"]
)


# ============================================================
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# 7. READ DATA
# ============================================================

print()
print("Reading datasets...")


<<<<<<< HEAD
buildings = safe_read_csv(
    building_file
)

hospitals = safe_read_csv(
    hospital_file
)

schools = safe_read_csv(
    school_file
)

parks = safe_read_csv(
    park_file
)

roads = safe_read_csv(
    road_file
)

water = safe_read_csv(
    water_file
)

bands_summary = safe_read_csv(
    all_bands_file
)
=======
buildings = safe_read_csv(building_file)

hospitals = safe_read_csv(hospital_file)

schools = safe_read_csv(school_file)

parks = safe_read_csv(park_file)

roads = safe_read_csv(road_file)

water = safe_read_csv(water_file)

bands_summary = safe_read_csv(all_bands_file)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

bands_spatial = safe_read_csv(
    all_bands_spatial_file
)

builtup_summary = safe_read_csv(
    builtup_summary_file
)

green_summary = safe_read_csv(
    green_summary_file
)

lulc_summary = safe_read_csv(
    lulc_summary_file
)

<<<<<<< HEAD
flood_data = safe_read_csv(
    flood_file
)

heatmap_data = safe_read_csv(
    heatmap_file
)


# ============================================================
# 8. STATISTICS
# ============================================================

building_count = count_rows(
    buildings
)

hospital_count = count_rows(
    hospitals
)

school_count = count_rows(
    schools
)

park_count = count_rows(
    parks
)

road_count = count_rows(
    roads
)

water_count = count_rows(
    water
)

flood_count = count_rows(
    flood_data
)

heatmap_count = count_rows(
    heatmap_data
)
=======

# ============================================================
# 8. BASIC STATISTICS
# ============================================================

building_count = count_rows(buildings)

hospital_count = count_rows(hospitals)

school_count = count_rows(schools)

park_count = count_rows(parks)

road_count = count_rows(roads)

water_count = count_rows(water)


print()
print("Infrastructure records:")

print("Buildings:", building_count)
print("Hospitals:", hospital_count)
print("Schools:", school_count)
print("Parks:", park_count)
print("Roads:", road_count)
print("Water Bodies:", water_count)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


# ============================================================
# 9. SATELLITE INFORMATION
# ============================================================

scene_date = "N/A"

cloud_cover = "N/A"

mean_ndvi = "N/A"

mean_ndbi = "N/A"

mean_ndwi = "N/A"


if bands_summary is not None:

    if len(bands_summary) > 0:

        row = bands_summary.iloc[0]

        if "Scene_Date" in bands_summary.columns:

            scene_date = str(
                row["Scene_Date"]
            )

<<<<<<< HEAD
        if (
            "Cloud_Cover_Percent"
            in bands_summary.columns
        ):

            cloud_cover = fmt(
                row[
                    "Cloud_Cover_Percent"
                ],
=======
        if "Cloud_Cover_Percent" in bands_summary.columns:

            cloud_cover = fmt(
                row["Cloud_Cover_Percent"],
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
                2
            )

        if "Mean_NDVI" in bands_summary.columns:

            mean_ndvi = fmt(
                row["Mean_NDVI"],
                4
            )

        if "Mean_NDBI" in bands_summary.columns:

            mean_ndbi = fmt(
                row["Mean_NDBI"],
                4
            )

        if "Mean_NDWI" in bands_summary.columns:

            mean_ndwi = fmt(
                row["Mean_NDWI"],
                4
            )


<<<<<<< HEAD
=======
# ============================================================
# 10. CALCULATE INDICES FROM SPATIAL DATA IF NEEDED
# ============================================================

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
if bands_spatial is not None:

    if mean_ndvi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDVI"
        )

        if value is not None:
<<<<<<< HEAD

            mean_ndvi = fmt(
                value,
                4
            )
=======
            mean_ndvi = fmt(value, 4)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


    if mean_ndbi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDBI"
        )

        if value is not None:
<<<<<<< HEAD

            mean_ndbi = fmt(
                value,
                4
            )
=======
            mean_ndbi = fmt(value, 4)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


    if mean_ndwi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDWI"
        )

        if value is not None:
<<<<<<< HEAD

            mean_ndwi = fmt(
                value,
                4
            )


# ============================================================
# 10. CREATE INFRASTRUCTURE CHART
# ============================================================

print()
print(
    "Creating infrastructure chart..."
)
=======
            mean_ndwi = fmt(value, 4)


# ============================================================
# 11. INFRASTRUCTURE CHART
# ============================================================

print()
print("Creating infrastructure chart...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


categories = [
    "Buildings",
    "Hospitals",
    "Schools",
    "Parks",
    "Roads",
    "Water Bodies"
]


values = [
    building_count,
    hospital_count,
    school_count,
    park_count,
    road_count,
    water_count
]


<<<<<<< HEAD
INFRA_CHART = make_chart(
    categories,
    values,
    "Nagpur Urban Infrastructure Dataset Summary",
=======
INFRA_CHART = os.path.join(
    CHART_DIR,
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    "infrastructure_summary.png"
)


<<<<<<< HEAD
# ============================================================
# 11. NDVI CHART
=======
plt.figure(
    figsize=(10, 6)
)

plt.bar(
    categories,
    values
)

plt.title(
    "Nagpur Infrastructure Dataset Summary"
)

plt.ylabel(
    "Number of Records"
)

plt.xticks(
    rotation=30,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    INFRA_CHART,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 12. NDVI CHART
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

NDVI_CHART = None


if bands_spatial is not None:

    if "NDVI" in bands_spatial.columns:

        ndvi_values = pd.to_numeric(
            bands_spatial["NDVI"],
            errors="coerce"
        ).dropna()

<<<<<<< HEAD
        if len(ndvi_values) > 0:

=======

        if len(ndvi_values) > 0:

            print(
                "Creating NDVI distribution chart..."
            )

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            NDVI_CHART = os.path.join(
                CHART_DIR,
                "ndvi_distribution.png"
            )

<<<<<<< HEAD
            plt.figure(
                figsize=(10, 5.5)
=======

            plt.figure(
                figsize=(10, 6)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            )

            plt.hist(
                ndvi_values,
                bins=40
            )

            plt.title(
                "Sentinel-2 NDVI Distribution"
            )

            plt.xlabel(
                "NDVI"
            )

            plt.ylabel(
                "Number of Pixels"
            )

            plt.tight_layout()

            plt.savefig(
                NDVI_CHART,
                dpi=200,
                bbox_inches="tight"
            )

            plt.close()


# ============================================================
<<<<<<< HEAD
# 12. FLOOD CHART
# ============================================================

FLOOD_CHART = None


if flood_data is not None:

    numeric_columns = (
        flood_data
        .select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    if len(numeric_columns) > 0:

        flood_column = numeric_columns[0]

        values = pd.to_numeric(
            flood_data[
                flood_column
            ],
            errors="coerce"
        ).dropna()

        if len(values) > 0:

            FLOOD_CHART = os.path.join(
                CHART_DIR,
                "flood_risk_distribution.png"
            )

            plt.figure(
                figsize=(10, 5.5)
            )

            plt.hist(
                values,
                bins=20
            )

            plt.title(
                "Flood Risk Distribution"
            )

            plt.xlabel(
                flood_column
            )

            plt.ylabel(
                "Records"
            )

            plt.tight_layout()

            plt.savefig(
                FLOOD_CHART,
                dpi=200,
                bbox_inches="tight"
            )

            plt.close()


# ============================================================
# 13. HEATMAP CHART
# ============================================================

HEAT_CHART = None


if heatmap_data is not None:

    numeric_columns = (
        heatmap_data
        .select_dtypes(
            include="number"
        )
        .columns
        .tolist()
    )

    if len(numeric_columns) > 0:

        heat_column = numeric_columns[-1]

        values = pd.to_numeric(
            heatmap_data[
                heat_column
            ],
            errors="coerce"
        ).dropna()

        if len(values) > 0:

            HEAT_CHART = os.path.join(
                CHART_DIR,
                "heatmap_distribution.png"
            )

            plt.figure(
                figsize=(10, 5.5)
            )

            plt.hist(
                values,
                bins=20
            )

            plt.title(
                "Urban Heatmap Distribution"
            )

            plt.xlabel(
                heat_column
            )

            plt.ylabel(
                "Records"
            )

            plt.tight_layout()

            plt.savefig(
                HEAT_CHART,
                dpi=200,
                bbox_inches="tight"
            )

            plt.close()


# ============================================================
# 14. PDF DOCUMENT
# ============================================================

print()
print(
    "Building professional PDF..."
)
=======
# 13. PDF DOCUMENT
# ============================================================

print()
print("Building professional PDF...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


doc = SimpleDocTemplate(

    REPORT_FILE,

    pagesize=A4,

    rightMargin=18 * mm,

    leftMargin=18 * mm,

    topMargin=18 * mm,

    bottomMargin=18 * mm
)


# ============================================================
<<<<<<< HEAD
# 15. STYLES
=======
# 14. STYLES
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

styles = getSampleStyleSheet()


title_style = ParagraphStyle(

    "TitleCustom",

    parent=styles["Title"],

    fontSize=26,

    leading=32,

    alignment=TA_CENTER,

    spaceAfter=18
)


subtitle_style = ParagraphStyle(

    "Subtitle",

    parent=styles["Normal"],

    fontSize=14,

    leading=20,

    alignment=TA_CENTER,

    spaceAfter=12
)


heading_style = ParagraphStyle(

    "HeadingCustom",

    parent=styles["Heading1"],

    fontSize=18,

    leading=23,

    spaceBefore=10,

    spaceAfter=10
)


<<<<<<< HEAD
subheading_style = ParagraphStyle(

    "SubHeading",

    parent=styles["Heading2"],

    fontSize=13,

    leading=17,

    spaceBefore=8,

    spaceAfter=7
)


=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
body_style = ParagraphStyle(

    "BodyCustom",

    parent=styles["BodyText"],

    fontSize=9.5,

    leading=15,

    spaceAfter=8
)


center_style = ParagraphStyle(

    "Center",

    parent=body_style,

    alignment=TA_CENTER
)


small_style = ParagraphStyle(

    "Small",

    parent=styles["BodyText"],

    fontSize=8,

    leading=11
)


story = []


# ============================================================
<<<<<<< HEAD
# 16. COVER PAGE
=======
# 15. COVER PAGE
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Spacer(
        1,
<<<<<<< HEAD
        30 * mm
=======
        35 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )
)


story.append(
    Paragraph(
        "GEOTWINAI",
        title_style
    )
)


story.append(
    Paragraph(
        "AI-Powered Digital Twin for Smart Cities",
        subtitle_style
    )
)


story.append(
    Spacer(
        1,
<<<<<<< HEAD
        8 * mm
=======
        10 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )
)


story.append(
    Paragraph(
        "Nagpur Urban Planning & Decision Support Report",
        subtitle_style
    )
)


story.append(
    Spacer(
        1,
<<<<<<< HEAD
        18 * mm
=======
        20 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )
)


cover_data = [

    [
        Paragraph(
            "<b>Study Area</b>",
            body_style
        ),
        Paragraph(
            "Nagpur, Maharashtra",
            body_style
        )
    ],

    [
        Paragraph(
<<<<<<< HEAD
            "<b>Satellite</b>",
=======
            "<b>Satellite Dataset</b>",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            body_style
        ),
        Paragraph(
            "Sentinel-2 Level-2A",
            body_style
        )
    ],

    [
        Paragraph(
            "<b>Satellite Source</b>",
            body_style
        ),
        Paragraph(
            "Microsoft Planetary Computer",
            body_style
        )
    ],

    [
        Paragraph(
<<<<<<< HEAD
            "<b>Spatial Resolution</b>",
=======
            "<b>Analysis Resolution</b>",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            body_style
        ),
        Paragraph(
            "10 metres",
            body_style
        )
    ],

    [
        Paragraph(
            "<b>Scene Date</b>",
            body_style
        ),
        Paragraph(
            scene_date,
            body_style
        )
<<<<<<< HEAD
    ],

    [
        Paragraph(
            "<b>Generated By</b>",
            body_style
        ),
        Paragraph(
            "GeoTwinAI Automated Report Generator",
            body_style
        )
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    ]

]


cover_table = Table(

    cover_data,

    colWidths=[
        55 * mm,
        105 * mm
    ]
)


cover_table.setStyle(
    TableStyle([

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            8
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            8
        ),

        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            7
        )

    ])
)


story.append(
    cover_table
)


story.append(
    Spacer(
        1,
<<<<<<< HEAD
        18 * mm
=======
        20 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    )
)


story.append(
    Paragraph(
<<<<<<< HEAD

        "GeoTwinAI integrates geospatial infrastructure "
        "datasets, satellite remote sensing, environmental "
        "indices, flood analysis, heatmap analysis and "
        "machine learning to support smart-city planning "
        "and decision-making.",

=======
        "GeoTwinAI integrates geospatial datasets, "
        "satellite-derived indicators and machine learning "
        "to support urban planning and smart-city "
        "decision-making.",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        center_style
    )
)


story.append(
    PageBreak()
)


# ============================================================
<<<<<<< HEAD
# 17. EXECUTIVE SUMMARY
=======
# 16. EXECUTIVE SUMMARY
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
        "1. Executive Summary",
        heading_style
    )
)


executive_text = f"""
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
GeoTwinAI is an AI-powered geospatial decision-support
platform developed for urban planning and smart-city
analysis in Nagpur, Maharashtra.

<<<<<<< HEAD
The platform integrates infrastructure datasets,
Sentinel-2 satellite observations, environmental indices,
flood-risk analysis, heatmap analysis and machine-learning
components.

The selected Sentinel-2 scene has a reported cloud cover
of {cloud_cover}% and a scene date of {scene_date}.

The environmental analysis includes NDVI, NDBI and NDWI.
Infrastructure analysis includes buildings, hospitals,
schools, parks, roads and water bodies.

The platform additionally incorporates flood-risk and
urban heatmap analysis to support environmental risk
assessment.

The final workflow connects GIS visualization, machine
learning, automated data processing and Power BI analytics.
=======
The system integrates infrastructure datasets with
Sentinel-2 satellite observations to provide a spatial
understanding of the urban environment.

The selected satellite scene has a recorded cloud cover
of {cloud_cover}% and a scene date of {scene_date}.

The platform analyses vegetation, built-up areas and
water-related characteristics using NDVI, NDBI and NDWI.

Infrastructure datasets include buildings, hospitals,
schools, parks, roads and water bodies.

The final system combines GIS visualization, machine
learning and Power BI analytics into a unified urban
planning workflow.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
"""


story.append(
    Paragraph(
        executive_text,
        body_style
    )
)


# ============================================================
<<<<<<< HEAD
# 18. PROJECT OBJECTIVES
=======
# 17. PROJECT OBJECTIVES
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
        "2. Project Objectives",
        heading_style
    )
)


objectives = [

    "Develop an AI-powered Digital Twin framework for Nagpur.",

    "Integrate satellite and GIS datasets.",

    "Analyse vegetation and environmental conditions.",

<<<<<<< HEAD
    "Analyse built-up and water-related characteristics.",

    "Map important urban infrastructure.",

    "Analyse flood-risk conditions.",

    "Identify heat-related urban hotspots.",

=======
    "Identify built-up and water-related characteristics.",

    "Map important urban infrastructure.",

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    "Create machine-learning-based urban priority analysis.",

    "Provide interactive GIS visualization.",

    "Provide analytical dashboards through Power BI.",

<<<<<<< HEAD
    "Support data-driven urban planning decisions.",

    "Create an extensible framework for future data updates."
=======
    "Support data-driven urban planning decisions."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


for objective in objectives:

    story.append(
        Paragraph(
            "• " + objective,
            body_style
        )
    )


# ============================================================
<<<<<<< HEAD
# 19. DATA SOURCES
=======
# 18. DATA SOURCES
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
        "3. Data Sources",
        heading_style
    )
)


data_source_table = Table(

    [

        [
            Paragraph(
                "<b>Dataset</b>",
                body_style
            ),

            Paragraph(
                "<b>Purpose</b>",
                body_style
            )
        ],

        [
            "Buildings",
            "Urban building and infrastructure analysis"
        ],

        [
            "Hospitals",
            "Healthcare infrastructure mapping"
        ],

        [
            "Schools",
            "Educational infrastructure mapping"
        ],

        [
            "Parks",
            "Green and open-space analysis"
        ],

        [
            "Roads",
            "Transportation network analysis"
        ],

        [
            "Water Bodies",
            "Water-resource analysis"
        ],

        [
            "Sentinel-2",
            "Satellite and environmental analysis"
        ],

        [
<<<<<<< HEAD
            "All Sentinel-2 Bands",
            "Multi-spectral analysis"
        ],

        [
            "NDVI / NDBI / NDWI",
            "Environmental and urban indicators"
        ],

        [
            "LULC",
            "Land-use and land-cover analysis"
        ],

        [
            "Flood Risk",
            "Flood vulnerability analysis"
        ],

        [
            "Heatmap",
            "Urban hotspot analysis"
        ],

        [
=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
            "Machine Learning",
            "Urban priority prediction"
        ],

        [
            "Power BI",
            "Interactive analytical dashboard"
        ]

    ],

    colWidths=[
        55 * mm,
        105 * mm
    ]
)


data_source_table.setStyle(
    TableStyle([

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.lightgrey
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            7
        )

    ])
)


story.append(
    data_source_table
)


# ============================================================
<<<<<<< HEAD
# 20. INFRASTRUCTURE STATISTICS
=======
# 19. INFRASTRUCTURE STATISTICS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "4. Urban Infrastructure Statistics",
        heading_style
    )
)


infra_table = Table(

    [

        [
            Paragraph(
                "<b>Infrastructure Type</b>",
                body_style
            ),

            Paragraph(
                "<b>Records</b>",
                body_style
            )
        ],

        [
            "Buildings",
            str(building_count)
        ],

        [
            "Hospitals",
            str(hospital_count)
        ],

        [
            "Schools",
            str(school_count)
        ],

        [
            "Parks",
            str(park_count)
        ],

        [
            "Roads",
            str(road_count)
        ],

        [
            "Water Bodies",
            str(water_count)
        ]

    ],

    colWidths=[
        100 * mm,
        60 * mm
    ]
)


infra_table.setStyle(
    TableStyle([

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.lightgrey
        ),

        (
            "ALIGN",
            (1, 1),
            (1, -1),
            "CENTER"
        )

    ])
)


story.append(
    infra_table
)


story.append(
    Spacer(
        1,
        8 * mm
    )
)


<<<<<<< HEAD
if os.path.exists(
    INFRA_CHART
):
=======
if os.path.exists(INFRA_CHART):
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    story.append(
        Image(
            INFRA_CHART,
            width=165 * mm,
<<<<<<< HEAD
            height=90 * mm
=======
            height=95 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )
    )


# ============================================================
<<<<<<< HEAD
# 21. SATELLITE ANALYSIS
=======
# 20. SATELLITE ANALYSIS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "5. Sentinel-2 Satellite Analysis",
        heading_style
    )
)


satellite_text = f"""
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
The satellite analysis uses Sentinel-2 Level-2A imagery
obtained through Microsoft Planetary Computer.

The selected scene date is {scene_date}, with a reported
cloud cover of {cloud_cover}%.

A common 10-metre spatial reference grid is used for
integrated multi-band analysis.

<<<<<<< HEAD
The processed Sentinel-2 dataset includes B01, B02, B03,
B04, B05, B06, B07, B08, B8A, B09, B11 and B12.
=======
The processed dataset includes B01, B02, B03, B04, B05,
B06, B07, B08, B8A, B09, B11 and B12.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
"""


story.append(
    Paragraph(
        satellite_text,
        body_style
    )
)


# ============================================================
<<<<<<< HEAD
# 22. SPECTRAL INDICES
=======
# 21. SPECTRAL INDICES
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
        "6. Spectral Indices",
        heading_style
    )
)


index_table = Table(

    [

        [
            Paragraph(
                "<b>Index</b>",
                body_style
            ),

            Paragraph(
                "<b>Purpose</b>",
                body_style
            ),

            Paragraph(
                "<b>Mean</b>",
                body_style
            )
        ],

        [
            "NDVI",
            "Vegetation condition",
            mean_ndvi
        ],

        [
            "NDBI",
            "Built-up area indication",
            mean_ndbi
        ],

        [
            "NDWI",
            "Water-related analysis",
            mean_ndwi
        ]

    ],

    colWidths=[
        35 * mm,
        90 * mm,
        35 * mm
    ]
)


index_table.setStyle(
    TableStyle([

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.lightgrey
        ),

        (
            "ALIGN",
            (2, 1),
            (2, -1),
            "CENTER"
        )

    ])
)


story.append(
    index_table
)


if NDVI_CHART is not None:

    story.append(
        Spacer(
            1,
            8 * mm
        )
    )

    story.append(
        Image(
            NDVI_CHART,
            width=165 * mm,
<<<<<<< HEAD
            height=90 * mm
=======
            height=95 * mm
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        )
    )


# ============================================================
<<<<<<< HEAD
# 23. ALL-BAND ANALYSIS
=======
# 22. ALL BAND ANALYSIS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "7. Sentinel-2 All-Band Analysis",
        heading_style
    )
)


all_band_text = """
<<<<<<< HEAD

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
The all-band Sentinel-2 dataset preserves spectral
information required for environmental and urban analysis.

Processed bands include:

B01 - Coastal/Aerosol

B02 - Blue

B03 - Green

B04 - Red

B05 - Vegetation Red Edge

B06 - Vegetation Red Edge

B07 - Vegetation Red Edge

B08 - Near Infrared

B8A - Narrow Near Infrared

B09 - Water Vapour

B11 - Short-Wave Infrared

B12 - Short-Wave Infrared

<<<<<<< HEAD
The combined spectral information supports vegetation,
water, soil, built-up and land-cover analysis.
=======
These bands support vegetation, water, soil, built-up
and land-cover analysis.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
"""


story.append(
    Paragraph(
        all_band_text,
        body_style
    )
)


# ============================================================
<<<<<<< HEAD
# 24. LULC / BUILT-UP / GREEN COVER
=======
# 23. MACHINE LEARNING
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
<<<<<<< HEAD
        "8. Land Use, Built-up Area and Green Cover",
        heading_style
    )
)


lulc_text = """

GeoTwinAI incorporates land-use and land-cover analysis
to understand the spatial composition of the study area.

Built-up analysis provides an indication of urbanized
areas, while green-cover analysis supports identification
of vegetation-rich and vegetation-deficient regions.

LULC analysis can support planning decisions involving
urban expansion, open spaces, vegetation conservation
and land management.
"""


story.append(
    Paragraph(
        lulc_text,
        body_style
    )
)


# ============================================================
# 25. FLOOD RISK ANALYSIS
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "9. Flood Risk Analysis",
        heading_style
    )
)


if flood_data is not None:

    flood_text = f"""

The GeoTwinAI system includes flood-risk analysis as an
additional environmental risk component.

The detected flood dataset contains approximately
{flood_count} records.

The flood analysis can be used to identify areas that may
require additional attention for drainage planning,
water management, emergency planning and urban resilience.

The interactive GIS map can be used to spatially inspect
the flood-risk information.
"""

else:

    flood_text = """

Flood-risk analysis is included as a planned component of
the GeoTwinAI platform.

The report generator automatically searches the project
output folders for flood-related datasets and incorporates
them when available.
"""


story.append(
    Paragraph(
        flood_text,
        body_style
    )
)


if FLOOD_CHART is not None:

    story.append(
        Spacer(
            1,
            6 * mm
        )
    )

    story.append(
        Image(
            FLOOD_CHART,
            width=165 * mm,
            height=90 * mm
        )
    )


flood_images = find_images(
    ["flood"]
)


for image_file in flood_images[:2]:

    try:

        story.append(
            Spacer(
                1,
                5 * mm
            )
        )

        story.append(
            Image(
                image_file,
                width=165 * mm,
                height=90 * mm
            )
        )

    except Exception:
        pass


# ============================================================
# 26. HEATMAP ANALYSIS
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "10. Urban Heatmap Analysis",
        heading_style
    )
)


if heatmap_data is not None:

    heat_text = f"""

The GeoTwinAI platform also incorporates urban heatmap
analysis to identify spatial concentrations or hotspots
associated with heat-related conditions.

The detected heatmap dataset contains approximately
{heatmap_count} records.

Heatmap information can support urban heat mitigation,
green-space planning, infrastructure planning and
identification of areas requiring additional environmental
attention.
"""

else:

    heat_text = """

Urban heatmap analysis is included as an environmental
planning component of GeoTwinAI.

The report generator automatically searches the project
output folders for heat-related datasets and incorporates
them when available.
"""


story.append(
    Paragraph(
        heat_text,
        body_style
    )
)


if HEAT_CHART is not None:

    story.append(
        Spacer(
            1,
            6 * mm
        )
    )

    story.append(
        Image(
            HEAT_CHART,
            width=165 * mm,
            height=90 * mm
        )
    )


heat_images = find_images(
    [
        "heat",
        "thermal"
    ]
)


for image_file in heat_images[:2]:

    try:

        story.append(
            Spacer(
                1,
                5 * mm
            )
        )

        story.append(
            Image(
                image_file,
                width=165 * mm,
                height=90 * mm
            )
        )

    except Exception:
        pass


# ============================================================
# 27. MACHINE LEARNING
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "11. Machine Learning Analysis",
=======
        "8. Machine Learning Analysis",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


ml_text = """
<<<<<<< HEAD

The machine-learning component of GeoTwinAI is designed
to classify urban areas according to planning priority.

Feature engineering combines relevant infrastructure,
environmental and spatial attributes into a machine-
learning dataset.

The trained model can generate priority predictions such
as High, Medium and Low.
=======
The machine-learning component of GeoTwinAI is designed
to classify urban areas according to planning priority.

The feature-engineering stage combines infrastructure
and environmental attributes into a machine-learning
dataset.

The trained model can generate urban priority
predictions such as High, Medium and Low.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

These predictions can support identification of areas
requiring additional infrastructure or environmental
attention.

<<<<<<< HEAD
Model performance should be evaluated using accuracy,
precision, recall and F1-score.
=======
Model performance should be evaluated using appropriate
classification metrics such as accuracy, precision,
recall and F1-score.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
"""


story.append(
    Paragraph(
        ml_text,
        body_style
    )
)


# ============================================================
<<<<<<< HEAD
# 28. INTERACTIVE GIS MAP
=======
# 24. DIGITAL TWIN WORKFLOW
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
<<<<<<< HEAD
        "12. Interactive GIS Visualization",
        heading_style
    )
)


map_text = """

GeoTwinAI provides an interactive GIS visualization layer
for exploring the spatial distribution of urban
infrastructure and environmental-risk information.

The interactive map is designed to allow users to switch
layers on and off and inspect individual spatial records.

Available layers include buildings, hospitals, schools,
parks, roads, water bodies, flood-risk information and
urban heatmap information when the corresponding datasets
are available.
"""


story.append(
    Paragraph(
        map_text,
        body_style
    )
)


map_file = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Interactive_Map.html"
)


if os.path.exists(map_file):

    story.append(
        Paragraph(
            "<b>Interactive Map:</b> "
            "Nagpur_Interactive_Map.html",
            body_style
        )
    )


# ============================================================
# 29. DIGITAL TWIN WORKFLOW
# ============================================================

story.append(
    Paragraph(
        "13. GeoTwinAI Workflow",
=======
        "9. GeoTwinAI Workflow",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


workflow = [

    "Data collection",

    "Data cleaning",

<<<<<<< HEAD
    "Satellite data acquisition",

    "Satellite preprocessing",

    "All-band processing",

    "NDVI / NDBI / NDWI generation",

    "LULC analysis",

    "Built-up and green-cover analysis",

    "Flood-risk analysis",

    "Heatmap analysis",
=======
    "Satellite processing",

    "Spectral index generation",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    "Feature engineering",

    "Machine learning",

    "Prediction",

    "Interactive GIS visualization",

    "Power BI dashboard",

<<<<<<< HEAD
    "Urban planning decision support",

    "Future automated data updates"
=======
    "Urban planning decision support"
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


for i, step in enumerate(
    workflow,
    start=1
):

    story.append(
        Paragraph(
            f"{i}. {step}",
            body_style
        )
    )


# ============================================================
<<<<<<< HEAD
# 30. KEY FINDINGS
=======
# 25. KEY FINDINGS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
<<<<<<< HEAD
        "14. Key Findings",
=======
        "10. Key Findings",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


findings = [

<<<<<<< HEAD
    f"The infrastructure dataset contains "
=======
    f"The processed infrastructure datasets contain "
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    f"{building_count} building records.",

    f"The healthcare dataset contains "
    f"{hospital_count} hospital records.",

    f"The education dataset contains "
    f"{school_count} school records.",

    f"The parks dataset contains "
    f"{park_count} park records.",

<<<<<<< HEAD
    f"The road dataset contains "
    f"{road_count} records.",

=======
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    f"The water-body dataset contains "
    f"{water_count} records.",

    f"The selected Sentinel-2 scene has "
    f"{cloud_cover}% reported cloud cover.",

<<<<<<< HEAD
    f"The mean NDVI is {mean_ndvi}.",

    f"The mean NDBI is {mean_ndbi}.",

    f"The mean NDWI is {mean_ndwi}.",

    f"Flood-risk records detected: "
    f"{flood_count}.",

    f"Heatmap records detected: "
    f"{heatmap_count}."
=======
    f"The mean NDVI is "
    f"{mean_ndvi}.",

    f"The mean NDBI is "
    f"{mean_ndbi}.",

    f"The mean NDWI is "
    f"{mean_ndwi}."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


for finding in findings:

    story.append(
        Paragraph(
            "• " + finding,
            body_style
        )
    )


# ============================================================
<<<<<<< HEAD
# 31. RECOMMENDATIONS
=======
# 26. RECOMMENDATIONS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
<<<<<<< HEAD
        "15. Recommendations",
=======
        "11. Recommendations",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


recommendations = [

    "Use the interactive GIS map to inspect spatial "
    "distribution of infrastructure.",

    "Use NDVI to identify vegetation-rich and "
    "vegetation-deficient areas.",

    "Use NDBI to identify highly built-up areas.",

<<<<<<< HEAD
    "Use NDWI and water-body information for "
    "water-resource planning.",

    "Use flood-risk analysis for drainage and "
    "urban-resilience planning.",

    "Use heatmap analysis to identify potential "
    "urban hotspots.",

=======
    "Use NDWI and water-body data to support "
    "water-resource planning.",

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
    "Use ML priority classifications to identify "
    "areas requiring planning attention.",

    "Use Power BI for executive-level monitoring "
    "and comparative analysis.",

<<<<<<< HEAD
    "Use multi-date satellite observations to "
    "monitor changes over time.",

    "Integrate official MRSAC datasets wherever "
    "available for production-level analysis.",

    "Maintain year/date information so that future "
    "observations can be compared with historical data."
=======
    "Periodically update Sentinel-2 observations "
    "to monitor urban environmental change.",

    "Integrate official MRSAC datasets wherever "
    "available for production-level analysis."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


for recommendation in recommendations:

    story.append(
        Paragraph(
            "• " + recommendation,
            body_style
        )
    )


# ============================================================
<<<<<<< HEAD
# 32. LIMITATIONS
=======
# 27. LIMITATIONS
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
<<<<<<< HEAD
        "16. Limitations",
=======
        "12. Limitations",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


limitations = [

    "The Nagpur bounding box represents an analysis "
    "area and is not necessarily a formal administrative boundary.",

    "Satellite observations are affected by atmospheric "
    "and seasonal conditions.",

    "Cloud-cover metadata is scene-level and does not "
    "necessarily represent cloud conditions at every pixel.",

<<<<<<< HEAD
    "Flood and heatmap outputs depend on the underlying "
    "input datasets and processing methods.",
=======
    "The current analysis uses one selected best-available "
    "scene rather than a full temporal time series.",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    "Machine-learning predictions depend on the quality "
    "and representativeness of the training dataset.",

    "Infrastructure records should be validated against "
<<<<<<< HEAD
    "authoritative datasets before operational deployment.",

    "Future-date information cannot be known until new "
    "observations or datasets become available."
=======
    "authoritative datasets before operational deployment."
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


for limitation in limitations:

    story.append(
        Paragraph(
            "• " + limitation,
            body_style
        )
    )


# ============================================================
<<<<<<< HEAD
# 33. CONCLUSION
=======
# 28. CONCLUSION
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
<<<<<<< HEAD
        "17. Conclusion",
=======
        "13. Conclusion",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


conclusion = """
<<<<<<< HEAD

GeoTwinAI provides a unified framework for combining
geospatial infrastructure data, satellite remote sensing,
environmental indices, flood-risk analysis, heatmap
analysis and machine learning for smart-city planning.

The integration of Sentinel-2 spectral information,
environmental indicators and infrastructure datasets
provides a spatially oriented understanding of urban
conditions.

The flood-risk and heatmap components extend the platform
from infrastructure mapping to environmental-risk
assessment.

The interactive GIS map provides detailed spatial
exploration, while Power BI can provide higher-level
=======
GeoTwinAI provides a unified framework for combining
geospatial infrastructure data, satellite remote sensing
and machine learning for smart-city planning.

The integration of Sentinel-2 spectral information,
environmental indices, infrastructure datasets and
machine-learning predictions provides a spatially
oriented view of urban conditions.

The interactive GIS map provides detailed spatial
exploration, while Power BI provides higher-level
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
analytical dashboards for decision-makers.

Future development can include multi-date satellite
monitoring, improved administrative boundaries, official
MRSAC datasets, advanced machine-learning models and
<<<<<<< HEAD
automated acquisition of newly available observations.
=======
automated data updates.
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

The overall system can therefore serve as a foundation
for an AI-enabled urban planning and decision-support
platform.
"""


story.append(
    Paragraph(
        conclusion,
        body_style
    )
)


# ============================================================
<<<<<<< HEAD
# 34. TECHNICAL INFORMATION
=======
# 29. TECHNICAL INFORMATION
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

story.append(
    Paragraph(
<<<<<<< HEAD
        "18. Technical Information",
=======
        "14. Technical Information",
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
        heading_style
    )
)


technical = [

    ["Programming", "Python"],

    ["Satellite", "Sentinel-2"],

    ["Product", "Sentinel-2 Level-2A"],

<<<<<<< HEAD
    [
        "Satellite Source",
        "Microsoft Planetary Computer"
    ],

    [
        "Spatial Reference",
        "10 metres"
    ],

    [
        "Indices",
        "NDVI, NDBI, NDWI"
    ],

    [
        "Land Analysis",
        "LULC / Built-up / Green Cover"
    ],

    [
        "Risk Analysis",
        "Flood Risk / Heatmap"
    ],

    [
        "GIS",
        "Folium Interactive HTML Map"
    ],

    [
        "Machine Learning",
        "Urban Priority Classification"
    ],

    [
        "Dashboard",
        "Microsoft Power BI"
    ],

    [
        "Report",
        "Professional PDF"
    ]
=======
    ["Satellite Source", "Microsoft Planetary Computer"],

    ["Spatial Reference Grid", "10 metres"],

    ["Indices", "NDVI, NDBI, NDWI"],

    ["GIS Visualization", "Interactive HTML Map"],

    ["Dashboard", "Microsoft Power BI"],

    ["Machine Learning", "Urban Priority Classification"],

    ["Report Format", "PDF"]
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

]


technical_table = Table(

    technical,

    colWidths=[
        65 * mm,
        95 * mm
    ]
)


technical_table.setStyle(
    TableStyle([

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.5,
            colors.grey
        ),

        (
            "BACKGROUND",
            (0, 0),
            (0, -1),
            colors.lightgrey
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),

        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            7
        ),

        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            7
        )

    ])
)


story.append(
    technical_table
)


# ============================================================
<<<<<<< HEAD
# 35. BUILD PDF
# ============================================================

print()
print(
    "Generating PDF..."
)
=======
# 30. BUILD PDF
# ============================================================

print()
print("Generating PDF...")
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe


try:

<<<<<<< HEAD
    doc.build(
        story
    )
=======
    doc.build(story)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

except Exception as e:

    print()
<<<<<<< HEAD
    print(
        "ERROR WHILE CREATING PDF"
    )

    print(
        e
    )
=======
    print("ERROR WHILE CREATING PDF")
    print(e)
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe

    raise


# ============================================================
<<<<<<< HEAD
# 36. FINAL
=======
# 31. FINAL MESSAGE
>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
# ============================================================

print()
print("=" * 70)
print("       PROFESSIONAL REPORT COMPLETED")
print("=" * 70)
<<<<<<< HEAD
print()

print(
    "Report created:"
)

print(
    REPORT_FILE
)

print()

print(
    "Report folder:"
)

print(
    REPORT_DIR
)

print()

print("=" * 70)
=======

print()

print("Report created:")

print(REPORT_FILE)

print()

print("Report folder:")

print(REPORT_DIR)

print()

print("=" * 70)



>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
