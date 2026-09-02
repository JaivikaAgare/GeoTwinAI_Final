# ============================================================
<<<<<<< HEAD
# GEOTWINAI - FAST 5-CLUSTER INTERACTIVE MAP
# Nagpur, Maharashtra
#
# IMPORTANT:
# - Buildings / Hospitals / Schools / Parks / Water Bodies / Roads
#   are kept as clickable infrastructure layers.
# - Environmental layers are represented by ONLY 5 polygons:
#   North, South, East, West, Central.
# - Raw satellite pixels are NEVER embedded in the HTML.
# - Cluster statistics are cached in output/satellite/cluster_cache.csv
#   so the next map generation is much faster.
# ============================================================

import os
import html
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import folium
from folium.plugins import MarkerCluster, Fullscreen, MeasureControl
from branca.colormap import LinearColormap

warnings.filterwarnings("ignore")

# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = OUTPUT_DIR / "processed"
SATELLITE_DIR = OUTPUT_DIR / "satellite"
MAP_FILE = OUTPUT_DIR / "Nagpur_Interactive_Map.html"
CACHE_FILE = SATELLITE_DIR / "cluster_cache.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SATELLITE_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------
# NAGPUR EXTENT / FIVE CLUSTERS
# ------------------------------------------------------------
MIN_LON, MIN_LAT = 78.95, 21.05
MAX_LON, MAX_LAT = 79.20, 21.25
CENTRAL_LEFT, CENTRAL_RIGHT = 79.05, 79.13
CENTRAL_BOTTOM, CENTRAL_TOP = 21.11, 21.18
CENTER = [21.1458, 79.0882]
CLUSTERS = ["North", "South", "East", "West", "Central"]

POLYGONS = {
    "North": [[CENTRAL_TOP, MIN_LON], [MAX_LAT, MIN_LON], [MAX_LAT, MAX_LON], [CENTRAL_TOP, MAX_LON]],
    "South": [[MIN_LAT, MIN_LON], [CENTRAL_BOTTOM, MIN_LON], [CENTRAL_BOTTOM, MAX_LON], [MIN_LAT, MAX_LON]],
    "West": [[CENTRAL_BOTTOM, MIN_LON], [CENTRAL_TOP, MIN_LON], [CENTRAL_TOP, CENTRAL_LEFT], [CENTRAL_BOTTOM, CENTRAL_LEFT]],
    "East": [[CENTRAL_BOTTOM, CENTRAL_RIGHT], [CENTRAL_TOP, CENTRAL_RIGHT], [CENTRAL_TOP, MAX_LON], [CENTRAL_BOTTOM, MAX_LON]],
    "Central": [[CENTRAL_BOTTOM, CENTRAL_LEFT], [CENTRAL_TOP, CENTRAL_LEFT], [CENTRAL_TOP, CENTRAL_RIGHT], [CENTRAL_BOTTOM, CENTRAL_RIGHT]],
}

# Keep the infrastructure behaviour you liked.
MAX_BUILDINGS = 2500
MAX_MARKERS = 1500
MAX_ROADS = 1200
MAX_WATER = 400

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def find(folder, names):
    folder = Path(folder)
    if not folder.exists():
        return None
    for name in names:
        p = folder / name
        if p.exists():
            return p
    return None


def find_any(folder, terms, extensions=None):
    """Find a file whose name contains every term."""
    folder = Path(folder)
    if not folder.exists():
        return None
    extensions = [e.lower() for e in (extensions or [])]
    for p in folder.iterdir():
        if not p.is_file():
            continue
        low = p.name.lower()
        if extensions and p.suffix.lower() not in extensions:
            continue
        if all(str(t).lower() in low for t in terms):
            return p
    return None


def read_csv(path, usecols=None):
    if not path:
        return None
    try:
        return pd.read_csv(path, usecols=usecols, low_memory=False)
    except Exception as e:
        print(f"Could not read {path}: {e}")
        return None


def read_header(path):
    if not path:
        return []
    try:
        return pd.read_csv(path, nrows=0).columns.tolist()
    except Exception:
        return []


def coord_cols(df):
    if df is None:
        return None, None
    lat = next((c for c in ["Latitude", "latitude", "lat", "LAT"] if c in df.columns), None)
    lon = next((c for c in ["Longitude", "longitude", "lon", "lng", "LON"] if c in df.columns), None)
    return lat, lon


def cluster_masks(lat, lon):
    return {
        "North": lat >= CENTRAL_TOP,
        "South": lat < CENTRAL_BOTTOM,
        "West": (lat >= CENTRAL_BOTTOM) & (lat < CENTRAL_TOP) & (lon < CENTRAL_LEFT),
        "East": (lat >= CENTRAL_BOTTOM) & (lat < CENTRAL_TOP) & (lon >= CENTRAL_RIGHT),
        "Central": (lat >= CENTRAL_BOTTOM) & (lat < CENTRAL_TOP) & (lon >= CENTRAL_LEFT) & (lon < CENTRAL_RIGHT),
    }


