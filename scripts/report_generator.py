# ============================================================
# GEOTWINAI
# PROFESSIONAL REPORT GENERATOR
#
# Project:
# AI-Powered Digital Twin for Smart Cities
#
# Study Area:
# Nagpur, Maharashtra
#
# Output:
# output/reports/GeoTwinAI_Nagpur_Professional_Report.pdf
# ============================================================

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image
)

warnings.filterwarnings("ignore")


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

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

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "GeoTwinAI_Nagpur_Professional_Report.pdf"
)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def find_file(folder, names):

    if not os.path.exists(folder):
        return None

    for name in names:

        path = os.path.join(folder, name)

        if os.path.exists(path):
            return path

    return None


def safe_read_csv(path):

    if path is None:
        return None

    try:
        return pd.read_csv(path)

    except Exception as e:

        print("Could not read:")
        print(path)
        print("Reason:", e)

        return None


def fmt(value, digits=2):

    try:

        if pd.isna(value):
            return "N/A"

        return f"{float(value):.{digits}f}"

    except Exception:
        return "N/A"


def count_rows(df):

    if df is None:
        return 0

    return len(df)


def safe_mean(df, column):

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


# ============================================================
# 3. START
# ============================================================

print()
print("=" * 70)
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


building_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Building_Clean.csv",
        "Nagpur_Buildings_Clean.csv",
        "Nagpur_Building_clean.csv",
        "Nagpur_building_clean.csv"
    ]
)


hospital_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Hospital_Clean.csv",
        "Nagpur_Hospitals_Clean.csv",
        "Nagpur_Hospital_clean.csv",
        "Nagpur_hospital_clean.csv"
    ]
)


school_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_School_Clean.csv",
        "Nagpur_Schools_Clean.csv",
        "Nagpur_School_clean.csv",
        "Nagpur_school_clean.csv"
    ]
)


park_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Park_Clean.csv",
        "Nagpur_Parks_Clean.csv",
        "Nagpur_Park_clean.csv",
        "Nagpur_park_clean.csv"
    ]
)


road_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Road_Clean.csv",
        "Nagpur_Roads_Clean.csv",
        "Nagpur_Road_clean.csv",
        "Nagpur_road_clean.csv"
    ]
)


water_file = find_file(
    PROCESSED_DIR,
    [
        "Nagpur_Water_Bodies_Clean.csv",
        "Nagpur_Water_Body_Clean.csv",
        "Nagpur_Water_Bodies_clean.csv",
        "Nagpur_water_bodies_clean.csv"
    ]
)


# ============================================================
# 5. LOCATE SATELLITE DATASETS
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


# ============================================================
# 6. LOCATE SATELLITE INDEX FILES
# ============================================================

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
# 7. READ DATA
# ============================================================

print()
print("Reading datasets...")


buildings = safe_read_csv(building_file)

hospitals = safe_read_csv(hospital_file)

schools = safe_read_csv(school_file)

parks = safe_read_csv(park_file)

roads = safe_read_csv(road_file)

water = safe_read_csv(water_file)

bands_summary = safe_read_csv(all_bands_file)

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

        if "Cloud_Cover_Percent" in bands_summary.columns:

            cloud_cover = fmt(
                row["Cloud_Cover_Percent"],
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


# ============================================================
# 10. CALCULATE INDICES FROM SPATIAL DATA IF NEEDED
# ============================================================

if bands_spatial is not None:

    if mean_ndvi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDVI"
        )

        if value is not None:
            mean_ndvi = fmt(value, 4)


    if mean_ndbi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDBI"
        )

        if value is not None:
            mean_ndbi = fmt(value, 4)


    if mean_ndwi == "N/A":

        value = safe_mean(
            bands_spatial,
            "NDWI"
        )

        if value is not None:
            mean_ndwi = fmt(value, 4)


# ============================================================
# 11. INFRASTRUCTURE CHART
# ============================================================

print()
print("Creating infrastructure chart...")


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


INFRA_CHART = os.path.join(
    CHART_DIR,
    "infrastructure_summary.png"
)


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
# ============================================================

NDVI_CHART = None


