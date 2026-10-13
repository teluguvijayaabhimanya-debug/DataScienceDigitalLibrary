import os
import sqlite3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "ds_lab")

# Mode: 'mysql' or fallback 'sqlite'
ACTIVE_DB_TYPE = "mysql"

def get_mysql_raw_connection(include_db=True):
    kwargs = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "autocommit": True
    }
    if include_db:
        kwargs["database"] = DB_NAME
    return mysql.connector.connect(**kwargs)

def get_sqlite_connection():
    db_path = os.path.join(os.path.dirname(__file__), "ds_lab.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_connection():
    global ACTIVE_DB_TYPE
    if ACTIVE_DB_TYPE == "mysql":
        try:
            return get_mysql_raw_connection(include_db=True)
        except Exception:
            # Fall back to sqlite if MySQL connection fails
            ACTIVE_DB_TYPE = "sqlite"
            return get_sqlite_connection()
    else:
        return get_sqlite_connection()

def init_db():
    global ACTIVE_DB_TYPE
    try:
        # Try connecting to MySQL server to ensure database exists
        server_conn = get_mysql_raw_connection(include_db=False)
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        server_cursor.close()
        server_conn.close()

        # Connect to ds_lab MySQL database
        conn = get_mysql_raw_connection(include_db=True)
        cursor = conn.cursor()

        # 1. Student table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                roll_no VARCHAR(100) NOT NULL,
                section VARCHAR(50) NOT NULL,
                branch VARCHAR(100) NOT NULL,
                assistant_professor VARCHAR(255) NOT NULL,
                photo_url VARCHAR(500) DEFAULT '',
                github_url VARCHAR(500) DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Experiments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                experiment_no VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                short_description TEXT NOT NULL,
                d2_heading VARCHAR(255) DEFAULT 'Long Description',
                long_content MEDIUMTEXT NOT NULL,
                github_url VARCHAR(500) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 3. Experiment media table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_media (
                id INT AUTO_INCREMENT PRIMARY KEY,
                experiment_id INT NOT NULL,
                media_type ENUM('cover_image', 'video', 'image') NOT NULL,
                media_url VARCHAR(500) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Seed initial student if table empty
        cursor.execute("SELECT COUNT(*) FROM student")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO student (name, roll_no, section, branch, assistant_professor, photo_url, github_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                "K. Sai Venkatesh",
                "22A91A0542",
                "DS-A",
                "Data Science & AI",
                "Dr. P. Rajesh Kumar",
                "",
                "https://github.com/saivenkatesh/ds-laboratory"
            ))

        # Seed initial sample experiment if experiments table is empty
        cursor.execute("SELECT COUNT(*) FROM experiments")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                "1",
                "Data Cleaning and Exploratory Data Analysis (EDA)",
                "Preprocessing raw structured datasets, handling missing values, identifying outliers, and generating statistical summaries using Pandas and Seaborn.",
                "Experiment Report: EDA & Data Preprocessing",
                "AIM:\nTo perform data wrangling, missing value imputation, outlier detection, and exploratory statistical analysis on a customer dataset using Python, Pandas, and Matplotlib.\n\nPROCEDURE:\n1. Load the raw CSV dataset into a Pandas DataFrame.\n2. Inspect data types, null values, and summary statistics using df.info() and df.describe().\n3. Impute missing numerical attributes with median values and categorical fields with mode.\n4. Detect outliers using the Interquartile Range (IQR) technique and visualize via Boxplots.\n5. Compute correlation matrix and visualize correlations using Seaborn heatmaps.\n6. Generate univariate and bivariate distribution plots for target features.\n\nOBSERVATIONS & OUTPUT:\n- Missing values accounted for 4.2% of the total dataset in the income column, successfully imputed.\n- Removed 18 extreme multivariate outlier records.\n- Strong positive correlation (r = 0.82) observed between spending score and purchase frequency.\n\nCONCLUSION:\nThe dataset was successfully cleaned and standardized. Exploratory data analysis provided crucial feature distribution insights ready for downstream predictive modeling.",
                "https://github.com/saivenkatesh/ds-laboratory/tree/main/exp01_eda"
            ))
            sample_exp_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (%s, %s, %s)
            """, (sample_exp_id, "cover_image", "/static/uploads/images/sample_eda_cover.png"))

        cursor.close()
        conn.close()
        ACTIVE_DB_TYPE = "mysql"
        print("[DATABASE] Successfully connected and initialized MySQL database: ds_lab")
    except Exception as e:
        print(f"[DATABASE NOTICE] MySQL connection attempt returned: {e}")
        print("[DATABASE] Falling back to SQLite database for instant local operation. (To use MySQL, set DB_PASSWORD in .env)")
        ACTIVE_DB_TYPE = "sqlite"
        _init_sqlite()

def _init_sqlite():
    conn = get_sqlite_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            section TEXT NOT NULL,
            branch TEXT NOT NULL,
            assistant_professor TEXT NOT NULL,
            photo_url TEXT DEFAULT '',
            github_url TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_no TEXT NOT NULL,
            title TEXT NOT NULL,
            short_description TEXT NOT NULL,
            d2_heading TEXT DEFAULT 'Long Description',
            long_content TEXT NOT NULL,
            github_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiment_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            media_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM student")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO student (name, roll_no, section, branch, assistant_professor, photo_url, github_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "K. Sai Venkatesh",
            "22A91A0542",
            "DS-A",
            "Data Science & AI",
            "Dr. P. Rajesh Kumar",
            "",
            "https://github.com/saivenkatesh/ds-laboratory"
        ))

    cursor.execute("SELECT COUNT(*) FROM experiments")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "1",
            "Data Cleaning and Exploratory Data Analysis (EDA)",
            "Preprocessing raw structured datasets, handling missing values, identifying outliers, and generating statistical summaries using Pandas and Seaborn.",
            "Experiment Report: EDA & Data Preprocessing",
            "AIM:\nTo perform data wrangling, missing value imputation, outlier detection, and exploratory statistical analysis on a customer dataset using Python, Pandas, and Matplotlib.\n\nPROCEDURE:\n1. Load the raw CSV dataset into a Pandas DataFrame.\n2. Inspect data types, null values, and summary statistics using df.info() and df.describe().\n3. Impute missing numerical attributes with median values and categorical fields with mode.\n4. Detect outliers using the Interquartile Range (IQR) technique and visualize via Boxplots.\n5. Compute correlation matrix and visualize correlations using Seaborn heatmaps.\n6. Generate univariate and bivariate distribution plots for target features.\n\nOBSERVATIONS & OUTPUT:\n- Missing values accounted for 4.2% of the total dataset in the income column, successfully imputed.\n- Removed 18 extreme multivariate outlier records.\n- Strong positive correlation (r = 0.82) observed between spending score and purchase frequency.\n\nCONCLUSION:\nThe dataset was successfully cleaned and standardized. Exploratory data analysis provided crucial feature distribution insights ready for downstream predictive modeling.",
            "https://github.com/saivenkatesh/ds-laboratory/tree/main/exp01_eda"
        ))
        sample_exp_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO experiment_media (experiment_id, media_type, media_url)
            VALUES (?, ?, ?)
        """, (sample_exp_id, "cover_image", "/static/uploads/images/sample_eda_cover.png"))

    conn.commit()
    conn.close()
    print("[DATABASE] SQLite database initialized successfully.")

