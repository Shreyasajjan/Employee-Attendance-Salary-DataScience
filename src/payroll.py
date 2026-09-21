"""Transparent project-assumption payroll calculations.

IMPORTANT:
These are educational/project assumptions, not official Indian payroll or tax rules.
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

DEFAULT_PF_RATE = 0.12
DEFAULT_TAX_RATE = 0.05
OVERTIME_MULTIPLIER = 1.5
BONUS_RATE = 0.05

def calculate_attendance_percentage(present_days, working_days):
    return round((present_days / working_days) * 100, 2) if working_days else 0.0

def calculate_overtime_pay(monthly_salary, overtime_hours, payroll_days=26):
    hourly_rate = monthly_salary / payroll_days / 8
    return round(overtime_hours * hourly_rate * OVERTIME_MULTIPLIER, 2)

def calculate_attendance_bonus(basic_pay, attendance_percentage, overtime_hours):
    if attendance_percentage >= 95 and overtime_hours > 0:
        return round(basic_pay * BONUS_RATE, 2)
    return 0.0

def calculate_payroll(employees, attendance):
    att = attendance.copy()
    att["Date"] = pd.to_datetime(att["Date"])

    # Use actual weekdays represented in the period.
    working_days = int((att["Date"].dt.dayofweek < 5).sum() / max(att["Employee_ID"].nunique(), 1))
    working_days = max(working_days, 1)

    records = []
    for _, emp in employees.iterrows():
        ea = att[att["Employee_ID"] == emp["Employee_ID"]].copy()
        eligible = ea[ea["Attendance_Status"].isin(["Present", "Late"])]
        present = len(eligible)
        absent = int((ea["Attendance_Status"] == "Absent").sum())
        leave = int((ea["Attendance_Status"] == "Leave").sum())
        overtime = float(ea["Overtime_Hours"].sum())
        total_hours = float(ea["Work_Hours"].sum())

        attendance_pct = calculate_attendance_percentage(present, working_days)
        daily_salary = emp["Monthly_Salary"] / working_days
        basic_pay = daily_salary * present
        overtime_pay = calculate_overtime_pay(emp["Monthly_Salary"], overtime, working_days)
        bonus = calculate_attendance_bonus(basic_pay, attendance_pct, overtime)

        gross = basic_pay + overtime_pay + bonus
        pf = round(basic_pay * DEFAULT_PF_RATE, 2)
        taxable_base = max(gross - pf, 0)
        tax = round(taxable_base * DEFAULT_TAX_RATE, 2)
        other = round(max(0, absent - 2) * daily_salary * 0.5, 2)
        net = max(gross - pf - tax - other, 0)

        records.append({
            "Employee_ID": emp["Employee_ID"],
            "Employee_Name": emp["Employee_Name"],
            "Department": emp["Department"],
            "Job_Role": emp["Job_Role"],
            "Monthly_Salary": emp["Monthly_Salary"],
            "Working_Days": working_days,
            "Days_Present": present,
            "Days_Absent": absent,
            "Days_On_Leave": leave,
            "Attendance_Percentage": attendance_pct,
            "Total_Work_Hours": round(total_hours, 2),
            "Overtime_Hours": round(overtime, 2),
            "Overtime_Pay": overtime_pay,
            "Attendance_Bonus": bonus,
            "Basic_Pay": round(basic_pay, 2),
            "Gross_Salary": round(gross, 2),
            "PF_Deduction": pf,
            "Tax_Deduction": tax,
            "Other_Deductions": other,
            "Net_Salary": round(net, 2),
        })

    payroll = pd.DataFrame(records)
    payroll.to_csv(PROCESSED / "payroll_processed.csv", index=False)
    return payroll

if __name__ == "__main__":
    employees = pd.read_csv(PROCESSED / "cleaned_employees.csv")
    attendance = pd.read_csv(PROCESSED / "cleaned_attendance.csv")
    payroll = calculate_payroll(employees, attendance)
    print(payroll.head().to_string(index=False))