if bands_spatial is not None:

    if "NDVI" in bands_spatial.columns:

        ndvi_values = pd.to_numeric(
            bands_spatial["NDVI"],
            errors="coerce"
        ).dropna()


        if len(ndvi_values) > 0:

            print(
                "Creating NDVI distribution chart..."
            )

            NDVI_CHART = os.path.join(
                CHART_DIR,
                "ndvi_distribution.png"
            )


            plt.figure(
                figsize=(10, 6)
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
# 13. PDF DOCUMENT
# ============================================================

print()
print("Building professional PDF...")


doc = SimpleDocTemplate(

    REPORT_FILE,

    pagesize=A4,

    rightMargin=18 * mm,

    leftMargin=18 * mm,

    topMargin=18 * mm,

    bottomMargin=18 * mm
)


# ============================================================
# 14. STYLES
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
# 15. COVER PAGE
# ============================================================

story.append(
    Spacer(
        1,
        35 * mm
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
        10 * mm
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
        20 * mm
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
            "<b>Satellite Dataset</b>",
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
            "<b>Analysis Resolution</b>",
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
        20 * mm
    )
)


story.append(
    Paragraph(
        "GeoTwinAI integrates geospatial datasets, "
        "satellite-derived indicators and machine learning "
        "to support urban planning and smart-city "
        "decision-making.",
        center_style
    )
)


story.append(
    PageBreak()
)


# ============================================================
# 16. EXECUTIVE SUMMARY
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
"""


story.append(
    Paragraph(
        executive_text,
        body_style
    )
)


# ============================================================
# 17. PROJECT OBJECTIVES
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

    "Identify built-up and water-related characteristics.",

    "Map important urban infrastructure.",

    "Create machine-learning-based urban priority analysis.",

    "Provide interactive GIS visualization.",

    "Provide analytical dashboards through Power BI.",

    "Support data-driven urban planning decisions."

]


for objective in objectives:

    story.append(
        Paragraph(
            "• " + objective,
            body_style
        )
    )


# ============================================================
# 18. DATA SOURCES
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
# 19. INFRASTRUCTURE STATISTICS
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


if os.path.exists(INFRA_CHART):

    story.append(
        Image(
            INFRA_CHART,
            width=165 * mm,
            height=95 * mm
        )
    )


# ============================================================
# 20. SATELLITE ANALYSIS
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

The processed dataset includes B01, B02, B03, B04, B05,
B06, B07, B08, B8A, B09, B11 and B12.
"""


story.append(
    Paragraph(
        satellite_text,
        body_style
    )
)


# ============================================================
# 21. SPECTRAL INDICES
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
            height=95 * mm
        )
    )


# ============================================================
# 22. ALL BAND ANALYSIS
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

These bands support vegetation, water, soil, built-up
and land-cover analysis.
"""


story.append(
    Paragraph(
        all_band_text,
        body_style
    )
)


# ============================================================
# 23. MACHINE LEARNING
# ============================================================

story.append(
    Paragraph(
        "8. Machine Learning Analysis",
        heading_style
    )
)


ml_text = """
The machine-learning component of GeoTwinAI is designed
to classify urban areas according to planning priority.

The feature-engineering stage combines infrastructure
and environmental attributes into a machine-learning
dataset.

The trained model can generate urban priority
predictions such as High, Medium and Low.

These predictions can support identification of areas
requiring additional infrastructure or environmental
attention.

