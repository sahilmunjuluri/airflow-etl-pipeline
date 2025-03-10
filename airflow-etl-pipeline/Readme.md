## 📌 Airflow DAG Workflow
This pipeline is designed to process and load data efficiently using Apache Airflow.

### 1️⃣ **Staging Data**
- `stage_redshift.py` → Loads raw JSON logs and song data from **AWS S3** into **AWS Redshift staging tables**.

### 2️⃣ **Processing & Loading**
- `load_fact.py` → Inserts transformed data into the **fact table** (`songplays`).
- `load_dimension.py` → Loads structured data into **dimension tables** (`users`, `songs`, `artists`, `time`).

### 3️⃣ **Data Quality Checks**
- `data_quality.py` → Runs validation checks to ensure the integrity of data in Redshift.

---

## 🚀 Running the Pipeline
Follow these steps to execute the Airflow DAG and process data.

### 1️⃣ **Initialize Airflow**
Run the following commands in your terminal:

```bash
airflow db init  # Set up the Airflow metadata database
airflow scheduler &  # Start the scheduler to manage task execution
airflow webserver -p 8080  # Launch the Airflow web interface

