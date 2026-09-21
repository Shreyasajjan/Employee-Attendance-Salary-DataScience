"""Feature engineering for attendance and payroll analytics."""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

def build_features():
    att = pd.read_csv(PROCESSED / "cleaned_attendance.csv", parse_dates=["Date"])
    employees = pd.read_csv(PROCESSED / "cleaned_employees.csv", parse_dates=["Joining_Date"])
    payroll = pd.read_csv(PROCESSED / "payroll_processed.csv")

    att["Month"] = att["Date"].dt.to_period("M").astype(str)
    att["Week"] = att["Date"].dt.isocalendar().week.astype(int)
    att["Day_of_Week"] = att["Date"].dt.day_name()
    att["Is_Weekend"] = att["Date"].dt.dayofweek >= 5
    att["Is_Late"] = att["Attendance_Status"].eq("Late").astype(int)
    att["Is_Overtime"] = (att["Overtime_Hours"] > 0).astype(int)

    summary = att.groupby("Employee_ID").agg(
        Average_Work_Hours=("Work_Hours", "mean"),
        Total_Overtime_Hours=("Overtime_Hours", "sum"),
        Average_Late_Minutes=("Late_Minutes", "mean"),
        Late_Count=("Is_Late", "sum"),
    ).reset_index()

    features = employees.merge(summary, on="Employee_ID", how="left").merge(
        payroll, on=["Employee_ID", "Employee_Name", "Department", "Job_Role", "Monthly_Salary"], how="left"
    )

    features["Experience_Years"] = (
        (pd.Timestamp("2026-08-31") - features["Joining_Date"]).dt.days / 365.25
    ).round(2)
    features["Salary_Per_Working_Day"] = (
        features["Monthly_Salary"] / features["Working_Days"].replace(0, np.nan)
    ).fillna(0).round(2)
    features["Attendance_Percentage"] = features["Attendance_Percentage"].fillna(0)
    features["Days_Present"] = features["Days_Present"].fillna(0)
    features["Days_Absent"] = features["Days_Absent"].fillna(0)
    features["Days_On_Leave"] = features["Days_On_Leave"].fillna(0)
    features["Average_Work_Hours"] = features["Average_Work_Hours"].fillna(0)
    features["Total_Overtime_Hours"] = features["Total_Overtime_Hours"].fillna(0)
    features["Average_Late_Minutes"] = features["Average_Late_Minutes"].fillna(0)
    features["Late_Count"] = features["Late_Count"].fillna(0)

    features.to_csv(PROCESSED / "employee_features.csv", index=False)
    return att, features

if __name__ == "__main__":
    build_features()
    print("Feature engineering completed.")
