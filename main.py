import os
import warnings
import pandas as pd
import geopandas as gpd
import osmnx as ox

warnings.filterwarnings("ignore")

# ============================================================
# GEOTWINAI - NAGPUR OSM DATA COLLECTION
# Output: D:\GeoTwinAI_Final\output\
# ============================================================

# ------------------------------------------------------------
# 1. PROJECT PATH
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ------------------------------------------------------------
# 2. OSM SETTINGS
# ------------------------------------------------------------

ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.requests_timeout = 180

PLACE = "Nagpur, Maharashtra, India"

print("\n" + "=" * 65)
print("              GEOTWINAI - NAGPUR")
print("        OPENSTREETMAP DATA COLLECTION")
print("=" * 65)

print("\nOutput folder:")
print(OUTPUT_DIR)

# ------------------------------------------------------------
# 3. REGION CLASSIFICATION
# ------------------------------------------------------------
#
# IMPORTANT:
# Central / North / South / East / West are
# analytical project regions, NOT official Nagpur wards.
#
# Central = approximately central 4 km radius
# Outside central area -> based on direction from Nagpur centre
#
# This is useful for Power BI filtering.
# ------------------------------------------------------------

NAGPUR_LAT = 21.1458
NAGPUR_LON = 79.0882

CENTRAL_RADIUS_KM = 4.0


def add_region(gdf):

    if gdf.empty:
        return gdf

    gdf = gdf.copy()

    # Ensure geographic CRS
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)

    # Convert to projected CRS before centroid calculation
    projected = gdf.to_crs(epsg=32644)

    centroid = projected.geometry.centroid

    # Convert centroid back to WGS84
    centroid_wgs84 = gpd.GeoSeries(
        centroid,
        crs="EPSG:32644"
    ).to_crs(epsg=4326)

    gdf["Latitude"] = centroid_wgs84.y.values
    gdf["Longitude"] = centroid_wgs84.x.values

    # Difference in approximate kilometres
    dx = (
        (gdf["Longitude"] - NAGPUR_LON)
        * 111
        * 0.94
    )

    dy = (
        (gdf["Latitude"] - NAGPUR_LAT)
        * 111
    )

    distance = (dx ** 2 + dy ** 2) ** 0.5

    regions = []

    for x, y, d in zip(dx, dy, distance):

        # Central area
        if d <= CENTRAL_RADIUS_KM:
            regions.append("Central")

        # Outside central area
        elif abs(x) >= abs(y):

            if x >= 0:
                regions.append("East")
            else:
                regions.append("West")

        else:

            if y >= 0:
                regions.append("North")
            else:
                regions.append("South")

    gdf["Region"] = regions

    return gdf


# ------------------------------------------------------------
# 4. SAVE FUNCTION
# ------------------------------------------------------------

def save_csv(gdf, filename):

    if gdf is None or gdf.empty:

        print(f"\nWARNING: No data found for {filename}")

        return

    gdf = add_region(gdf)

    # Convert geometry into readable WKT
    gdf["geometry"] = gdf.geometry.astype(str)

    # Save
    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    gdf.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nSaved: {output_path}")
    print(f"Records: {len(gdf)}")

    print("\nRegion distribution:")

    print(
        gdf["Region"]
        .value_counts()
    )


# ============================================================
# 5. ROADS
# ============================================================

print("\n" + "-" * 65)
print("1. Downloading Roads...")
print("-" * 65)

try:

    graph = ox.graph_from_place(
        PLACE,
        network_type="drive",
        simplify=True
    )

    nodes, edges = ox.graph_to_gdfs(
        graph
    )

    # Keep useful columns where available
    roads = edges.copy()

    save_csv(
        roads,
        "Nagpur_Roads.csv"
    )

except Exception as e:

    print("\nERROR while downloading Roads:")
    print(e)


# ============================================================
# 6. BUILDINGS
# ============================================================

print("\n" + "-" * 65)
print("2. Downloading Buildings...")
print("-" * 65)

try:

    buildings = ox.features_from_place(
        PLACE,
        tags={
            "building": True
        }
    )

    save_csv(
        buildings,
        "Nagpur_Buildings.csv"
    )

except Exception as e:

    print("\nERROR while downloading Buildings:")
    print(e)


# ============================================================
# 7. SCHOOLS
# ============================================================

print("\n" + "-" * 65)
print("3. Downloading Schools...")
print("-" * 65)

try:

    schools = ox.features_from_place(
        PLACE,
        tags={
            "amenity": "school"
        }
    )

    save_csv(
        schools,
        "Nagpur_Schools.csv"
    )

except Exception as e:

    print("\nERROR while downloading Schools:")
    print(e)


# ============================================================
# 8. HOSPITALS
# ============================================================

print("\n" + "-" * 65)
print("4. Downloading Hospitals...")
print("-" * 65)

try:

    hospitals = ox.features_from_place(
        PLACE,
        tags={
            "amenity": "hospital"
        }
    )

    save_csv(
        hospitals,
        "Nagpur_Hospitals.csv"
    )

except Exception as e:

    print("\nERROR while downloading Hospitals:")
    print(e)


# ============================================================
# 9. PARKS
# ============================================================

print("\n" + "-" * 65)
print("5. Downloading Parks...")
print("-" * 65)

try:

    parks = ox.features_from_place(
        PLACE,
        tags={
            "leisure": "park"
        }
    )

    save_csv(
        parks,
        "Nagpur_Parks.csv"
    )

except Exception as e:

    print("\nERROR while downloading Parks:")
    print(e)


# ============================================================
# 10. WATER BODIES
# ============================================================

print("\n" + "-" * 65)
print("6. Downloading Water Bodies...")
print("-" * 65)

try:

    water = ox.features_from_place(
        PLACE,
        tags={
            "natural": "water"
        }
    )

    save_csv(
        water,
        "Nagpur_WaterBodies.csv"
    )

except Exception as e:

    print("\nERROR while downloading Water Bodies:")
    print(e)


# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 65)
print("              DATA COLLECTION COMPLETED")
print("=" * 65)

print("\nCSV files created in:")

print(OUTPUT_DIR)

print("\nDatasets:")

print("Nagpur_Roads.csv")
print("Nagpur_Buildings.csv")
print("Nagpur_Schools.csv")
print("Nagpur_Hospitals.csv")
print("Nagpur_Parks.csv")
print("Nagpur_WaterBodies.csv")

print("\nRegions available for Power BI:")

print("Central")
print("North")
print("South")
print("East")
print("West")

print("\n" + "=" * 65)
print("          READY FOR POWER BI REGIONAL FILTERING")
print("=" * 65)