Model performance should be evaluated using appropriate
classification metrics such as accuracy, precision,
recall and F1-score.
"""


story.append(
    Paragraph(
        ml_text,
        body_style
    )
)


# ============================================================
# 24. DIGITAL TWIN WORKFLOW
# ============================================================

story.append(
    Paragraph(
        "9. GeoTwinAI Workflow",
        heading_style
    )
)


workflow = [

    "Data collection",

    "Data cleaning",

    "Satellite processing",

    "Spectral index generation",

    "Feature engineering",

    "Machine learning",

    "Prediction",

    "Interactive GIS visualization",

    "Power BI dashboard",

    "Urban planning decision support"

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
# 25. KEY FINDINGS
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "10. Key Findings",
        heading_style
    )
)


findings = [

    f"The processed infrastructure datasets contain "
    f"{building_count} building records.",

    f"The healthcare dataset contains "
    f"{hospital_count} hospital records.",

    f"The education dataset contains "
    f"{school_count} school records.",

    f"The parks dataset contains "
    f"{park_count} park records.",

    f"The water-body dataset contains "
    f"{water_count} records.",

    f"The selected Sentinel-2 scene has "
    f"{cloud_cover}% reported cloud cover.",

    f"The mean NDVI is "
    f"{mean_ndvi}.",

    f"The mean NDBI is "
    f"{mean_ndbi}.",

    f"The mean NDWI is "
    f"{mean_ndwi}."

]


for finding in findings:

    story.append(
        Paragraph(
            "• " + finding,
            body_style
        )
    )


# ============================================================
# 26. RECOMMENDATIONS
# ============================================================

story.append(
    Paragraph(
        "11. Recommendations",
        heading_style
    )
)


recommendations = [

    "Use the interactive GIS map to inspect spatial "
    "distribution of infrastructure.",

    "Use NDVI to identify vegetation-rich and "
    "vegetation-deficient areas.",

    "Use NDBI to identify highly built-up areas.",

    "Use NDWI and water-body data to support "
    "water-resource planning.",

    "Use ML priority classifications to identify "
    "areas requiring planning attention.",

    "Use Power BI for executive-level monitoring "
    "and comparative analysis.",

    "Periodically update Sentinel-2 observations "
    "to monitor urban environmental change.",

    "Integrate official MRSAC datasets wherever "
    "available for production-level analysis."

]


for recommendation in recommendations:

    story.append(
        Paragraph(
            "• " + recommendation,
            body_style
        )
    )


# ============================================================
# 27. LIMITATIONS
# ============================================================

story.append(
    Paragraph(
        "12. Limitations",
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

    "The current analysis uses one selected best-available "
    "scene rather than a full temporal time series.",

    "Machine-learning predictions depend on the quality "
    "and representativeness of the training dataset.",

    "Infrastructure records should be validated against "
    "authoritative datasets before operational deployment."

]


for limitation in limitations:

    story.append(
        Paragraph(
            "• " + limitation,
            body_style
        )
    )


# ============================================================
# 28. CONCLUSION
# ============================================================

story.append(
    PageBreak()
)


story.append(
    Paragraph(
        "13. Conclusion",
        heading_style
    )
)


conclusion = """
GeoTwinAI provides a unified framework for combining
geospatial infrastructure data, satellite remote sensing
and machine learning for smart-city planning.

The integration of Sentinel-2 spectral information,
environmental indices, infrastructure datasets and
machine-learning predictions provides a spatially
oriented view of urban conditions.

The interactive GIS map provides detailed spatial
exploration, while Power BI provides higher-level
analytical dashboards for decision-makers.

Future development can include multi-date satellite
monitoring, improved administrative boundaries, official
MRSAC datasets, advanced machine-learning models and
automated data updates.

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
# 29. TECHNICAL INFORMATION
# ============================================================

story.append(
    Paragraph(
        "14. Technical Information",
        heading_style
    )
)


technical = [

    ["Programming", "Python"],

    ["Satellite", "Sentinel-2"],

    ["Product", "Sentinel-2 Level-2A"],

    ["Satellite Source", "Microsoft Planetary Computer"],

    ["Spatial Reference Grid", "10 metres"],

    ["Indices", "NDVI, NDBI, NDWI"],

    ["GIS Visualization", "Interactive HTML Map"],

    ["Dashboard", "Microsoft Power BI"],

    ["Machine Learning", "Urban Priority Classification"],

    ["Report Format", "PDF"]

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
# 30. BUILD PDF
# ============================================================

print()
print("Generating PDF...")


try:

    doc.build(story)

except Exception as e:

    print()
    print("ERROR WHILE CREATING PDF")
    print(e)

    raise


# ============================================================
# 31. FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print("       PROFESSIONAL REPORT COMPLETED")
print("=" * 70)

print()

print("Report created:")

print(REPORT_FILE)

print()

print("Report folder:")

print(REPORT_DIR)

print()

print("=" * 70)



