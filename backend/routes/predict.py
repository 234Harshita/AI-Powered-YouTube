from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

from backend.database import get_connection

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "features.pkl"

# Load Model
model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURES_PATH)

# Database
conn = get_connection()


class PredictionInput(BaseModel):
    title_length: int
    upload_hour: int
    category: str
    tags_count: int
    duration_min: int
    thumbnail_score: int
    seo_score: int
    ctr_percent: float
    likes: int
    comments: int
    subscriber_count: int
    viral_score: int


@router.post("/predict")
def predict(data: PredictionInput):

    input_data = data.dict()

    df = pd.DataFrame([input_data])

    # One Hot Encoding
    df = pd.get_dummies(df)

    # Missing Columns
    for col in features:
        if col not in df.columns:
            df[col] = 0

    # Same Order
    df = df[features]

    prediction = int(model.predict(df)[0])

    try:
        db_cursor = conn.cursor()
        db_cursor.execute("""
            INSERT INTO predictions
            (title_length, likes, subscriber_count, predicted_views)
            VALUES (?, ?, ?, ?)
        """, (
            data.title_length,
            data.likes,
            data.subscriber_count,
            prediction
        ))
        conn.commit()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "Predicted Views": prediction
    }


@router.get("/history")
def history():

    db_cursor = conn.cursor()
    db_cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
    """)

    rows = db_cursor.fetchall()

    result = []

    for row in rows:

        result.append({

            "id": row[0],
            "title_length": row[1],
            "likes": row[2],
            "subscriber_count": row[3],
            "predicted_views": row[4]

        })

    return result


@router.get("/stats")
def stats():

    db_cursor = conn.cursor()
    db_cursor.execute("SELECT COUNT(*) FROM predictions")
    total = db_cursor.fetchone()[0]

    db_cursor.execute("SELECT AVG(predicted_views) FROM predictions")
    avg = db_cursor.fetchone()[0]

    if avg is None:
        avg = 0

    return {
        "total_predictions": total,
        "average_views": int(avg)
    }