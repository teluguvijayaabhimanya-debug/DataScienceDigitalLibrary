-- Data Science Laboratory (DS LAB) Database Schema
-- Database: ds_lab

CREATE DATABASE IF NOT EXISTS ds_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ds_lab;

-- 1. Student Table
CREATE TABLE IF NOT EXISTS student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'Venkatesh Rao',
    roll_no VARCHAR(100) NOT NULL DEFAULT '22A91A0501',
    section VARCHAR(50) NOT NULL DEFAULT 'DS-A',
    branch VARCHAR(100) NOT NULL DEFAULT 'Data Science & AI',
    assistant_professor VARCHAR(255) NOT NULL DEFAULT 'Dr. K. Sharma',
    photo_url VARCHAR(500) DEFAULT '',
    github_url VARCHAR(500) DEFAULT 'https://github.com/example/ds-lab-records',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Experiments Table
CREATE TABLE IF NOT EXISTS experiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_no VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    short_description TEXT NOT NULL,
    d2_heading VARCHAR(255) DEFAULT 'Long Description',
    long_content MEDIUMTEXT NOT NULL,
    github_url VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Experiment Media Table (images and videos)
CREATE TABLE IF NOT EXISTS experiment_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    experiment_id INT NOT NULL,
    media_type ENUM('cover_image', 'video', 'image') NOT NULL,
    media_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

-- Insert initial student profile if not exists
INSERT INTO student (id, name, roll_no, section, branch, assistant_professor, photo_url, github_url)
SELECT 1, 'K. Sai Venkatesh', '22A91A0542', 'DS-B', 'Data Science & AI', 'Dr. P. Rajesh Kumar', '', 'https://github.com/saivenkatesh/ds-laboratory'
WHERE NOT EXISTS (SELECT 1 FROM student WHERE id = 1);

-- Insert a sample experiment if experiments table is empty
INSERT INTO experiments (id, experiment_no, title, short_description, d2_heading, long_content, github_url)
SELECT 
    1,
    '01',
    'Data Cleaning and Exploratory Data Analysis (EDA)',
    'Preprocessing raw structured datasets, handling missing values, identifying outliers, and generating statistical summaries using Pandas and Seaborn.',
    'Experiment Report: EDA & Data Preprocessing',
    'AIM:\nTo perform data wrangling, missing value imputation, outlier detection, and exploratory statistical analysis on a customer dataset using Python, Pandas, and Matplotlib.\n\nPROCEDURE:\n1. Load the raw CSV dataset into a Pandas DataFrame.\n2. Inspect data types, null values, and summary statistics using df.info() and df.describe().\n3. Impute missing numerical attributes with median values and categorical fields with mode.\n4. Detect outliers using the Interquartile Range (IQR) technique and visualize via Boxplots.\n5. Compute correlation matrix and visualize correlations using Seaborn heatmaps.\n6. Generate univariate and bivariate distribution plots for target features.\n\nOBSERVATIONS & OUTPUT:\n- Missing values accounted for 4.2% of the total dataset in the income column, successfully imputed.\n- Removed 18 extreme multivariate outlier records.\n- Strong positive correlation (r = 0.82) observed between spending score and purchase frequency.\n\nCONCLUSION:\nThe dataset was successfully cleaned and standardized. Exploratory data analysis provided crucial feature distribution insights ready for downstream predictive modeling.',
    'https://github.com/saivenkatesh/ds-laboratory/tree/main/exp01_eda'
WHERE NOT EXISTS (SELECT 1 FROM experiments WHERE id = 1);

-- Insert cover image for sample experiment if not exists
INSERT INTO experiment_media (experiment_id, media_type, media_url)
SELECT 1, 'cover_image', '/static/uploads/images/sample_eda_cover.png'
WHERE NOT EXISTS (SELECT 1 FROM experiment_media WHERE experiment_id = 1 AND media_type = 'cover_image');