def cluster_of(lat, lon):
    try:
        lat, lon = float(lat), float(lon)
    except Exception:
        return None
    if lat >= CENTRAL_TOP:
        return "North"
    if lat < CENTRAL_BOTTOM:
        return "South"
    if lon < CENTRAL_LEFT:
        return "West"
    if lon >= CENTRAL_RIGHT:
        return "East"
    return "Central"


def esc(x):
    if x is None:
        return "N/A"
    try:
        if pd.isna(x):
            return "N/A"
    except Exception:
        pass
    return html.escape(str(x))


def fmt(v, d=2):
    try:
        if pd.isna(v):
            return "N/A"
        return f"{float(v):.{d}f}"
    except Exception:
        return str(v)


def popup_table(title, rows):
    s = (
        "<div style='font-family:Arial,sans-serif;min-width:300px;max-width:500px;"
        "font-size:13px'>"
        f"<div style='font-size:17px;font-weight:700;margin-bottom:9px'>{esc(title)}</div>"
        "<table style='width:100%;border-collapse:collapse'>"
    )
    for k, v in rows:
        s += (
            "<tr>"
            f"<td style='padding:5px 7px;border-bottom:1px solid #ddd;font-weight:700;width:45%'>{esc(k)}</td>"
            f"<td style='padding:5px 7px;border-bottom:1px solid #ddd'>{esc(v)}</td>"
            "</tr>"
        )
    return s + "</table></div>"


def empty_stats():
    return {
        c: {
            "Cluster": c,
            "Buildings": 0,
            "Hospitals": 0,
            "Schools": 0,
            "Parks": 0,
            "Water Bodies": 0,
        }
        for c in CLUSTERS
    }


# ------------------------------------------------------------
# DATA FILE DISCOVERY
# ------------------------------------------------------------
print("=" * 72)
print("GEOTWINAI - FAST 5-CLUSTER INTERACTIVE MAP")
print("Project:", BASE_DIR)
print("=" * 72)

building_file = find(PROCESSED_DIR, [
    "Nagpur_Buildings_Clean.csv", "Nagpur_Building_Clean.csv", "Nagpur_Buildings.csv"
])
hospital_file = find(PROCESSED_DIR, [
    "Nagpur_Hospitals_Clean.csv", "Nagpur_Hospital_Clean.csv", "Nagpur_Hospitals.csv"
])
school_file = find(PROCESSED_DIR, [
    "Nagpur_Schools_Clean.csv", "Nagpur_School_Clean.csv", "Nagpur_Schools.csv"
])
park_file = find(PROCESSED_DIR, [
    "Nagpur_Parks_Clean.csv", "Nagpur_Park_Clean.csv", "Nagpur_Parks.csv"
])
road_file = find(PROCESSED_DIR, [
    "Nagpur_Roads_Clean.csv", "Nagpur_Road_Clean.csv", "Nagpur_Roads.csv"
])
water_file = find(PROCESSED_DIR, [
    "Nagpur_WaterBodies_Clean.csv", "Nagpur_Water_Bodies_Clean.csv", "Nagpur_WaterBodies.csv"
])

# Broad environmental filename search prevents "file not found" merely because
# the user's filename differs slightly from the original expected name.
def first_existing(*candidates):
    for p in candidates:
        if p and Path(p).exists():
            return Path(p)
    return None

ndvi_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Sentinel2_NDVI_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_NDVI_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["ndvi", "spatial"], [".csv"]),
)
green_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_GreenCover_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Green_Cover_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["green", "spatial"], [".csv"]),
)
ndbi_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_NDBI_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_BuiltUp_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["ndbi", "spatial"], [".csv"]),
)
ndwi_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_NDWI_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["ndwi", "spatial"], [".csv"]),
)
flood_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_FloodRisk_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Flood_Risk_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["flood", "spatial"], [".csv"]),
)
heat_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Heatmap_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_UrbanHeat_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Urban_Heat_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["heat", "spatial"], [".csv"]),
)
carbon_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Carbon_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_CarbonStorage_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Carbon_Storage_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["carbon", "spatial"], [".csv"]),
)
allbands_file = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Sentinel2_AllBands_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Sentinel-2_AllBands_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["allbands", "spatial"], [".csv"]),
)

