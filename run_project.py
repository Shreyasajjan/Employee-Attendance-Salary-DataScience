"""Run the complete reproducible project pipeline."""

from pathlib import Path
import sqlite3
import pandas as pd

from src.data_generator import main as generate_data
from src.data_cleaning import clean_data
from src.feature_engineering import build_features
from src.payroll import calculate_payroll
from src.ml_model import train_salary_models, train_attendance_risk_model
from src.anomaly_detection import detect_anomalies

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "database" / "employee_payroll.db"
SCHEMA = ROOT / "sql" / "schema.sql"

def build_database():
    employees = pd.read_csv(ROOT / "data" / "processed" / "cleaned_employees.csv")
    attendance = pd.read_csv(ROOT / "data" / "processed" / "cleaned_attendance.csv")
    payroll = pd.read_csv(ROOT / "data" / "processed" / "payroll_processed.csv")

    if DB.exists():
        DB.unlink()

    conn = sqlite3.connect(DB)
    with open(SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    employees.to_sql("employees", conn, if_exists="append", index=False)
    attendance.to_sql("attendance", conn, if_exists="append", index=False)
    payroll.to_sql("payroll", conn, if_exists="append", index=False)
    conn.close()

def main():
    print("\n=== 1. DATA GENERATION ===")
    generate_data()

    print("\n=== 2. DATA CLEANING ===")
    employees, attendance, quality = clean_data()
    print(quality)

    print("\n=== 3. PAYROLL PROCESSING ===")
    payroll = calculate_payroll(employees, attendance)
    print(f"Payroll records: {len(payroll)}")

    print("\n=== 4. FEATURE ENGINEERING ===")
    build_features()

    print("\n=== 5. MACHINE LEARNING ===")
    salary_results, salary_best = train_salary_models()
    risk_results, risk_best = train_attendance_risk_model()
    print(salary_results.to_string(index=False))
    print(f"Selected salary model: {salary_best}")
    print(risk_results.to_string(index=False))
    print(f"Selected attendance-risk model: {risk_best}")

    print("\n=== 6. ANOMALY DETECTION ===")
    anomalies = detect_anomalies()
    print(anomalies["Anomaly_Status"].value_counts().to_string())

    print("\n=== 7. SQLITE DATABASE ===")
    build_database()
    print(f"Database created: {DB}")

    print("\n=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    main()
