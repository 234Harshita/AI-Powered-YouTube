from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_predict_accepts_common_categories():
    payload = {
        "title_length": 20,
        "upload_hour": 15,
        "category": "tech",
        "tags_count": 8,
        "duration_min": 12,
        "thumbnail_score": 85,
        "seo_score": 80,
        "ctr_percent": 6.2,
        "likes": 500,
        "comments": 60,
        "subscriber_count": 10000,
        "viral_score": 70,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
