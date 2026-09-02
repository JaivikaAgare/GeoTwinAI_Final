# ============================================================
# GEOTWINAI
# PROFESSIONAL SMART CITY REPORT GENERATOR
#
# Project:
# AI-Powered Digital Twin for Smart Cities
#
# Study Area:
# Nagpur, Maharashtra
#
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

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether
)

warnings.filterwarnings("ignore")


# ============================================================
# 1. PATHS
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


REPORT_FILE = os.path.join(
    REPORT_DIR,
    "GeoTwinAI_Nagpur_Professional_Report.pdf"
)


# ============================================================
# 2. HELPERS
# ============================================================

def find_file(folder, names):

    if not os.path.exists(folder):
        return None

    for name in names:

        path = os.path.join(
            folder,
            name
        )

        if os.path.exists(path):
            return path

    return None


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


def safe_read_csv(path):

    if path is None:
        return None

    try:

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

        return None


def count_rows(df):

    if df is None:
        return 0

    return len(df)


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


# ============================================================
# 3. START
# ============================================================

print()
print("=" * 70)
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

building_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Building_Clean.csv",
        "Nagpur_Buildings_Clean.csv",
        "Nagpur_Building_clean.csv"
    ]
)


hospital_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Hospital_Clean.csv",
        "Nagpur_Hospitals_Clean.csv",
        "Nagpur_Hospital_clean.csv"
    ]
)


school_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_School_Clean.csv",
        "Nagpur_Schools_Clean.csv",
        "Nagpur_School_clean.csv"
    ]
)


park_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Park_Clean.csv",
        "Nagpur_Parks_Clean.csv",
        "Nagpur_Park_clean.csv"
    ]
)


road_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Road_Clean.csv",
        "Nagpur_Roads_Clean.csv",
        "Nagpur_Road_clean.csv"
    ]
)


water_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Water_Bodies_Clean.csv",
        "Nagpur_Water_Body_Clean.csv",
        "Nagpur_Water_Bodies_clean.csv"
    ]
)


# ============================================================
# 5. SATELLITE FILES
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
# 6. NEW FLOOD + HEATMAP DATA
# ============================================================

flood_file = find_keyword_file(
    ["flood"]
)


heatmap_file = find_keyword_file(
    ["heat"]
)


# ============================================================
# 7. READ DATA
# ============================================================

print()
print("Reading datasets...")


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

        if (
            "Cloud_Cover_Percent"
            in bands_summary.columns
        ):

            cloud_cover = fmt(
                row[
                    "Cloud_Cover_Percent"
                ],
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


if bands_spatial is not None:

    if mean_ndvi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDVI"
        )

        if value is not None:

            mean_ndvi = fmt(
                value,
                4
            )


    if mean_ndbi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDBI"
        )

        if value is not None:

            mean_ndbi = fmt(
                value,
                4
            )


    if mean_ndwi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDWI"
        )

        if value is not None:

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


INFRA_CHART = make_chart(
    categories,
    values,
    "Nagpur Urban Infrastructure Dataset Summary",
    "infrastructure_summary.png"
)


# ============================================================
# 11. NDVI CHART
# ============================================================

NDVI_CHART = None


