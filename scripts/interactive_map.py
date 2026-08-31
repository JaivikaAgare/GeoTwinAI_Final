# ============================================================
# GEOTWINAI
# INTERACTIVE NAGPUR DIGITAL TWIN MAP
#
# Layers:
#   Buildings
#   Hospitals
#   Schools
#   Parks
#   Roads
#   Water Bodies
#   Sentinel-2 NDVI
#
# Output:
#   output/Nagpur_Interactive_Map.html
# ============================================================

import os
import warnings

import pandas as pd
import folium
from folium.plugins import HeatMap

warnings.filterwarnings("ignore")


# ============================================================
# 1. PROJECT PATH
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

MAP_FILE = os.path.join(
    OUTPUT_DIR,
    "Nagpur_Interactive_Map.html"
)


# ============================================================
# 2. NAGPUR CENTER
# ============================================================

NAGPUR_LAT = 21.1458
NAGPUR_LON = 79.0882


# ============================================================
# 3. START MAP
# ============================================================

print()
print("=" * 70)
print("       GEOTWINAI - INTERACTIVE NAGPUR DIGITAL TWIN")
print("=" * 70)

print()
print("Project:")
print(BASE_DIR)

print()
print("Creating map...")


m = folium.Map(
    location=[
        NAGPUR_LAT,
        NAGPUR_LON
    ],
    zoom_start=11,
    control_scale=True
)


# ============================================================
# 4. HELPER FUNCTION
# ============================================================

def find_csv(possible_names):

    for filename in possible_names:

        path = os.path.join(
            PROCESSED_DIR,
            filename
        )

        if os.path.exists(path):

            return path


    return None


def add_points_layer(
    csv_path,
    layer_name,
    marker_color,
    popup_columns
):

    if csv_path is None:

        print(
            f"{layer_name}: CSV not found"
        )

        return


    print(
        f"Loading {layer_name}..."
    )


    df = pd.read_csv(
        csv_path
    )


    # --------------------------------------------------------
    # Find latitude / longitude columns
    # --------------------------------------------------------

    lat_column = None
    lon_column = None


    for column in df.columns:

        name = column.lower().strip()


        if name in [
            "latitude",
            "lat"
        ]:

            lat_column = column


        if name in [
            "longitude",
            "lon",
            "lng"
        ]:

            lon_column = column


    if (
        lat_column is None
        or lon_column is None
    ):

        print(
            f"WARNING: Coordinates not found in {layer_name}"
        )

        print(
            "Columns:",
            list(df.columns)
        )

        return


    layer = folium.FeatureGroup(
        name=layer_name,
        show=True
    )


    count = 0


    for _, row in df.iterrows():

        try:

            latitude = float(
                row[lat_column]
            )

            longitude = float(
                row[lon_column]
            )

        except:

            continue


        if (
            pd.isna(latitude)
            or pd.isna(longitude)
        ):

            continue


        popup_text = (
            f"<b>{layer_name}</b><br>"
        )


        for column in popup_columns:

            if column in df.columns:

                value = row[column]

                if pd.notna(value):

                    popup_text += (
                        f"<b>{column}:</b> "
                        f"{value}<br>"
                    )


        folium.CircleMarker(

            location=[
                latitude,
                longitude
            ],

            radius=4,

            color=marker_color,

            fill=True,

            fill_opacity=0.75,

            popup=folium.Popup(
                popup_text,
                max_width=350
            )

        ).add_to(layer)


        count += 1


    layer.add_to(m)


    print(
        f"{layer_name}: {count} locations added"
    )


# ============================================================
# 5. BUILDINGS
# ============================================================

building_csv = find_csv([
    "Nagpur_Building_Clean.csv",
    "Nagpur_Buildings_Clean.csv",
    "Nagpur_Building_clean.csv",
    "Nagpur_building_clean.csv"
])


add_points_layer(

    building_csv,

    "Buildings",

    "blue",

    [
        "Name",
        "name",
        "building_type",
        "Building_Type",
        "area",
        "Area"
    ]
)


# ============================================================
# 6. HOSPITALS
# ============================================================

hospital_csv = find_csv([
    "Nagpur_Hospital_Clean.csv",
    "Nagpur_Hospitals_Clean.csv",
    "Nagpur_Hospital_clean.csv"
])


add_points_layer(

    hospital_csv,

    "Hospitals",

    "red",

    [
        "Name",
        "name",
        "hospital",
        "Hospital",
        "type",
        "Type"
    ]
)


# ============================================================
# 7. SCHOOLS
# ============================================================

school_csv = find_csv([
    "Nagpur_School_Clean.csv",
    "Nagpur_Schools_Clean.csv",
    "Nagpur_School_clean.csv"
])


add_points_layer(

    school_csv,

    "Schools",

    "purple",

    [
        "Name",
        "name",
        "school",
        "School",
        "type",
        "Type"
    ]
)


# ============================================================
# 8. PARKS
# ============================================================

park_csv = find_csv([
    "Nagpur_Park_Clean.csv",
    "Nagpur_Parks_Clean.csv",
    "Nagpur_Park_clean.csv"
])