ndvi_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Sentinel2_NDVI_Summary.csv"]),
    find_any(SATELLITE_DIR, ["ndvi", "summary"], [".csv"]),
)
green_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_GreenCover_Summary.csv"]),
    find_any(SATELLITE_DIR, ["green", "summary"], [".csv"]),
)
ndbi_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_BuiltUp_Summary.csv"]),
    find(SATELLITE_DIR, ["Nagpur_NDBI_Summary.csv"]),
    find_any(SATELLITE_DIR, ["ndbi", "summary"], [".csv"]),
    find_any(SATELLITE_DIR, ["builtup", "summary"], [".csv"]),
)
ndwi_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_NDWI_Summary.csv"]),
    find_any(SATELLITE_DIR, ["ndwi", "summary"], [".csv"]),
)
flood_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_FloodRisk_Summary.csv"]),
    find_any(SATELLITE_DIR, ["flood", "summary"], [".csv"]),
)
heat_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Heatmap_Summary.csv"]),
    find(SATELLITE_DIR, ["Nagpur_UrbanHeat_Summary.csv"]),
    find_any(SATELLITE_DIR, ["heat", "summary"], [".csv"]),
)
carbon_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_Carbon_Summary.csv"]),
    find(SATELLITE_DIR, ["Nagpur_CarbonStorage_Summary.csv"]),
    find_any(SATELLITE_DIR, ["carbon", "summary"], [".csv"]),
)
lulc_spatial = first_existing(
    find(SATELLITE_DIR, ["Nagpur_LULC_Spatial.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Land_Use_Spatial.csv"]),
    find_any(SATELLITE_DIR, ["lulc", "spatial"], [".csv"]),
)
lulc_summary = first_existing(
    find(SATELLITE_DIR, ["Nagpur_LULC_Summary.csv"]),
    find(SATELLITE_DIR, ["Nagpur_Land_Use_Summary.csv"]),
    find_any(SATELLITE_DIR, ["lulc", "summary"], [".csv"]),
)

for label, p in [
    ("Buildings", building_file), ("Hospitals", hospital_file), ("Schools", school_file),
    ("Parks", park_file), ("Roads", road_file), ("Water Bodies", water_file),
    ("NDVI spatial", ndvi_file), ("NDBI spatial", ndbi_file), ("NDWI spatial", ndwi_file),
    ("Green Cover spatial", green_file), ("Flood spatial", flood_file),
    ("Heat spatial", heat_file), ("Carbon spatial", carbon_file),
    ("All Bands spatial", allbands_file), ("LULC spatial", lulc_spatial),
]:
    print(f"{label:20} : {'FOUND' if p else 'not found'}")

# ------------------------------------------------------------
# INFRASTRUCTURE DATA
# Do not change the popup structure you liked.
# ------------------------------------------------------------
buildings = read_csv(building_file)
hospitals = read_csv(hospital_file)
schools = read_csv(school_file)
parks = read_csv(park_file)
roads = read_csv(road_file)
water = read_csv(water_file)

stats = empty_stats()


def add_infra_counts(df, key):
    if df is None or df.empty:
        return
    lat, lon = coord_cols(df)
    if not lat or not lon:
        return
    d = df[[lat, lon]].copy()
    d[lat] = pd.to_numeric(d[lat], errors="coerce")
    d[lon] = pd.to_numeric(d[lon], errors="coerce")
    d = d.dropna()
    masks = cluster_masks(d[lat], d[lon])
    for c, mask in masks.items():
        stats[c][key] = int(mask.sum())


add_infra_counts(buildings, "Buildings")
add_infra_counts(hospitals, "Hospitals")
add_infra_counts(schools, "Schools")
add_infra_counts(parks, "Parks")
add_infra_counts(water, "Water Bodies")

# ------------------------------------------------------------
# FAST ENVIRONMENTAL AGGREGATION
# ------------------------------------------------------------
def aggregate_one(path, metric_candidates, output_key, digits=2):
    """Read a spatial CSV ONCE in chunks and calculate 5 means."""
    if not path:
        return False
    header = read_header(path)
    lat = next((c for c in ["Latitude", "latitude", "lat"] if c in header), None)
    lon = next((c for c in ["Longitude", "longitude", "lon", "lng"] if c in header), None)
    metric = next((c for c in metric_candidates if c in header), None)
    if not lat or not lon or not metric:
        print(f"{output_key}: required columns not found in {Path(path).name}")
        return False

    sums = {c: 0.0 for c in CLUSTERS}
    counts = {c: 0 for c in CLUSTERS}

    try:
        for chunk in pd.read_csv(path, usecols=[lat, lon, metric], chunksize=100000, low_memory=False):
            chunk[lat] = pd.to_numeric(chunk[lat], errors="coerce")
            chunk[lon] = pd.to_numeric(chunk[lon], errors="coerce")
            chunk[metric] = pd.to_numeric(chunk[metric], errors="coerce")
            chunk = chunk.replace([np.inf, -np.inf], np.nan).dropna()
            if chunk.empty:
                continue
            masks = cluster_masks(chunk[lat], chunk[lon])
            for c, mask in masks.items():
                vals = chunk.loc[mask, metric]
                if not vals.empty:
                    sums[c] += float(vals.sum())
                    counts[c] += int(vals.size)
        ok = False
        for c in CLUSTERS:
            if counts[c]:
                stats[c][output_key] = fmt(sums[c] / counts[c], digits)
                stats[c][output_key + " Records"] = counts[c]
                ok = True
        print(f"{output_key:20}: {sum(counts.values())} records")
        return ok
    except Exception as e:
        print(f"{output_key}: skipped -> {e}")
        return False