if bands_spatial is not None:

    if "NDVI" in bands_spatial.columns:

        ndvi_values = pd.to_numeric(
            bands_spatial["NDVI"],
            errors="coerce"
        ).dropna()

        if len(ndvi_values) > 0:

            NDVI_CHART = os.path.join(
                CHART_DIR,
                "ndvi_distribution.png"
            )

            plt.figure(
                figsize=(10, 5.5)
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


doc = SimpleDocTemplate(

    REPORT_FILE,

    pagesize=A4,

    rightMargin=18 * mm,

    leftMargin=18 * mm,

    topMargin=18 * mm,

    bottomMargin=18 * mm
)


# ============================================================
# 15. STYLES
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


subheading_style = ParagraphStyle(

    "SubHeading",

    parent=styles["Heading2"],

    fontSize=13,

    leading=17,

    spaceBefore=8,

    spaceAfter=7
)


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
# 16. COVER PAGE
# ============================================================

story.append(
    Spacer(
        1,
        30 * mm
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
        8 * mm
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
        18 * mm
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
            "<b>Satellite</b>",
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
            "<b>Spatial Resolution</b>",
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
        18 * mm
    )
)


story.append(
    Paragraph(

        "GeoTwinAI integrates geospatial infrastructure "
        "datasets, satellite remote sensing, environmental "
        "indices, flood analysis, heatmap analysis and "
        "machine learning to support smart-city planning "
        "and decision-making.",

        center_style
    )
)


story.append(
    PageBreak()
)


# ============================================================
# 17. EXECUTIVE SUMMARY
# ============================================================

story.append(
    Paragraph(
        "1. Executive Summary",
        heading_style
    )
)


executive_text = f"""

GeoTwinAI is an AI-powered geospatial decision-support
platform developed for urban planning and smart-city
analysis in Nagpur, Maharashtra.

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
"""


story.append(
    Paragraph(
        executive_text,
        body_style
    )
)


# ============================================================
# 18. PROJECT OBJECTIVES
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

    "Analyse built-up and water-related characteristics.",

    "Map important urban infrastructure.",

    "Analyse flood-risk conditions.",

    "Identify heat-related urban hotspots.",

    "Create machine-learning-based urban priority analysis.",

    "Provide interactive GIS visualization.",

    "Provide analytical dashboards through Power BI.",

    "Support data-driven urban planning decisions.",

    "Create an extensible framework for future data updates."

]


for objective in objectives:

    story.append(
        Paragraph(
            "• " + objective,
            body_style
        )
    )


# ============================================================
# 19. DATA SOURCES
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
# 20. INFRASTRUCTURE STATISTICS
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


if os.path.exists(
    INFRA_CHART
):

    story.append(
        Image(
            INFRA_CHART,
            width=165 * mm,
            height=90 * mm
        )
    )


# ============================================================
# 21. SATELLITE ANALYSIS
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

The satellite analysis uses Sentinel-2 Level-2A imagery
obtained through Microsoft Planetary Computer.

The selected scene date is {scene_date}, with a reported
cloud cover of {cloud_cover}%.

A common 10-metre spatial reference grid is used for
integrated multi-band analysis.

The processed Sentinel-2 dataset includes B01, B02, B03,
B04, B05, B06, B07, B08, B8A, B09, B11 and B12.
"""


story.append(
    Paragraph(
        satellite_text,
        body_style
    )
)


# ============================================================
# 22. SPECTRAL INDICES
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
            height=90 * mm
        )
    )


# ============================================================
# 23. ALL-BAND ANALYSIS
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

The combined spectral information supports vegetation,
water, soil, built-up and land-cover analysis.
"""


story.append(
    Paragraph(
        all_band_text,
        body_style
    )
)


# ============================================================
# 24. LULC / BUILT-UP / GREEN COVER
# ============================================================

story.append(
    Paragraph(
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
        heading_style
    )
)


ml_text = """

The machine-learning component of GeoTwinAI is designed
to classify urban areas according to planning priority.

Feature engineering combines relevant infrastructure,
environmental and spatial attributes into a machine-
learning dataset.

The trained model can generate priority predictions such
as High, Medium and Low.

These predictions can support identification of areas
requiring additional infrastructure or environmental
attention.

Model performance should be evaluated using accuracy,
precision, recall and F1-score.
"""


story.append(
    Paragraph(
        ml_text,
        body_style
    )
)


# ============================================================
# 28. INTERACTIVE GIS MAP
# ============================================================

story.append(
    Paragraph(
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
        heading_style
    )
)


workflow = [

    "Data collection",

    "Data cleaning",

    "Satellite data acquisition",

    "Satellite preprocessing",

    "All-band processing",

    "NDVI / NDBI / NDWI generation",

    "LULC analysis",

    "Built-up and green-cover analysis",

    "Flood-risk analysis",

    "Heatmap analysis",

    "Feature engineering",

    "Machine learning",

    "Prediction",

    "Interactive GIS visualization",

    "Power BI dashboard",

    "Urban planning decision support",

    "Future automated data updates"

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
# 30. KEY FINDINGS
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "14. Key Findings",
        heading_style
    )
)


