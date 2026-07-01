import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "youtube.db"


def get_connection():
    """Get a new database connection with proper configuration"""
    try:
        logger.debug(f"Creating database connection to {DB_PATH}")
        conn = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        logger.debug("✅ Database connection established")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to create database connection: {e}")
        raise


def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        logger.info(f"Initializing database at {DB_PATH}")
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_length INTEGER,
            likes INTEGER,
            subscriber_count INTEGER,
            predicted_views INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


# Initialize database on module import
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialize database on module import: {e}")