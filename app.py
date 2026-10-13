import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import database

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "ds-lab-college-secret-key-2026")
app.config["MAX_CONTENT_LENGTH"] = 75 * 1024 * 1024  # 75 MB limit for video & images

# Base upload folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "images")
VIDEO_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "videos")

os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def save_uploaded_file(file_storage, target_folder, allowed_extensions):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "bin"
    unique_name = f"{uuid.uuid4().hex[:12]}_{original_name}"
    save_path = os.path.join(target_folder, unique_name)
    file_storage.save(save_path)
    return unique_name

# Initialize database tables & default records
with app.app_context():
    database.init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "database_type": database.ACTIVE_DB_TYPE,
        "mysql_database": database.DB_NAME
    })

@app.route("/api/student", methods=["GET"])
def get_student_profile():
    try:
        student = database.get_student()
        return jsonify({"success": True, "student": student})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/student", methods=["POST", "PUT"])
def update_student_profile():
    try:
        if request.is_json:
            data = request.get_json(silent=True) or {}
            photo_url = data.get("photo_url")
        else:
            data = request.form
            photo_file = request.files.get("photo")
            photo_url = None
            if photo_file and photo_file.filename != "":
                saved_filename = save_uploaded_file(photo_file, IMAGE_UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS)
                photo_url = f"/static/uploads/images/{saved_filename}"

        name = data.get("name", "").strip()
        roll_no = data.get("roll_no", "").strip()
        section = data.get("section", "").strip()
        branch = data.get("branch", "").strip()
        assistant_professor = data.get("assistant_professor", "").strip()
        github_url = data.get("github_url", "").strip()

        if not name or not roll_no:
            return jsonify({"success": False, "error": "Name and Roll Number are required."}), 400

        updated = database.update_student(
            name=name,
            roll_no=roll_no,
            section=section,
            branch=branch,
            assistant_professor=assistant_professor,
            photo_url=photo_url,
            github_url=github_url
        )
        return jsonify({"success": True, "student": updated, "message": "ID card updated successfully!"})
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments", methods=["GET"])
def list_experiments():
    try:
        query = request.args.get("q", "").strip()
        experiments = database.get_all_experiments(search=query if query else None)
        return jsonify({"success": True, "count": len(experiments), "experiments": experiments})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/<int:exp_id>", methods=["GET"])
def get_experiment(exp_id):
    try:
        experiment = database.get_experiment_by_id(exp_id)
        if not experiment:
            return jsonify({"success": False, "error": "Experiment not found"}), 404
        return jsonify({"success": True, "experiment": experiment})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments", methods=["POST"])
def add_experiment():
    try:
        data = request.form
        experiment_no = data.get("experiment_no", "").strip()
        title = data.get("title", "").strip()
        short_description = data.get("short_description", "").strip()
        d2_heading = data.get("d2_heading", "Long Description").strip()
        long_content = data.get("long_content", "").strip()
        github_url = data.get("github_url", "").strip()

        if not experiment_no:
            return jsonify({"success": False, "error": "Experiment number is required."}), 400
        if not title:
            return jsonify({"success": False, "error": "Experiment title is required."}), 400
        if not short_description:
            return jsonify({"success": False, "error": "Short description (D1) is required."}), 400
        if not long_content:
            return jsonify({"success": False, "error": "Long content (Aim, Procedure, etc.) is required."}), 400

        # Handle Cover Image upload
        cover_file = request.files.get("cover_image")
        cover_url = ""
        if cover_file and cover_file.filename != "":
            saved_cover = save_uploaded_file(cover_file, IMAGE_UPLOAD_FOLDER, ALLOWED_IMAGE_EXTENSIONS)
            cover_url = f"/static/uploads/images/{saved_cover}"
        else:
            # Default placeholder image if none provided
            cover_url = "/static/uploads/images/sample_eda_cover.png"

        # Handle Video upload (optional)
        video_file = request.files.get("video")
        video_url = ""
        if video_file and video_file.filename != "":
            saved_video = save_uploaded_file(video_file, VIDEO_UPLOAD_FOLDER, ALLOWED_VIDEO_EXTENSIONS)
            video_url = f"/static/uploads/videos/{saved_video}"

        created_exp = database.create_experiment(
            experiment_no=experiment_no,
            title=title,
            short_description=short_description,
            d2_heading=d2_heading or "Long Description",
            long_content=long_content,
            github_url=github_url,
            cover_url=cover_url,
            video_url=video_url
        )

        return jsonify({
            "success": True,
            "message": "Experiment added successfully!",
            "experiment": created_exp
        }), 201

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/experiments/<int:exp_id>", methods=["DELETE"])
def remove_experiment(exp_id):
    try:
        exp = database.get_experiment_by_id(exp_id)
        if not exp:
            return jsonify({"success": False, "error": "Experiment not found"}), 404

        # Delete from DB and get associated media files
        media_urls = database.delete_experiment(exp_id)

        # Delete physical files from disk (only if located in static/uploads and not sample defaults)
        for url in media_urls:
            if url and url.startswith("/static/uploads/"):
                # Avoid deleting default sample template image
                if "sample_eda_cover.png" in url or "default_avatar.png" in url:
                    continue
                relative_path = url.lstrip("/").replace("/", os.sep)
                full_path = os.path.join(BASE_DIR, relative_path)
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                except Exception as file_err:
                    print(f"Error removing file {full_path}: {file_err}")

        return jsonify({"success": True, "message": "Experiment and media deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"success": False, "error": "File size exceeds the 75MB limit. Please upload a smaller video or image."}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), 404

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"Starting Data Science Laboratory (DS LAB) on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