def aggregate_two_band(path, band_a_candidates, band_b_candidates, formula, output_key, digits=4):
    """Calculate an index from two bands in one pass."""
    if not path:
        return False
    header = read_header(path)
    lat = next((c for c in ["Latitude", "latitude", "lat"] if c in header), None)
    lon = next((c for c in ["Longitude", "longitude", "lon", "lng"] if c in header), None)
    a = next((c for c in band_a_candidates if c in header), None)
    b = next((c for c in band_b_candidates if c in header), None)
    if not all([lat, lon, a, b]):
        print(f"{output_key}: bands/coordinates not found")
        return False

    sums = {c: 0.0 for c in CLUSTERS}
    counts = {c: 0 for c in CLUSTERS}
    try:
        for chunk in pd.read_csv(path, usecols=[lat, lon, a, b], chunksize=100000, low_memory=False):
            for col in [lat, lon, a, b]:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
            chunk = chunk.dropna()
            if chunk.empty:
                continue
            chunk["_index"] = formula(chunk[a], chunk[b])
            chunk = chunk.replace([np.inf, -np.inf], np.nan).dropna(subset=["_index"])
            masks = cluster_masks(chunk[lat], chunk[lon])
            for c, mask in masks.items():
                vals = chunk.loc[mask, "_index"]
                if not vals.empty:
                    sums[c] += float(vals.sum())
                    counts[c] += int(vals.size)
        ok = False
        for c in CLUSTERS:
            if counts[c]:
                stats[c][output_key] = fmt(sums[c] / counts[c], digits)
                stats[c][output_key + " Records"] = counts[c]
                ok = True
        print(f"{output_key:20}: calculated from {Path(path).name}")
        return ok
    except Exception as e:
        print(f"{output_key}: calculation failed -> {e}")
        return False


# ------------------------------------------------------------
# CACHE
# ------------------------------------------------------------
METRIC_KEYS = [
    "NDVI Mean", "NDBI Mean", "NDWI Mean", "Green Cover %",
    "Flood Risk Mean", "Heat Mean °C", "Carbon Mean", "LULC Mix"
]


def load_cache():
    if not CACHE_FILE.exists():
        return False
    try:
        df = pd.read_csv(CACHE_FILE)
        if set(CLUSTERS) != set(df["Cluster"].astype(str)):
            return False
        for _, r in df.iterrows():
            c = str(r["Cluster"])
            for key in METRIC_KEYS:
                if key in df.columns and pd.notna(r[key]) and str(r[key]).strip() not in ["", "nan"]:
                    stats[c][key] = str(r[key])
        print("Cluster cache loaded -> fast mode")
        return True
    except Exception as e:
        print("Cache ignored:", e)
        return False


def save_cache():
    try:
        rows = []
        for c in CLUSTERS:
            row = {"Cluster": c}
            for key in METRIC_KEYS:
                row[key] = stats[c].get(key, "")
            rows.append(row)
        pd.DataFrame(rows).to_csv(CACHE_FILE, index=False)
        print("Cluster cache saved:", CACHE_FILE)
    except Exception as e:
        print("Could not save cache:", e)


# Rebuild only if an environmental file is newer than the cache.
source_files = [p for p in [ndvi_file, green_file, ndbi_file, ndwi_file, flood_file, heat_file, carbon_file, lulc_spatial, ndvi_summary, green_summary, ndbi_summary, ndwi_summary, flood_summary, heat_summary, carbon_summary, lulc_summary] if p]
cache_current = CACHE_FILE.exists() and source_files and CACHE_FILE.stat().st_mtime >= max(p.stat().st_mtime for p in source_files)
cache_loaded = load_cache() if cache_current else False

