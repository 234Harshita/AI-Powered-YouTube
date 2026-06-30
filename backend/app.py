from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.database
from backend.routes.predict import router as predict_router

app = FastAPI(
    title="AI Powered YouTube Analytics",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Prediction Routes
app.include_router(predict_router)

# Home API
@app.get("/")
def home():
    return {
        "message": "Backend Running Successfully"
    }
