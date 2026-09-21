# Real-Time Employee Attendance and Salary Processing System

A complete end-to-end Data Science and Analytics project for simulated employee attendance, payroll processing, machine learning, anomaly detection, SQL analytics, and interactive visualization.

> **Important:** The "real-time" component is a simulated attendance feed. No biometric device is integrated. Payroll/tax/PF values are educational project assumptions and are not official Indian payroll or tax rules.

## 1. Objectives

- Store employee and attendance information.
- Clean and validate attendance data.
- Analyze attendance, work hours, overtime and salary.
- Engineer payroll and attendance features.
- Calculate project-assumption payroll.
- Perform statistical analysis.
- Predict salary using regression.
- Predict attendance risk using classification.
- Detect attendance anomalies using Isolation Forest.
- Store data in SQLite.
- Provide an interactive Streamlit + Plotly dashboard.
- Generate reproducible outputs and tests.

## 2. Technology Stack

Python, Pandas, NumPy, Matplotlib, Seaborn, SciPy, Scikit-learn, SQLite, Joblib, Plotly, Streamlit, Jupyter and Pytest.

## 3. Pipeline

Raw Data → Validation → Cleaning → EDA → Feature Engineering → Payroll → Statistical Analysis → Machine Learning → Anomaly Detection → SQL → Dashboard → Business Insights

## 4. Project Structure

```text
Employee-Attendance-Salary-DataScience/
├── data/
│   ├── raw/
│   ├── processed/
│   └── database/
├── notebooks/
├── src/
├── sql/
├── models/
├── dashboard/
├── outputs/
├── tests/
├── requirements.txt
├── run_project.py
└── README.md
```

## 5. Installation — Windows / VS Code

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 6. Run the complete pipeline

```powershell
python run_project.py
```

This generates:
- raw employee and attendance datasets
- cleaned datasets
- payroll dataset
- feature dataset
- ML model comparison results
- saved models
- anomaly results
- SQLite database

## 7. Run tests

```powershell
pytest
```

## 8. Run dashboard

```powershell
streamlit run dashboard/app.py
```

## 9. Dataset

The generator creates 100 employees and approximately one year of daily attendance records, including Present, Late, Absent, Leave and Holiday statuses. Small amounts of missing data, duplicates and intentionally unusual attendance values are inserted so that the cleaning and anomaly-detection stages are meaningful.

## 10. Payroll assumptions

- Daily Salary = Monthly Salary / payroll working days.
- Overtime Rate = Hourly Rate × 1.5.
- Attendance bonus = 5% of basic pay when attendance >= 95% and overtime > 0.
- PF deduction = 12% of basic pay.
- Project tax assumption = 5% of gross salary after PF.
- Other deductions are simulated for excessive absence.

These are **project assumptions**, not legal or official payroll rules.

## 11. Machine Learning

### Salary Regression
Models:
- Linear Regression
- Random Forest Regressor
- Gradient Boosting Regressor

Metrics:
- MAE
- MSE
- RMSE
- R²

### Attendance Risk Classification
Classes:
- Low
- Medium
- High

Models:
- Logistic Regression
- Decision Tree
- Random Forest

Metrics:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

### Anomaly Detection
Isolation Forest is used on:
- Work hours
- Overtime hours
- Late minutes

## 12. Statistical Analysis

The project can investigate:
- attendance and salary association
- overtime and salary association
- department and salary differences
- experience and salary association
- overtime and net salary association
- late arrivals and attendance

Correlation does not establish causation.

## 13. SQL

SQLite tables:
- employees
- attendance
- payroll

SQL examples include department salary, attendance, overtime, high/low attendance, salary expense and employee payroll reports.

## 14. Dashboard

The Streamlit dashboard contains:
- KPI cards
- department filters
- employee filters
- month filters
- attendance analytics
- salary analytics
- employee details
- ML risk predictions
- anomaly records
- simulated real-time disclaimer

## 15. Data Quality

The pipeline validates:
- duplicate employee IDs
- duplicate employee/date records
- negative salaries
- negative work hours
- invalid statuses
- missing critical employee IDs
- impossible attendance percentages
- negative net salary

## 16. Limitations

- Dataset is simulated because real employee payroll data is private.
- Payroll calculations are educational assumptions.
- Real-time attendance is simulated.
- ML predictions should not be used for actual HR/payroll decisions without appropriate validation, governance and privacy controls.

## 17. Future Scope

- biometric integration
- RFID
- mobile attendance
- cloud database
- real-time APIs
- notifications
- payroll software integration
- employee self-service
- advanced explainable AI
- cloud deployment

## 18. Final-Year Report Chapters

1. Introduction
2. Problem Statement
3. Objectives
4. Literature / Background
5. System Requirements
6. Methodology
7. Dataset
8. Data Preprocessing
9. Exploratory Data Analysis
10. Feature Engineering
11. Statistical Analysis
12. Machine Learning
13. Anomaly Detection
14. SQL Database
15. Dashboard
16. Results and Findings
17. Limitations
18. Future Scope
19. Conclusion

## 19. Author

Add your name, college, department, GitHub repository and contact information before final submission.