if not cache_loaded:
    print("Building 5-cluster environmental statistics...")

    aggregate_one(ndvi_file, ["NDVI", "NDVI_Mean", "Mean_NDVI"], "NDVI Mean", 4)
    aggregate_one(green_file, ["Green_Cover_Percent", "Green_Cover_Percentage", "Green_Cover", "GreenCover"], "Green Cover %", 2)
    aggregate_one(ndbi_file, ["NDBI", "NDBI_Mean", "Mean_NDBI"], "NDBI Mean", 4)
    aggregate_one(ndwi_file, ["NDWI", "NDWI_Mean", "Mean_NDWI"], "NDWI Mean", 4)
    aggregate_one(flood_file, ["Flood_Risk_Score", "FloodRisk", "Risk_Score", "Mean_Flood_Risk"], "Flood Risk Mean", 2)
    aggregate_one(heat_file, ["Land_Surface_Temperature_C", "Mean_Temperature_C", "Temperature_C", "LST_C", "LST"], "Heat Mean °C", 2)
    aggregate_one(carbon_file, ["Carbon_Storage", "Carbon_Stock", "Carbon_tonnes", "Carbon_Tonnes", "Mean_Carbon"], "Carbon Mean", 2)

    # If dedicated NDBI/NDWI files do not exist, calculate them from All-Bands.
    if not any("NDBI Mean" in stats[c] for c in CLUSTERS):
        aggregate_two_band(
            allbands_file,
            ["B11_SWIR", "B11", "B11_SWIR_20m"],
            ["B08_NIR", "B08", "B08_NIR_10m"],
            lambda a, b: np.where((a + b) != 0, (a - b) / (a + b), np.nan),
            "NDBI Mean", 4,
        )
    if not any("NDWI Mean" in stats[c] for c in CLUSTERS):
        aggregate_two_band(
            allbands_file or ndvi_file,
            ["B03_Green", "B03", "Green"],
            ["B08_NIR", "B08", "NIR"],
            lambda a, b: np.where((a + b) != 0, (a - b) / (a + b), np.nan),
            "NDWI Mean", 4,
        )

    # Summary fallback: only use it as OVERALL, never pretend it is cluster-specific.
    def summary_fallback(path, candidates, key, digits):
        if not path or any(key in stats[c] for c in CLUSTERS):
            return
        df = read_csv(path)
        if df is None or df.empty:
            return
        col = next((c for c in candidates if c in df.columns), None)
        if not col:
            return
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        if vals.empty:
            return
        value = fmt(vals.iloc[0], digits) + " (overall)"
        for c in CLUSTERS:
            stats[c][key] = value

    summary_fallback(ndvi_summary, ["Mean_NDVI", "NDVI_Mean", "NDVI"], "NDVI Mean", 4)
    summary_fallback(ndbi_summary, ["Mean_NDBI", "NDBI_Mean", "NDBI"], "NDBI Mean", 4)
    summary_fallback(ndwi_summary, ["Mean_NDWI", "NDWI_Mean", "NDWI"], "NDWI Mean", 4)
    summary_fallback(green_summary, ["Mean_Green_Cover", "Green_Cover_Percent", "Green_Cover_Percentage"], "Green Cover %", 2)
    summary_fallback(flood_summary, ["Mean_Flood_Risk_Score", "Mean_Flood_Risk", "Flood_Risk_Score"], "Flood Risk Mean", 2)
    summary_fallback(heat_summary, ["Mean_Temperature_C", "Mean_LST_C", "LST_C"], "Heat Mean °C", 2)
    summary_fallback(carbon_summary, ["Mean_Carbon", "Carbon_Storage", "Carbon_Stock"], "Carbon Mean", 2)

    # LULC cluster mix, if spatial CSV is available.
    if lulc_spatial:
        try:
            header = read_header(lulc_spatial)
            lat = next((c for c in ["Latitude", "latitude", "lat"] if c in header), None)
            lon = next((c for c in ["Longitude", "longitude", "lon", "lng"] if c in header), None)
            cls = next((c for c in ["LULC_Class", "Class", "class", "Class_Name", "Land_Cover"] if c in header), None)
            if lat and lon and cls:
                class_counts = {c: {} for c in CLUSTERS}
                for chunk in pd.read_csv(lulc_spatial, usecols=[lat, lon, cls], chunksize=100000, low_memory=False):
                    chunk[lat] = pd.to_numeric(chunk[lat], errors="coerce")
                    chunk[lon] = pd.to_numeric(chunk[lon], errors="coerce")
                    chunk = chunk.dropna(subset=[lat, lon, cls])
                    masks = cluster_masks(chunk[lat], chunk[lon])
                    for c, mask in masks.items():
                        counts = chunk.loc[mask, cls].value_counts()
                        for k, v in counts.items():
                            class_counts[c][str(k)] = class_counts[c].get(str(k), 0) + int(v)
                for c in CLUSTERS:
                    if class_counts[c]:
                        total = sum(class_counts[c].values())
                        parts = [f"{k}: {v / total * 100:.1f}%" for k, v in sorted(class_counts[c].items(), key=lambda x: -x[1])]
                        stats[c]["LULC Mix"] = ", ".join(parts)
        except Exception as e:
            print("LULC processing skipped:", e)

    # Overall LULC summary fallback.
    if not all("LULC Mix" in stats[c] for c in CLUSTERS) and lulc_summary:
        df = read_csv(lulc_summary)
        if df is not None and not df.empty:
            parts = []
            for _, r in df.iterrows():
                cls = r.get("LULC_Class", r.get("Class", r.get("Class_Name", "Unknown")))
                pct = r.get("Percentage", r.get("Percent", "N/A"))
                parts.append(f"{cls}: {fmt(pct, 1)}%")
            overall = ", ".join(parts)
            for c in CLUSTERS:
                if "LULC Mix" not in stats[c]:
                    stats[c]["LULC Mix"] = overall + " (overall)"

    save_cache()

