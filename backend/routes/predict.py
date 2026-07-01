import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

from backend.database import get_connection, init_db

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "features.pkl"

# Global variables for lazy loading
_model = None
_features = None

CATEGORY_MAP = {
    "ai": "AI",
    "coding": "Coding",
    "education": "Education",
    "finance": "Finance",
    "food": "Food",
    "gaming": "Gaming",
    "tech": "Tech",
    "technology": "Tech",
    "travel": "Travel",
    "science": "Education",
    "news": "Tech",
    "entertainment": "Gaming",
    "music": "Gaming",
    "sports": "Gaming",
    "beauty": "Food",
    "lifestyle": "Travel",
    "vlogs": "Travel",
    "business": "Finance",
    "health": "Education",
}


def load_model():
    """Lazily load the ML model and features"""
    global _model, _features
    
    if _model is not None and _features is not None:
        return _model, _features
    
    try:
        logger.info(f"Loading model from {MODEL_PATH}")
        if not MODEL_PATH.exists():
            logger.error(f"❌ Model file not found at {MODEL_PATH}")
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        _model = joblib.load(MODEL_PATH)
        logger.info("✅ Model loaded successfully")
        
        logger.info(f"Loading features from {FEATURES_PATH}")
        if not FEATURES_PATH.exists():
            logger.error(f"❌ Features file not found at {FEATURES_PATH}")
            raise FileNotFoundError(f"Features not found at {FEATURES_PATH}")
        
        _features = joblib.load(FEATURES_PATH)
        logger.info(f"✅ Features loaded successfully ({len(_features)} features)")
        
        return _model, _features
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise


# Initialize database on module import
try:
    init_db()
    logger.info("✅ Database initialized in predict route module")
except Exception as e:
    logger.error(f"❌ Database initialization failed in predict route: {e}")


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


def normalize_category(category: str) -> str:
    """Normalize category to match training data"""
    if not isinstance(category, str):
        logger.warning(f"Category is not a string: {type(category)}")
        return "Tech"

    normalized = category.strip().lower()
    result = CATEGORY_MAP.get(normalized, category.strip().title())
    logger.debug(f"Category normalized: {category} -> {result}")
    return result


@router.post("/predict")
def predict(data: PredictionInput):
    """Make a prediction using the ML model"""
    try:
        logger.info(f"Prediction request received from subscriber: {data.subscriber_count}")
        
        # Load model on demand
        try:
            model, features = load_model()
        except Exception as e:
            logger.error(f"❌ Failed to load model during prediction: {e}")
            raise HTTPException(status_code=503, detail=f"Model not ready: {str(e)}")
        
        input_data = data.model_dump()
        input_data["category"] = normalize_category(input_data["category"])
        logger.debug(f"Input data: {input_data}")

        df = pd.DataFrame([input_data])

        # One Hot Encoding
        df = pd.get_dummies(df)
        logger.debug(f"After encoding: {df.columns.tolist()}")

        # Add missing columns
        missing_cols = [col for col in features if col not in df.columns]
        if missing_cols:
            logger.debug(f"Adding missing columns: {missing_cols}")
            for col in missing_cols:
                df[col] = 0

        # Ensure same order as training data
        df = df[features]

        prediction = int(model.predict(df)[0])
        logger.info(f"✅ Prediction successful: {prediction} views")

        # Save to database
        try:
            conn = get_connection()
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
            conn.close()
            logger.info(f"✅ Prediction saved to database")
        except Exception as db_error:
            logger.error(f"❌ Failed to save prediction to database: {db_error}")
            # Don't fail the request if DB save fails, just log it
            pass

        return {
            "Predicted Views": prediction,
            "status": "success",
            "timestamp": str(pd.Timestamp.now())
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"❌ Prediction failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(exc)}")


@router.get("/history")
def history():
    """Get prediction history"""
    try:
        logger.info("History request received")
        conn = get_connection()
        db_cursor = conn.cursor()
        db_cursor.execute("""
            SELECT *
            FROM predictions
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = db_cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "title_length": row[1],
                "likes": row[2],
                "subscriber_count": row[3],
                "predicted_views": row[4]
            })

        logger.info(f"✅ History retrieved: {len(result)} records")
        return result
    except Exception as exc:
        logger.error(f"❌ Failed to retrieve history: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(exc)}")


@router.get("/stats")
def stats():
    """Get prediction statistics"""
    try:
        logger.info("Stats request received")
        conn = get_connection()
        db_cursor = conn.cursor()
        
        db_cursor.execute("SELECT COUNT(*) FROM predictions")
        total = db_cursor.fetchone()[0]

        db_cursor.execute("SELECT AVG(predicted_views) FROM predictions")
        avg = db_cursor.fetchone()[0]

        if avg is None:
            avg = 0
        
        avg = float(avg)
        conn.close()
        
        logger.info(f"✅ Stats retrieved: total={total}, avg={avg:.0f}")
        return {
            "total_predictions": total,
            "average_views": avg,
            "status": "success"
        }
    except Exception as exc:
        logger.error(f"❌ Failed to retrieve stats: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(exc)}")

    return {
        "total_predictions": total,
        "average_views": int(avg)
    }