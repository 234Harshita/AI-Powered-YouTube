import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor

# ----------------------------
# Load Dataset
# ----------------------------

dataset_path = "Dataset/youtube_growth_dataset.xlsx"

df = pd.read_excel(dataset_path)

print("Dataset Loaded Successfully")
print(df.head())

# ----------------------------
# Remove ID Column
# ----------------------------

df.drop(columns=["video_id"], inplace=True)

# ----------------------------
# One Hot Encoding
# ----------------------------

df = pd.get_dummies(df)

# ----------------------------
# Target
# ----------------------------

y = df["views"]

X = df.drop(columns=["views"])

# ----------------------------
# Split
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ----------------------------
# Train Model
# ----------------------------

model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print()

print("MAE :", mean_absolute_error(y_test, pred))
print("R2 Score :", r2_score(y_test, pred))

# ----------------------------
# Save Model
# ----------------------------

os.makedirs("backend/models", exist_ok=True)

joblib.dump(model, "backend/models/model.pkl")
joblib.dump(list(X.columns), "backend/models/features.pkl")

print()
print("Model Saved Successfully")