# ------------------------------------------------------------
# SCENE DATE
# ------------------------------------------------------------
for summary_file in [ndvi_summary, green_summary, ndbi_summary, ndwi_summary, flood_summary, heat_summary, carbon_summary]:
    if summary_file:
        df = read_csv(summary_file)
        if df is not None and not df.empty and "Scene_Date" in df.columns:
            vals = df["Scene_Date"].dropna().astype(str)
            if not vals.empty:
                for c in CLUSTERS:
                    stats[c]["Scene Date"] = vals.iloc[0]
                break

# ------------------------------------------------------------
# MAP
# ------------------------------------------------------------
print("Creating lightweight map...")
m = folium.Map(
    location=CENTER,
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True,
    prefer_canvas=True,
)

# Keep GeoTwinAI information in bottom-left.
title = """
<div style="position:fixed;bottom:18px;left:18px;z-index:9997;background:rgba(255,255,255,.97);
padding:11px 15px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,.25);
font-family:Arial,sans-serif;min-width:235px;max-width:285px">
<div style="font-size:19px;font-weight:700">GEOTWINAI</div>
<div style="font-size:11px;margin-top:3px">AI-Powered Digital Twin for Smart Cities</div>
<div style="font-size:11px;margin-top:5px"><b>Study Area:</b> Nagpur, Maharashtra</div>
<div style="font-size:10px;margin-top:5px">Environmental analysis: 5 clusters</div>
</div>
"""
m.get_root().html.add_child(folium.Element(title))


def add_points(df, name, color, icon, fields, max_rows, show=True):
    if df is None or df.empty:
        return
    lat, lon = coord_cols(df)
    if not lat or not lon:
        return
    d = df.dropna(subset=[lat, lon]).copy()
    if len(d) > max_rows:
        d = d.iloc[np.linspace(0, len(d) - 1, max_rows, dtype=int)]
    group = MarkerCluster(
        name=name,
        show=show,
        options={"maxClusterRadius": 35, "disableClusteringAtZoom": 15},
    )
    for _, r in d.iterrows():
        try:
            la, lo = float(r[lat]), float(r[lon])
            rows = []
            for col, label in fields:
                if col in r.index and pd.notna(r[col]):
                    rows.append((label, str(r[col])[:180]))
            rows.append(("Cluster", cluster_of(la, lo)))
            folium.Marker(
                [la, lo],
                icon=folium.Icon(icon=icon, prefix="fa", color=color),
                popup=folium.Popup(popup_table(name, rows), max_width=500),
                tooltip=name,
            ).add_to(group)
        except Exception:
            continue
    group.add_to(m)


# DO NOT CHANGE these infrastructure layers.
add_points(
    buildings, "Buildings", "gray", "building",
    [("name", "Name"), ("name_en", "Name (English)"), ("building", "Building Type"),
     ("building_use", "Use"), ("addr_street", "Street"), ("addr_housenumber", "House No."),
     ("addr_postcode", "Postcode")], MAX_BUILDINGS, True,
)
add_points(
    hospitals, "Hospitals", "red", "plus",
    [("name", "Name"), ("healthcare", "Healthcare"), ("healthcare_speciality", "Speciality"),
     ("healthcare:speciality", "Speciality"), ("addr_full", "Address"), ("addr_street", "Street"),
     ("addr_city", "City"), ("phone", "Phone"), ("website", "Website")], MAX_MARKERS, True,
)
add_points(
    schools, "Schools", "blue", "graduation-cap",
    [("name", "Name"), ("education", "Education"), ("grades", "Grades"),
     ("addr_street", "Street"), ("addr_city", "City"), ("phone", "Phone")], MAX_MARKERS, True,
)
add_points(
    parks, "Parks", "green", "tree",
    [("name", "Name"), ("leisure", "Type"), ("description", "Description"),
     ("addr_street", "Street")], MAX_MARKERS, True,
)

# Water bodies - keep polygon style.
if water is not None and not water.empty and "geometry" in water.columns:
    layer = folium.FeatureGroup(name="Water Bodies", show=True)
    try:
        from shapely import wkt
        d = water.dropna(subset=["geometry"]).copy()
        if len(d) > MAX_WATER:
            d = d.iloc[np.linspace(0, len(d) - 1, MAX_WATER, dtype=int)]
        for _, r in d.iterrows():
            try:
                g = wkt.loads(str(r["geometry"]))
                polys = list(g.geoms) if g.geom_type == "MultiPolygon" else ([g] if g.geom_type == "Polygon" else [])
                for poly in polys:
                    coords = [[y, x] for x, y in poly.exterior.coords]
                    rows = [
                        ("Name", r.get("name", "N/A")),
                        ("Water Type", r.get("water", "N/A")),
                        ("Natural", r.get("natural", "N/A")),
                        ("Cluster", cluster_of(r.get("Latitude"), r.get("Longitude"))),
                    ]
                    folium.Polygon(
                        coords, color="#1976a3", weight=2, fill=True,
                        fill_color="#42a5f5", fill_opacity=.45,
                        popup=folium.Popup(popup_table("Water Body", rows), max_width=500),
                        tooltip="Water Body",
                    ).add_to(layer)
            except Exception:
                continue
    except Exception as e:
        print("Water body geometry skipped:", e)
    layer.add_to(m)

