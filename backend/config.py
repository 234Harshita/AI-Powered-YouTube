import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model.pkl")
DATASET_PATH = os.path.join(os.path.dirname(BASE_DIR), "Dataset", "youtube.csv")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
