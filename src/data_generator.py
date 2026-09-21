"""Generate reproducible simulated employee and attendance datasets."""

from pathlib import Path
from datetime import date, timedelta
import random
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

N_EMPLOYEES = 100
START_DATE = pd.Timestamp("2025-09-01")
END_DATE = pd.Timestamp("2026-08-31")

DEPARTMENTS = ["Engineering", "HR", "Finance", "Sales", "Marketing", "IT Support", "Operations"]
ROLES = {
    "Engineering": ["Software Engineer", "Data Analyst", "ML Engineer"],
    "HR": ["HR Executive", "HR Manager", "Recruiter"],
    "Finance": ["Accountant", "Financial Analyst", "Finance Manager"],
    "Sales": ["Sales Executive", "Sales Manager", "Business Development Executive"],
    "Marketing": ["Marketing Executive", "Digital Marketing Analyst", "Marketing Manager"],
    "IT Support": ["Support Engineer", "System Administrator", "IT Manager"],
    "Operations": ["Operations Executive", "Operations Analyst", "Operations Manager"],
}
LOCATIONS = ["Bengaluru", "Mangaluru", "Mysuru", "Hyderabad", "Pune"]
EMP_TYPES = ["Full-Time", "Part-Time", "Contract"]

FIRST_NAMES = [
    "Aarav","Aditya","Akash","Aishwarya","Ananya","Arjun","Bhavana","Chetan",
    "Deepa","Dhanush","Divya","Farhan","Gaurav","Harsh","Isha","Karan",
    "Kavya","Kiran","Lakshmi","Manoj","Meera","Naveen","Neha","Nikhil",
    "Pooja","Pranav","Priya","Rahul","Rakesh","Ravi","Riya","Rohit",
    "Sakshi","Sameer","Sanjay","Shreya","Sneha","Sonal","Tanvi","Varun"
]
LAST_NAMES = [
    "Kumar","Sharma","Patil","Reddy","Shetty","Gowda","Naik","Joshi",
    "Singh","Verma","Bhat","Hegde","Rao","Kulkarni","Desai","Iyer"
]

def generate_employees(n=N_EMPLOYEES):
    rows = []
    for i in range(n):
        emp_id = f"EMP{1001+i}"
        dept = random.choice(DEPARTMENTS)
        role = random.choice(ROLES[dept])
        experience = random.randint(0, 12)
        age = random.randint(21, min(55, 23 + experience + 25))
        base_by_dept = {
            "Engineering": 60000, "HR": 48000, "Finance": 52000,
            "Sales": 50000, "Marketing": 47000, "IT Support": 49000,
            "Operations": 46000
        }
        role_factor = {
            "Manager": 1.45, "Engineer": 1.15, "Analyst": 1.10,
            "Executive": 0.92, "Recruiter": 0.95, "Accountant": 1.0,
            "Developer": 1.12, "Administrator": 1.08
        }
        factor = 1.0
        for key, value in role_factor.items():
            if key.lower() in role.lower():
                factor = value
                break
        salary = int(np.clip(
            base_by_dept[dept] * factor + experience * 3500 + np.random.normal(0, 5000),
            25000, 180000
        ))
        joining = pd.Timestamp("2015-01-01") + pd.Timedelta(days=random.randint(0, 3650))
        rows.append({
            "Employee_ID": emp_id,
            "Employee_Name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "Gender": random.choice(["Male", "Female", "Other"]),
            "Age": age,
            "Department": dept,
            "Job_Role": role,
            "Joining_Date": joining.date().isoformat(),
            "Monthly_Salary": salary,
            "Employment_Type": random.choices(EMP_TYPES, weights=[0.78, 0.08, 0.14])[0],
            "Location": random.choice(LOCATIONS),
        })
    return pd.DataFrame(rows)

def time_string(minutes_from_midnight):
    h = int(minutes_from_midnight // 60)
    m = int(minutes_from_midnight % 60)
    return f"{h:02d}:{m:02d}"

def generate_attendance(employees):
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    rows = []
    for _, emp in employees.iterrows():
        reliability = np.random.beta(18, 2.2)  # generally high
        for d in dates:
            weekday = d.weekday()
            if weekday >= 5:
                # Keep weekends as Holiday; realistic and useful for analysis.
                rows.append({
                    "Date": d.date().isoformat(),
                    "Employee_ID": emp["Employee_ID"],
                    "Attendance_Status": "Holiday",
                    "Check_In": None,
                    "Check_Out": None,
                    "Work_Hours": 0.0,
                    "Overtime_Hours": 0.0,
                    "Leave_Type": None,
                    "Late_Minutes": 0,
                })
                continue

            u = random.random()
            # Employee-specific attendance reliability drives patterns.
            absent_p = 0.025 + (1-reliability)*0.12
            leave_p = 0.035 + (1-reliability)*0.08
            late_p = 0.07 + (1-reliability)*0.18

            if u < absent_p:
                status = "Absent"
                check_in = check_out = None
                work_hours = overtime = 0.0
                leave_type = None
                late = 0
            elif u < absent_p + leave_p:
                status = "Leave"
                check_in = check_out = None
                work_hours = overtime = 0.0
                leave_type = random.choice(["Casual Leave", "Sick Leave", "Earned Leave"])
                late = 0
            else:
                is_late = random.random() < late_p
                status = "Late" if is_late else "Present"
                late = random.randint(5, 75) if is_late else 0
                start_minutes = 9*60 + random.randint(0, 12) + late
                work_hours = float(np.clip(np.random.normal(8.3, 0.65), 5.5, 11.5))
                # Occasional early leaving.
                if random.random() < 0.04:
                    work_hours = float(np.clip(work_hours - random.uniform(0.5, 2.0), 4.5, 10))
                overtime = max(0.0, round(work_hours - 8.0, 2))
                check_in = time_string(start_minutes)
                checkout_minutes = start_minutes + int(work_hours * 60)
                check_out = time_string(checkout_minutes)
                leave_type = None

            rows.append({
                "Date": d.date().isoformat(),
                "Employee_ID": emp["Employee_ID"],
                "Attendance_Status": status,
                "Check_In": check_in,
                "Check_Out": check_out,
                "Work_Hours": round(work_hours, 2),
                "Overtime_Hours": round(overtime, 2),
                "Leave_Type": leave_type,
                "Late_Minutes": late,
            })

    attendance = pd.DataFrame(rows)

    # Intentionally inject a small number of data-quality issues for the cleaning stage.
    rng = np.random.default_rng(SEED)
    for col in ["Check_In", "Check_Out", "Late_Minutes"]:
        idx = rng.choice(attendance.index, size=8, replace=False)
        attendance.loc[idx, col] = np.nan

    # A few duplicate attendance records.
    duplicate_rows = attendance.sample(12, random_state=SEED)
    attendance = pd.concat([attendance, duplicate_rows], ignore_index=True)

    # A few explicit anomalies.
    anomaly_idx = rng.choice(attendance.index, size=12, replace=False)
    attendance.loc[anomaly_idx[:4], "Work_Hours"] = 16
    attendance.loc[anomaly_idx[4:8], "Overtime_Hours"] = 8
    attendance.loc[anomaly_idx[8:], "Late_Minutes"] = 240

    return attendance

def main():
    employees = generate_employees()
    attendance = generate_attendance(employees)
    employees.to_csv(RAW / "employees.csv", index=False)
    attendance.to_csv(RAW / "attendance.csv", index=False)
    print(f"Generated {len(employees):,} employees.")
    print(f"Generated {len(attendance):,} attendance records.")
    print(f"Saved to: {RAW}")

if __name__ == "__main__":
    main()
