import logging
import sys
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import backend.database
from backend.routes.predict import router as predict_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Powered YouTube Analytics",
    version="1.0"
)

# CORS - Allow frontend to connect from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🚀 Backend Starting Up...")
    logger.info("=" * 60)
    try:
        backend.database.init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Backend Shutting Down...")

# Include Prediction Routes
app.include_router(predict_router)

# Health Check Endpoint
@app.get("/health")
def health_check():
    """Check if backend is running and ready to accept requests"""
    try:
        backend.database.get_connection()
        logger.info("✅ Health check passed")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Backend is running and ready"
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Home API
@app.get("/")
def home():
    logger.info("Home endpoint accessed")
    return {
        "message": "Backend Running Successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0"
    }