# Roads - black lines exactly as requested.
if roads is not None and not roads.empty and "geometry" in roads.columns:
    layer = folium.FeatureGroup(name="Roads — Black Lines", show=True)
    try:
        from shapely import wkt
        d = roads.dropna(subset=["geometry"]).copy()
        if len(d) > MAX_ROADS:
            d = d.iloc[np.linspace(0, len(d) - 1, MAX_ROADS, dtype=int)]
        for _, r in d.iterrows():
            try:
                g = wkt.loads(str(r["geometry"]))
                lines = list(g.geoms) if g.geom_type == "MultiLineString" else ([g] if g.geom_type == "LineString" else [])
                for line in lines:
                    coords = [[y, x] for x, y in line.coords]
                    rows = [
                        ("Road Name", r.get("name", "Unnamed")),
                        ("Road Type", r.get("highway", "N/A")),
                        ("Length (m)", fmt(r.get("length"), 1)),
                        ("Lanes", r.get("lanes", "N/A")),
                        ("Max Speed", r.get("maxspeed", "N/A")),
                        ("One Way", r.get("oneway", "N/A")),
                    ]
                    folium.PolyLine(
                        coords, color="black", weight=2.4, opacity=.78,
                        popup=folium.Popup(popup_table("Road", rows), max_width=450),
                        tooltip=str(r.get("name") or r.get("highway") or "Road"),
                    ).add_to(layer)
            except Exception:
                continue
    except Exception as e:
        print("Road geometry skipped:", e)
    layer.add_to(m)

# ------------------------------------------------------------
# ENVIRONMENTAL CLUSTER POPUPS
# ------------------------------------------------------------
ANALYSIS = {
    "NDVI": ("NDVI Mean", "Mean NDVI", 4),
    "NDBI": ("NDBI Mean", "Mean NDBI", 4),
    "NDWI": ("NDWI Mean", "Mean NDWI", 4),
    "Green Cover": ("Green Cover %", "Green Cover", 2),
    "Flood Risk": ("Flood Risk Mean", "Flood Risk Score", 2),
    "Urban Heat": ("Heat Mean °C", "Mean Surface Temperature (°C)", 2),
    "Carbon": ("Carbon Mean", "Mean Carbon", 2),
    "LULC": ("LULC Mix", "Land Use / Land Cover", 2),
}


def cluster_popup(cluster, selected):
    s = stats[cluster]
    rows = [("Cluster", cluster), ("Selected Layer", selected)]
    key, label, digits = ANALYSIS[selected]
    value = s.get(key)
    if value is None or str(value).strip() == "":
        value = "DATA NOT AVAILABLE"
    rows.append((label, value))
    if key.endswith("Mean") or key == "Green Cover %":
        rec_key = key + " Records"
        if rec_key in s:
            rows.append(("Source Records", s[rec_key]))
    if "Scene Date" in s:
        rows.append(("Scene Date", s["Scene Date"]))
    rows.extend([
        ("Buildings", s.get("Buildings", 0)),
        ("Hospitals", s.get("Hospitals", 0)),
        ("Schools", s.get("Schools", 0)),
        ("Parks", s.get("Parks", 0)),
        ("Water Bodies", s.get("Water Bodies", 0)),
    ])
    return popup_table(f"GeoTwinAI — {cluster} Cluster", rows)


def add_environment_layer(label, key, palette, selected, show=False):
    layer = folium.FeatureGroup(name=label, show=show)
    values = []
    for c in CLUSTERS:
        value = stats[c].get(key)
        try:
            if "overall" not in str(value).lower():
                values.append(float(value))
        except Exception:
            pass

    # Even when no data exists, create the five regions so the user sees exactly
    # where the analysis belongs. Never fabricate values.
    if not values:
        for c in CLUSTERS:
            folium.Polygon(
                POLYGONS[c], color="#777", weight=1.4,
                fill=True, fill_color="#eeeeee", fill_opacity=.25,
                popup=folium.Popup(cluster_popup(c, selected), max_width=500),
                tooltip=f"{c} | {selected} | data unavailable",
            ).add_to(layer)
        layer.add_to(m)
        return

    lo, hi = min(values), max(values)
    if lo == hi:
        pad = 0.01 if abs(lo) < 1 else max(abs(lo) * 0.05, 1)
        lo, hi = lo - pad, hi + pad
    cmap = LinearColormap(palette, vmin=lo, vmax=hi, caption=f"{selected} — 5 Cluster Analysis")

    for c in CLUSTERS:
        value = stats[c].get(key)
        try:
            num = float(value)
            fill = cmap(num)
            text = fmt(num, ANALYSIS[selected][2])
        except Exception:
            # Overall fallback is deliberately neutral: not presented as a
            # cluster-specific number.
            fill = "#eeeeee"
            text = str(value) if value else "N/A"
        folium.Polygon(
            POLYGONS[c], color="#333", weight=1.5,
            fill=True, fill_color=fill, fill_opacity=.68,
            popup=folium.Popup(cluster_popup(c, selected), max_width=500),
            tooltip=f"{c} | {selected}: {text}",
        ).add_to(layer)
    cmap.add_to(m)
    layer.add_to(m)


