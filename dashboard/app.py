"""Streamlit dashboard for Employee Attendance & Salary Analytics."""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import joblib

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "database" / "employee_payroll.db"
MODEL_DIR = ROOT / "models"
PRED_DIR = ROOT / "outputs" / "predictions"

st.set_page_config(
    page_title="Employee Attendance & Salary Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("Employee Attendance & Salary Analytics Dashboard")
st.caption("Simulated Real-Time Employee Attendance and Salary Processing System")

if not DB.exists():
    st.error("Database not found. Run `python run_project.py` first.")
    st.stop()

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB)
    employees = pd.read_sql("SELECT * FROM employees", conn)
    attendance = pd.read_sql("SELECT * FROM attendance", conn, parse_dates=["Date"])
    payroll = pd.read_sql("SELECT * FROM payroll", conn)
    conn.close()
    return employees, attendance, payroll

employees, attendance, payroll = load_data()

st.sidebar.header("Filters")
departments = ["All"] + sorted(payroll["Department"].unique().tolist())
dept = st.sidebar.selectbox("Department", departments)

filtered_payroll = payroll.copy()
filtered_attendance = attendance.copy()

if dept != "All":
    ids = payroll.loc[payroll["Department"] == dept, "Employee_ID"]
    filtered_payroll = payroll[payroll["Employee_ID"].isin(ids)]
    filtered_attendance = attendance[attendance["Employee_ID"].isin(ids)]

employee_names = ["All"] + sorted(filtered_payroll["Employee_Name"].unique().tolist())
employee = st.sidebar.selectbox("Employee", employee_names)

if employee != "All":
    emp_id = filtered_payroll.loc[
        filtered_payroll["Employee_Name"] == employee, "Employee_ID"
    ].iloc[0]
    filtered_payroll = filtered_payroll[filtered_payroll["Employee_ID"] == emp_id]
    filtered_attendance = filtered_attendance[filtered_attendance["Employee_ID"] == emp_id]

months = sorted(filtered_attendance["Date"].dt.to_period("M").astype(str).unique())
month_options = ["All"] + months
month = st.sidebar.selectbox("Month", month_options)
if month != "All":
    filtered_attendance = filtered_attendance[
        filtered_attendance["Date"].dt.to_period("M").astype(str) == month
    ]

high_risk_path = PRED_DIR / "attendance_risk_predictions.csv"
if high_risk_path.exists():
    risks = pd.read_csv(high_risk_path)
    high_risk_count = int((risks["Attendance_Risk"] == "High").sum())
else:
    high_risk_count = 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Employees", len(filtered_payroll))
c2.metric("Avg Attendance", f"{filtered_payroll['Attendance_Percentage'].mean():.1f}%")
c3.metric("Salary Expense", f"₹{filtered_payroll['Net_Salary'].sum():,.0f}")
c4.metric("Avg Salary", f"₹{filtered_payroll['Net_Salary'].mean():,.0f}")
c5.metric("Overtime Hours", f"{filtered_payroll['Overtime_Hours'].sum():,.1f}")
c6.metric("High-Risk Employees", high_risk_count)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Attendance", "Salary", "Employee Details", "ML & Anomalies"
])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        dept_count = payroll.groupby("Department").size().reset_index(name="Employees")
        fig = px.bar(dept_count, x="Department", y="Employees", title="Employees by Department")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            filtered_payroll, x="Attendance_Percentage",
            nbins=15, title="Attendance Percentage Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    monthly = filtered_attendance.copy()
    monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)
    monthly = monthly[monthly["Attendance_Status"].isin(["Present", "Late"])]
    monthly_trend = monthly.groupby("Month").size().reset_index(name="Present_or_Late")
    fig = px.line(monthly_trend, x="Month", y="Present_or_Late",
                  markers=True, title="Monthly Attendance Trend")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    status = filtered_attendance["Attendance_Status"].value_counts().reset_index()
    status.columns = ["Status", "Count"]
    with col1:
        fig = px.pie(status, names="Status", values="Count", title="Attendance Status")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dept_att = payroll.groupby("Department")["Attendance_Percentage"].mean().reset_index()
        fig = px.bar(dept_att, x="Department", y="Attendance_Percentage",
                     title="Average Attendance by Department")
        st.plotly_chart(fig, use_container_width=True)

    ranking = payroll[["Employee_Name", "Department", "Attendance_Percentage"]].sort_values(
        "Attendance_Percentage", ascending=False
    )
    st.subheader("Employee Attendance Ranking")
    st.dataframe(ranking, use_container_width=True, hide_index=True)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        dept_salary = payroll.groupby("Department")["Net_Salary"].mean().reset_index()
        fig = px.bar(dept_salary, x="Department", y="Net_Salary",
                     title="Average Net Salary by Department")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(filtered_payroll, y="Net_Salary", x="Department",
                     title="Salary Distribution by Department")
        st.plotly_chart(fig, use_container_width=True)

    salary_detail = filtered_payroll[
        ["Employee_Name", "Department", "Gross_Salary", "Net_Salary",
         "Overtime_Pay", "PF_Deduction", "Tax_Deduction", "Other_Deductions"]
    ].sort_values("Net_Salary", ascending=False)
    st.dataframe(salary_detail, use_container_width=True, hide_index=True)

with tab4:
    selected = st.selectbox(
        "Select an employee",
        sorted(payroll["Employee_Name"].unique().tolist())
    )
    row = payroll[payroll["Employee_Name"] == selected].iloc[0]
    info = employees[employees["Employee_ID"] == row["Employee_ID"]].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Department", row["Department"])
    c2.metric("Attendance", f"{row['Attendance_Percentage']:.1f}%")
    c3.metric("Overtime", f"{row['Overtime_Hours']:.1f} hrs")
    c4.metric("Net Salary", f"₹{row['Net_Salary']:,.0f}")

    st.write({
        "Employee ID": row["Employee_ID"],
        "Role": row["Job_Role"],
        "Age": info["Age"],
        "Location": info["Location"],
        "Days Present": row["Days_Present"],
        "Days Absent": row["Days_Absent"],
        "Leave Days": row["Days_On_Leave"],
        "Gross Salary": row["Gross_Salary"],
        "Net Salary": row["Net_Salary"],
    })

    emp_att = attendance[attendance["Employee_ID"] == row["Employee_ID"]].copy()
    emp_att["Month"] = emp_att["Date"].dt.to_period("M").astype(str)
    trend = emp_att.groupby("Month")["Work_Hours"].mean().reset_index()
    fig = px.line(trend, x="Month", y="Work_Hours", markers=True,
                  title=f"Average Work Hours Trend — {selected}")
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Attendance Risk Predictions")
    risk_path = PRED_DIR / "attendance_risk_predictions.csv"
    if risk_path.exists():
        risk_df = pd.read_csv(risk_path)
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    else:
        st.info("Risk predictions are generated by the pipeline.")

    st.subheader("Anomaly Detection")
    anomaly_path = PRED_DIR / "attendance_anomalies.csv"
    if anomaly_path.exists():
        anomaly_df = pd.read_csv(anomaly_path)
        st.dataframe(
            anomaly_df[anomaly_df["Anomaly_Status"] == "Anomaly"],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Anomalies are generated by the pipeline.")

st.divider()
st.info(
    "Simulated Real-Time Attendance: this dashboard uses generated historical records "
    "and is not connected to a biometric device."
)
