import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib


# ============================================================
# GEOTWINAI - URBAN DEVELOPMENT ML MODEL
# ============================================================

print("\n" + "=" * 60)
print("GEOTWINAI - URBAN DEVELOPMENT ML MODEL")
print("=" * 60)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# CORRECT DATASET PATH
DATA_FILE = BASE_DIR / "output" / "Nagpur_Feature_Dataset.csv"

MODEL_DIR = BASE_DIR / "model"
MODEL_FILE = MODEL_DIR / "nagpur_urban_model.pkl"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

if not DATA_FILE.exists():
    print("\nERROR: Dataset nahi mila!")
    print(f"Required file: {DATA_FILE}")
    raise SystemExit

df = pd.read_csv(DATA_FILE)

print("\nDataset loaded successfully.")
print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")


# ============================================================
# REQUIRED FEATURES
# ============================================================

FEATURES = [
    "Healthcare_Index",
    "Education_Index",
    "Green_Space_Index",
    "Water_Availability_Index",
    "Building_Density_Index",
    "Road_Density_Index"
]


# ============================================================
# CHECK FEATURES
# ============================================================

missing_features = [
    col for col in FEATURES
    if col not in df.columns
]

if missing_features:
    print("\nERROR: Required features missing:")

    for col in missing_features:
        print(f"- {col}")

    print("\nAvailable columns:")
    print(list(df.columns))

    raise SystemExit


# ============================================================
# CREATE URBAN DEVELOPMENT SCORE
# ============================================================

score_components = [
    "Healthcare_Index",
    "Education_Index",
    "Green_Space_Index",
    "Water_Availability_Index",
    "Building_Density_Index",
    "Road_Density_Index"
]


# Convert columns to numeric
for col in score_components:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# Remove invalid rows
df = df.dropna(subset=score_components).copy()


if len(df) < 2:
    print("\nERROR: Not enough valid rows for model training.")
    raise SystemExit


# ============================================================
# NORMALIZE FEATURES
# ============================================================

normalized = pd.DataFrame(index=df.index)

for col in score_components:

    min_value = df[col].min()
    max_value = df[col].max()

    if max_value == min_value:
        normalized[col] = 50
    else:
        normalized[col] = (
            (df[col] - min_value)
            / (max_value - min_value)
        ) * 100


# ============================================================
# URBAN DEVELOPMENT SCORE
# ============================================================

df["Urban_Development_Score"] = (
    normalized["Healthcare_Index"] * 0.20
    + normalized["Education_Index"] * 0.20
    + normalized["Green_Space_Index"] * 0.15
    + normalized["Water_Availability_Index"] * 0.15
    + normalized["Building_Density_Index"] * 0.15
    + normalized["Road_Density_Index"] * 0.15
)


# ============================================================
# PREPARE X AND Y
# ============================================================

X = df[FEATURES]
y = df["Urban_Development_Score"]


print("\nFeatures used for training:")

for feature in FEATURES:
    print(f"- {feature}")

print("\nTarget:")
print("- Urban_Development_Score")


# ============================================================
# DISPLAY GENERATED SCORES
# ============================================================

print("\nUrban Development Scores:")

for index, row in df.iterrows():

    region = row["Region"] if "Region" in df.columns else index

    print(
        f"{region}: "
        f"{row['Urban_Development_Score']:.2f}"
    )


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    max_depth=5
)

model.fit(X, y)


# ============================================================
# MODEL PERFORMANCE
# ============================================================

predictions = model.predict(X)

mae = mean_absolute_error(y, predictions)
rmse = np.sqrt(mean_squared_error(y, predictions))

print("\n" + "-" * 60)
print("MODEL PERFORMANCE")
print("-" * 60)

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")

if len(df) >= 3:
    r2 = r2_score(y, predictions)
    print(f"R2   : {r2:.2f}")
else:
    print("R2   : Not reliable with very small dataset")


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n" + "-" * 60)
print("FEATURE IMPORTANCE")
print("-" * 60)

importance = pd.DataFrame({
    "Feature": FEATURES,
    "Importance": model.feature_importances_
})

importance = importance.sort_values(
    by="Importance",
    ascending=False
)

for _, row in importance.iterrows():

    print(
        f"{row['Feature']:<30}"
        f"{row['Importance']:.4f}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(model, MODEL_FILE)

print("\n" + "=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)

print("\nModel saved at:")
print(MODEL_FILE)

print("\nNext file:")
print("scripts/predict.py")

print("=" * 60)