def get_student():
    conn = get_connection()
    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, roll_no, section, branch, assistant_professor, photo_url, github_url FROM student ORDER BY id ASC LIMIT 1")
        student = cursor.fetchone()
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, roll_no, section, branch, assistant_professor, photo_url, github_url FROM student ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
        student = dict(row) if row else None
        conn.close()

    if not student:
        student = {
            "id": 1,
            "name": "Student Name",
            "roll_no": "22A91A0501",
            "section": "DS-A",
            "branch": "Data Science & AI",
            "assistant_professor": "Faculty Incharge",
            "photo_url": "",
            "github_url": ""
        }
    return student

def update_student(name, roll_no, section, branch, assistant_professor, photo_url=None, github_url=None):
    current = get_student()
    student_id = current.get("id", 1)
    new_photo = photo_url if photo_url is not None else current.get("photo_url", "")
    new_github = github_url if github_url is not None else current.get("github_url", "")

    conn = get_connection()
    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE student 
            SET name = %s, roll_no = %s, section = %s, branch = %s, assistant_professor = %s, photo_url = %s, github_url = %s
            WHERE id = %s
        """, (name, roll_no, section, branch, assistant_professor, new_photo, new_github, student_id))
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE student 
            SET name = ?, roll_no = ?, section = ?, branch = ?, assistant_professor = ?, photo_url = ?, github_url = ?
            WHERE id = ?
        """, (name, roll_no, section, branch, assistant_professor, new_photo, new_github, student_id))
        conn.commit()
        conn.close()

    return get_student()

