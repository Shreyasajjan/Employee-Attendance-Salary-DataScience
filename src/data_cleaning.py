"""Clean and validate raw employee attendance data."""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

VALID_STATUSES = {"Present", "Late", "Absent", "Leave", "Holiday"}

def clean_data():
    employees = pd.read_csv(RAW / "employees.csv")
    attendance = pd.read_csv(RAW / "attendance.csv")

    employees["Joining_Date"] = pd.to_datetime(employees["Joining_Date"], errors="coerce")
    employees["Monthly_Salary"] = pd.to_numeric(employees["Monthly_Salary"], errors="coerce")
    attendance["Date"] = pd.to_datetime(attendance["Date"], errors="coerce")
    attendance["Work_Hours"] = pd.to_numeric(attendance["Work_Hours"], errors="coerce")
    attendance["Overtime_Hours"] = pd.to_numeric(attendance["Overtime_Hours"], errors="coerce")
    attendance["Late_Minutes"] = pd.to_numeric(attendance["Late_Minutes"], errors="coerce")

    # Remove impossible employee salaries.
    employees.loc[employees["Monthly_Salary"] < 0, "Monthly_Salary"] = np.nan
    employees["Monthly_Salary"] = employees["Monthly_Salary"].fillna(
        employees["Monthly_Salary"].median()
    )

    # Normalize attendance status.
    attendance["Attendance_Status"] = attendance["Attendance_Status"].astype(str).str.strip()
    attendance.loc[~attendance["Attendance_Status"].isin(VALID_STATUSES), "Attendance_Status"] = "Absent"

    # Remove duplicate employee/date attendance rows.
    attendance = attendance.sort_values(["Employee_ID", "Date"])
    attendance = attendance.drop_duplicates(["Employee_ID", "Date"], keep="first")

    # Fill critical numeric fields safely.
    attendance["Work_Hours"] = attendance["Work_Hours"].fillna(0).clip(lower=0, upper=24)
    attendance["Overtime_Hours"] = attendance["Overtime_Hours"].fillna(0).clip(lower=0, upper=12)
    attendance["Late_Minutes"] = attendance["Late_Minutes"].fillna(0).clip(lower=0, upper=600)

    # Holiday/absent/leave cannot have working hours.
    non_work = attendance["Attendance_Status"].isin(["Holiday", "Absent", "Leave"])
    attendance.loc[non_work, ["Work_Hours", "Overtime_Hours"]] = 0

    # Recompute overtime consistently.
    attendance["Overtime_Hours"] = np.maximum(attendance["Work_Hours"] - 8, 0).round(2)

    # Validate employee IDs.
    valid_ids = set(employees["Employee_ID"])
    attendance = attendance[attendance["Employee_ID"].isin(valid_ids)].copy()

    PROCESSED.mkdir(parents=True, exist_ok=True)
    employees.to_csv(PROCESSED / "cleaned_employees.csv", index=False)
    attendance.to_csv(PROCESSED / "cleaned_attendance.csv", index=False)

    quality = {
        "employee_rows": len(employees),
        "attendance_rows": len(attendance),
        "duplicate_employee_ids": int(employees["Employee_ID"].duplicated().sum()),
        "duplicate_attendance_keys": int(attendance.duplicated(["Employee_ID", "Date"]).sum()),
        "missing_employee_ids": int(attendance["Employee_ID"].isna().sum()),
        "negative_salary": int((employees["Monthly_Salary"] < 0).sum()),
        "negative_work_hours": int((attendance["Work_Hours"] < 0).sum()),
        "invalid_status": int((~attendance["Attendance_Status"].isin(VALID_STATUSES)).sum()),
    }
    pd.DataFrame([quality]).to_csv(PROCESSED / "data_quality_report.csv", index=False)
    return employees, attendance, quality

if __name__ == "__main__":
    _, _, report = clean_data()
    print(pd.DataFrame([report]).T.to_string(header=False))
