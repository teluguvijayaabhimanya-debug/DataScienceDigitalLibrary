# Data Science Laboratory (DS LAB) Portal

A simple, clean, and professional **Data Science Laboratory (DS LAB)** digital record website.

Designed for college students and faculty to upload, document, view, and manage lab experiments with images, full procedures, observations, output, GitHub source code, and video demonstrations.

---

## 🌟 Key Features

1. **Student ID Card / Profile**:
   - Clean academic ID card with student photo, name, roll number, section, branch, assistant professor, and repository link.
   - **Edit ID Card**: Update details and upload a custom profile photo with immediate UI and database synchronization.
   - Zero clutter—no unnecessary dashboards, charts, or analytics cards.

2. **Experiment Listing**:
   - Clean, responsive cards showing experiment number, cover image, experiment title, short description, Read More button, GitHub link, and delete button.
   - Smooth hover effects with clean typography (IBM Plex Sans + Sora).

3. **Add Experiment**:
   - Simple modal form to add experiments:
     - Experiment Number (e.g. `1`)
     - Experiment Name (e.g. `Data Collection & Preprocessing`)
     - Short Description (D1)
     - Main Cover Page (JPG, JPEG, PNG, WEBP with live preview)
     - D2 Heading (e.g. `Detailed Report`)
     - D2 Long Content (Aim, Procedure, Observations, Output, Conclusion)
     - GitHub Link (optional)
     - Short Video clip (optional MP4, WebM, MOV)
   - Media uploaded safely to server folders with paths stored in the database.

4. **Experiment Details (Read More)**:
   - Paper-style experiment details modal.
   - Displays cover banner, structured report sections (Aim, Procedure, Output, etc.), HTML5 video player with browser controls, and GitHub button.

5. **Instant Search**:
   - Real-time client-side search across experiment number, title, and description without full page reload.

6. **Delete Experiment**:
   - Confirmation dialog before deleting.
   - Permanently removes experiment and media records from the database and cleans up uploaded files from the server.

---

## 🗂️ Project Structure

```text
DS-Lab-Portal/
├── app.py                  # Flask backend with REST APIs & file upload handlers
├── database.py             # Database connectivity (MySQL + zero-config fallback)
├── database.sql            # Full MySQL schema creation script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Local environment configuration
├── test_app.py             # Integration test suite
│
├── templates/
│   └── index.html          # Clean, accessible HTML frontend
│
└── static/
    ├── css/
    │   └── style.css       # Clean college laboratory stylesheet
    ├── js/
    │   └── app.js          # Interactive JavaScript (AJAX, modals, uploads, search)
    └── uploads/
        ├── images/         # Stored cover pages & student photos
        └── videos/         # Stored experiment video clips
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MySQL Database
Create your MySQL database using the provided `database.sql`:
```bash
mysql -u root -p < database.sql
```

Update your `.env` file with your MySQL root credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=ds_lab
```

*(Note: If MySQL credentials are not yet entered, the app gracefully falls back to an embedded SQLite database `ds_lab.db` so you can test it immediately without interruptions).*

### 3. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Database Schema

### `student` Table
* `id`: INT AUTO_INCREMENT PRIMARY KEY
* `name`: VARCHAR(255)
* `roll_no`: VARCHAR(100)
* `section`: VARCHAR(50)
* `branch`: VARCHAR(100)
* `assistant_professor`: VARCHAR(255)
* `photo_url`: VARCHAR(500)
* `github_url`: VARCHAR(500)

### `experiments` Table
* `id`: INT AUTO_INCREMENT PRIMARY KEY
* `experiment_no`: VARCHAR(50)
* `title`: VARCHAR(255)
* `short_description`: TEXT
* `d2_heading`: VARCHAR(255)
* `long_content`: MEDIUMTEXT
* `github_url`: VARCHAR(500)
* `created_at`: TIMESTAMP

### `experiment_media` Table
* `id`: INT AUTO_INCREMENT PRIMARY KEY
* `experiment_id`: INT (Foreign Key -> `experiments.id` ON DELETE CASCADE)
* `media_type`: ENUM('cover_image', 'video', 'image')
* `media_url`: VARCHAR(500)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main laboratory web page |
| `GET` | `/api/student` | Fetch student ID card information |
| `POST` | `/api/student` | Update student ID card & upload photo |
| `GET` | `/api/experiments` | List all experiments (supports `?q=...` search) |
| `GET` | `/api/experiments/<id>` | Fetch single experiment details & media |
| `POST` | `/api/experiments` | Upload new experiment with cover image and optional video |
| `DELETE` | `/api/experiments/<id>` | Delete experiment and remove associated media files |