add_points_layer(

    park_csv,

    "Parks",

    "green",

    [
        "Name",
        "name",
        "park",
        "Park",
        "type",
        "Type"
    ]
)


# ============================================================
# 9. WATER BODIES
# ============================================================

water_csv = find_csv([
    "Nagpur_Water_Bodies_Clean.csv",
    "Nagpur_Water_Body_Clean.csv",
    "Nagpur_Water_Bodies_clean.csv"
])


add_points_layer(

    water_csv,

    "Water Bodies",

    "cadetblue",

    [
        "Name",
        "name",
        "waterbody",
        "Water_Body",
        "type",
        "Type"
    ]
)


# ============================================================
# 10. ROADS
# ============================================================

road_csv = find_csv([
    "Nagpur_Road_Clean.csv",
    "Nagpur_Roads_Clean.csv",
    "Nagpur_Road_clean.csv"
])


if road_csv is not None:

    print(
        "Loading Roads..."
    )


    road_df = pd.read_csv(
        road_csv
    )


    road_layer = folium.FeatureGroup(
        name="Roads",
        show=False
    )


    # --------------------------------------------------------
    # Check for latitude/longitude
    # --------------------------------------------------------

    lat_column = None
    lon_column = None


    for column in road_df.columns:

        name = column.lower().strip()


        if name in [
            "latitude",
            "lat"
        ]:

            lat_column = column


        if name in [
            "longitude",
            "lon",
            "lng"
        ]:

            lon_column = column


    if (
        lat_column is not None
        and lon_column is not None
    ):

        road_points = []


        for _, row in road_df.iterrows():

            try:

                lat = float(
                    row[lat_column]
                )

                lon = float(
                    row[lon_column]
                )

                if (
                    pd.notna(lat)
                    and pd.notna(lon)
                ):

                    road_points.append(
                        [lat, lon]
                    )

            except:

                continue


        if road_points:

            folium.PolyLine(

                road_points,

                weight=2,

                opacity=0.6,

                popup="Nagpur Roads"

            ).add_to(
                road_layer
            )


            print(
                "Road coordinates added:",
                len(road_points)
            )


    else:

        print(
            "Road latitude/longitude columns not found."
        )


    road_layer.add_to(
        m
    )


else:

    print(
        "Road CSV not found."
    )


# ============================================================
# 11. NDVI POINT / HEATMAP
# ============================================================

print()
print("Loading Sentinel-2 NDVI data...")


ndvi_csv = os.path.join(

    SATELLITE_DIR,

    "Nagpur_Sentinel2_AllBands_Spatial.csv"
)


if os.path.exists(
    ndvi_csv
):

    ndvi_df = pd.read_csv(
        ndvi_csv
    )


    print(
        "NDVI records:",
        len(ndvi_df)
    )


    required_columns = [
        "Latitude",
        "Longitude",
        "NDVI"
    ]


    if all(
        column in ndvi_df.columns
        for column in required_columns
    ):

        ndvi_df = ndvi_df.dropna(
            subset=required_columns
        )


        # ----------------------------------------------------
        # NDVI heatmap
        # ----------------------------------------------------

        ndvi_layer = folium.FeatureGroup(
            name="NDVI Heatmap",
            show=False
        )


        heat_data = []


        # Limit points so browser does not become too slow.

        sample_size = min(
            50000,
            len(ndvi_df)
        )


        sample_df = ndvi_df.sample(
            sample_size,
            random_state=42
        )


        for _, row in sample_df.iterrows():

            try:

                lat = float(
                    row["Latitude"]
                )

                lon = float(
                    row["Longitude"]
                )

                ndvi = float(
                    row["NDVI"]
                )


                # Convert NDVI
                # from -1..1
                # into 0..1
                intensity = (
                    ndvi + 1
                ) / 2


                heat_data.append(
                    [
                        lat,
                        lon,
                        intensity
                    ]
                )

            except:

                continue


        if heat_data:

            HeatMap(

                heat_data,

                radius=10,

                blur=15,

                min_opacity=0.3,

                max_zoom=13

            ).add_to(
                ndvi_layer
            )


        ndvi_layer.add_to(
            m
        )


        print(
            "NDVI heatmap created."
        )


    else:

        print(
            "NDVI CSV does not contain required columns."
        )


else:

    print(
        "Sentinel-2 all-band CSV not found."
    )


# ============================================================
# 12. LAYER CONTROL
# ============================================================

folium.LayerControl(
    collapsed=False
).add_to(
    m
)


# ============================================================
# 13. FULLSCREEN
# ============================================================

from folium.plugins import Fullscreen


Fullscreen(
    position="topright"
).add_to(
    m
)


# ============================================================
# 14. SAVE MAP
# ============================================================

print()
print("Saving interactive map...")


m.save(
    MAP_FILE
)


print()
print("=" * 70)
print("             MAP COMPLETED")
print("=" * 70)

print()

print(
    "Interactive map:"
)

print(
    MAP_FILE
)

print()

print(
    "Open this HTML file in Google Chrome."
)

print()
print("=" * 70)