findings = [

    f"The infrastructure dataset contains "
    f"{building_count} building records.",

    f"The healthcare dataset contains "
    f"{hospital_count} hospital records.",

    f"The education dataset contains "
    f"{school_count} school records.",

    f"The parks dataset contains "
    f"{park_count} park records.",

    f"The road dataset contains "
    f"{road_count} records.",

    f"The water-body dataset contains "
    f"{water_count} records.",

    f"The selected Sentinel-2 scene has "
    f"{cloud_cover}% reported cloud cover.",

    f"The mean NDVI is {mean_ndvi}.",

    f"The mean NDBI is {mean_ndbi}.",

    f"The mean NDWI is {mean_ndwi}.",

    f"Flood-risk records detected: "
    f"{flood_count}.",

    f"Heatmap records detected: "
    f"{heatmap_count}."

]


for finding in findings:

    story.append(
        Paragraph(
            "• " + finding,
            body_style
        )
    )


# ============================================================
# 31. RECOMMENDATIONS
# ============================================================

story.append(
    Paragraph(
        "15. Recommendations",
        heading_style
    )
)


recommendations = [

    "Use the interactive GIS map to inspect spatial "
    "distribution of infrastructure.",

    "Use NDVI to identify vegetation-rich and "
    "vegetation-deficient areas.",

    "Use NDBI to identify highly built-up areas.",

    "Use NDWI and water-body information for "
    "water-resource planning.",

    "Use flood-risk analysis for drainage and "
    "urban-resilience planning.",

    "Use heatmap analysis to identify potential "
    "urban hotspots.",

    "Use ML priority classifications to identify "
    "areas requiring planning attention.",

    "Use Power BI for executive-level monitoring "
    "and comparative analysis.",

    "Use multi-date satellite observations to "
    "monitor changes over time.",

    "Integrate official MRSAC datasets wherever "
    "available for production-level analysis.",

    "Maintain year/date information so that future "
    "observations can be compared with historical data."

]


for recommendation in recommendations:

    story.append(
        Paragraph(
            "• " + recommendation,
            body_style
        )
    )


# ============================================================
# 32. LIMITATIONS
# ============================================================

story.append(
    Paragraph(
        "16. Limitations",
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

    "Flood and heatmap outputs depend on the underlying "
    "input datasets and processing methods.",

    "Machine-learning predictions depend on the quality "
    "and representativeness of the training dataset.",

    "Infrastructure records should be validated against "
    "authoritative datasets before operational deployment.",

    "Future-date information cannot be known until new "
    "observations or datasets become available."

]


for limitation in limitations:

    story.append(
        Paragraph(
            "• " + limitation,
            body_style
        )
    )


# ============================================================
# 33. CONCLUSION
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "17. Conclusion",
        heading_style
    )
)


conclusion = """

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
analytical dashboards for decision-makers.

Future development can include multi-date satellite
monitoring, improved administrative boundaries, official
MRSAC datasets, advanced machine-learning models and
automated acquisition of newly available observations.

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
# 34. TECHNICAL INFORMATION
# ============================================================

story.append(
    Paragraph(
        "18. Technical Information",
        heading_style
    )
)


technical = [

    ["Programming", "Python"],

    ["Satellite", "Sentinel-2"],

    ["Product", "Sentinel-2 Level-2A"],

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
# 35. BUILD PDF
# ============================================================

print()
print(
    "Generating PDF..."
)


try:

    doc.build(
        story
    )

except Exception as e:

    print()
    print(
        "ERROR WHILE CREATING PDF"
    )

    print(
        e
    )

    raise


# ============================================================
# 36. FINAL
# ============================================================

print()
print("=" * 70)
print("       PROFESSIONAL REPORT COMPLETED")
print("=" * 70)
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