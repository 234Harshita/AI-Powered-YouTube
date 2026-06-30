from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from backend.config import UPLOAD_FOLDER

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")

@upload_bp.post("")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    return jsonify({"message": "File uploaded successfully", "filename": filename})