# NDVI is explicitly included and gets its own green colour scale.
add_environment_layer("NDVI — 5 Cluster Analysis", "NDVI Mean", ["#f7fcf5", "#74c476", "#006d2c"], "NDVI")
add_environment_layer("NDBI — 5 Cluster Analysis", "NDBI Mean", ["#fff5eb", "#fd8d3c", "#7f0000"], "NDBI")
add_environment_layer("NDWI — 5 Cluster Analysis", "NDWI Mean", ["#eff3ff", "#6baed6", "#08519c"], "NDWI")
add_environment_layer("Green Cover — 5 Cluster Analysis", "Green Cover %", ["#f7fcf5", "#74c476", "#238b45"], "Green Cover")
add_environment_layer("Flood Risk — 5 Cluster Analysis", "Flood Risk Mean", ["#ffffcc", "#fd8d3c", "#800026"], "Flood Risk")
add_environment_layer("Urban Heat — 5 Cluster Analysis", "Heat Mean °C", ["#fff5eb", "#fb6a4a", "#99000d"], "Urban Heat")
add_environment_layer("Carbon — 5 Cluster Analysis", "Carbon Mean", ["#f7fcf5", "#74c476", "#00441b"], "Carbon")
add_environment_layer("LULC — 5 Cluster Analysis", "LULC Mix", ["#f7fbff", "#9ecae1", "#2171b5"], "LULC")

# Five Cluster Overview - one table per cluster.
overview = folium.FeatureGroup(name="5 Cluster Overview", show=True)
for c in CLUSTERS:
    rows = [
        ("Cluster", c),
        ("NDVI", stats[c].get("NDVI Mean", "N/A")),
        ("NDBI", stats[c].get("NDBI Mean", "N/A")),
        ("NDWI", stats[c].get("NDWI Mean", "N/A")),
        ("Green Cover", stats[c].get("Green Cover %", "N/A")),
        ("Flood Risk", stats[c].get("Flood Risk Mean", "N/A")),
        ("Urban Heat", stats[c].get("Heat Mean °C", "N/A")),
        ("Carbon", stats[c].get("Carbon Mean", "N/A")),
        ("LULC", stats[c].get("LULC Mix", "N/A")),
        ("Buildings", stats[c].get("Buildings", 0)),
        ("Hospitals", stats[c].get("Hospitals", 0)),
        ("Schools", stats[c].get("Schools", 0)),
        ("Parks", stats[c].get("Parks", 0)),
        ("Water Bodies", stats[c].get("Water Bodies", 0)),
    ]
    folium.Polygon(
        POLYGONS[c], color="#222", weight=1.6, fill=False,
        popup=folium.Popup(popup_table(f"GeoTwinAI — {c} Cluster Overview", rows), max_width=540),
        tooltip=f"{c} — click for complete analysis",
    ).add_to(overview)
overview.add_to(m)

# ------------------------------------------------------------
# CONTROLS
# ------------------------------------------------------------
# Measurement stays top-left and title stays bottom-left, so they never overlap.
MeasureControl(
    position="topleft",
    primary_length_unit="kilometers",
    primary_area_unit="sqkilometers",
).add_to(m)
Fullscreen(position="topright").add_to(m)
folium.LayerControl(collapsed=False, position="topright").add_to(m)

info = """
<div style="position:fixed;bottom:18px;right:18px;z-index:9997;background:rgba(255,255,255,.96);
padding:9px 12px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);
font-family:Arial;font-size:11px;max-width:265px">
<b>GeoTwinAI Environmental Analysis</b><br>
• Tick one environmental layer.<br>
• North / South / East / West / Central are the five clusters.<br>
• Click a cluster for the complete table.<br>
• Green NDVI scale = lower → higher vegetation.<br>
• Roads remain black lines.<br>
• Infrastructure popups remain individually clickable.
</div>
"""
m.get_root().html.add_child(folium.Element(info))

m.fit_bounds([[MIN_LAT, MIN_LON], [MAX_LAT, MAX_LON]])

print("Saving lightweight HTML map...")
m.save(MAP_FILE)
size_mb = MAP_FILE.stat().st_size / (1024 * 1024)
print("=" * 72)
print("MAP COMPLETED")
print("Map:", MAP_FILE)
print(f"HTML size: {size_mb:.2f} MB")
print("Cluster cache:", CACHE_FILE)
print("=" * 72)
=======
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

>>>>>>> a08cd372948d939a206e50cc2dd246593a4ff2fe