def get_all_experiments(search=None):
    conn = get_connection()
    experiments = []

    sql = """
        SELECT e.id, e.experiment_no, e.title, e.short_description, e.d2_heading, e.long_content, e.github_url, e.created_at,
               m_cover.media_url AS cover_url,
               m_video.media_url AS video_url
        FROM experiments e
        LEFT JOIN experiment_media m_cover ON e.id = m_cover.experiment_id AND m_cover.media_type = 'cover_image'
        LEFT JOIN experiment_media m_video ON e.id = m_video.experiment_id AND m_video.media_type = 'video'
    """
    params = []
    if search and search.strip():
        term = f"%{search.strip()}%"
        sql += " WHERE e.experiment_no LIKE %s OR e.title LIKE %s OR e.short_description LIKE %s" if ACTIVE_DB_TYPE == "mysql" else " WHERE e.experiment_no LIKE ? OR e.title LIKE ? OR e.short_description LIKE ?"
        params = [term, term, term]

    sql += " ORDER BY CAST(e.experiment_no AS UNSIGNED) ASC, e.id ASC" if ACTIVE_DB_TYPE == "mysql" else " ORDER BY CAST(e.experiment_no AS INTEGER) ASC, e.id ASC"

    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, tuple(params) if params else ())
        rows = cursor.fetchall()
        for r in rows:
            if r.get("created_at"):
                r["created_at"] = str(r["created_at"])
            experiments.append(r)
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params) if params else ())
        rows = cursor.fetchall()
        for r in rows:
            item = dict(r)
            if item.get("created_at"):
                item["created_at"] = str(item["created_at"])
            experiments.append(item)
        conn.close()

    return experiments

def get_experiment_by_id(exp_id):
    conn = get_connection()
    exp = None
    sql = """
        SELECT e.id, e.experiment_no, e.title, e.short_description, e.d2_heading, e.long_content, e.github_url, e.created_at,
               m_cover.media_url AS cover_url,
               m_video.media_url AS video_url
        FROM experiments e
        LEFT JOIN experiment_media m_cover ON e.id = m_cover.experiment_id AND m_cover.media_type = 'cover_image'
        LEFT JOIN experiment_media m_video ON e.id = m_video.experiment_id AND m_video.media_type = 'video'
        WHERE e.id = %s
    """ if ACTIVE_DB_TYPE == "mysql" else """
        SELECT e.id, e.experiment_no, e.title, e.short_description, e.d2_heading, e.long_content, e.github_url, e.created_at,
               m_cover.media_url AS cover_url,
               m_video.media_url AS video_url
        FROM experiments e
        LEFT JOIN experiment_media m_cover ON e.id = m_cover.experiment_id AND m_cover.media_type = 'cover_image'
        LEFT JOIN experiment_media m_video ON e.id = m_video.experiment_id AND m_video.media_type = 'video'
        WHERE e.id = ?
    """

    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (exp_id,))
        row = cursor.fetchone()
        if row:
            if row.get("created_at"):
                row["created_at"] = str(row["created_at"])
            exp = row
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute(sql, (exp_id,))
        row = cursor.fetchone()
        if row:
            exp = dict(row)
            if exp.get("created_at"):
                exp["created_at"] = str(exp["created_at"])
        conn.close()

    return exp

def create_experiment(experiment_no, title, short_description, d2_heading, long_content, github_url="", cover_url="", video_url=""):
    conn = get_connection()
    d2_head = d2_heading.strip() if d2_heading and d2_heading.strip() else "Long Description"

    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (experiment_no, title, short_description, d2_head, long_content, github_url or ""))
        exp_id = cursor.lastrowid

        if cover_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (%s, 'cover_image', %s)
            """, (exp_id, cover_url))

        if video_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (%s, 'video', %s)
            """, (exp_id, video_url))

        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO experiments (experiment_no, title, short_description, d2_heading, long_content, github_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (experiment_no, title, short_description, d2_head, long_content, github_url or ""))
        exp_id = cursor.lastrowid

        if cover_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (?, 'cover_image', ?)
            """, (exp_id, cover_url))

        if video_url:
            cursor.execute("""
                INSERT INTO experiment_media (experiment_id, media_type, media_url)
                VALUES (?, 'video', ?)
            """, (exp_id, video_url))

        conn.commit()
        conn.close()

    return get_experiment_by_id(exp_id)

def delete_experiment(exp_id):
    conn = get_connection()
    media_files = []

    # First fetch any media URLs associated with this experiment
    if ACTIVE_DB_TYPE == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT media_url FROM experiment_media WHERE experiment_id = %s", (exp_id,))
        media_files = [r["media_url"] for r in cursor.fetchall()]
        cursor.execute("DELETE FROM experiments WHERE id = %s", (exp_id,))
        cursor.close()
        conn.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT media_url FROM experiment_media WHERE experiment_id = ?", (exp_id,))
        media_files = [r[0] for r in cursor.fetchall()]
        cursor.execute("DELETE FROM experiment_media WHERE experiment_id = ?", (exp_id,))
        cursor.execute("DELETE FROM experiments WHERE id = ?", (exp_id,))
        conn.commit()
        conn.close()

    return media_files
