# GeoTwinAI Project Configuration

CITY_NAME = "Nagpur"

BBOX = [78.95, 21.05, 79.20, 21.25]

ZONES = [
    "North",
    "South",
    "East",
    "West",
    "Central"
]

GRID_SIZE = 10

NDBI_THRESHOLD = 0.05
NDVI_MAX_FOR_BUILTUP = 0.40


# Configuration summary
if __name__ == "__main__":
    print("================================")
    print("     GeoTwinAI Configuration")
    print("================================")
    print("City:", CITY_NAME)
    print("Study Area:", BBOX)
    print("Zones:", ", ".join(ZONES))
    print("Grid Size:", GRID_SIZE)
    print("NDBI Threshold:", NDBI_THRESHOLD)
    print("NDVI Built-up Limit:", NDVI_MAX_FOR_BUILTUP)
    print("================================")