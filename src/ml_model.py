"""Salary prediction and attendance risk ML models."""

from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
PREDICTIONS = ROOT / "outputs" / "predictions"

def _preprocessor(numeric, categorical):
    return ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), numeric),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), categorical),
    ])

def train_salary_models():
    df = pd.read_csv(PROCESSED / "employee_features.csv")
    target = "Monthly_Salary"
    features = ["Age", "Department", "Job_Role", "Experience_Years",
                "Attendance_Percentage", "Average_Work_Hours", "Total_Overtime_Hours"]
    df = df.dropna(subset=[target]).copy()

    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    numeric = ["Age", "Experience_Years", "Attendance_Percentage",
               "Average_Work_Hours", "Total_Overtime_Hours"]
    categorical = ["Department", "Job_Role"]

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=250, random_state=42, min_samples_leaf=2),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42, n_estimators=150)
    }

    results = []
    fitted = {}
    for name, estimator in models.items():
        pipe = Pipeline([
            ("preprocessor", _preprocessor(numeric, categorical)),
            ("model", estimator)
        ])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        mse = mean_squared_error(y_test, pred)
        results.append({
            "Model": name,
            "MAE": mean_absolute_error(y_test, pred),
            "MSE": mse,
            "RMSE": np.sqrt(mse),
            "R2": r2_score(y_test, pred)
        })
        fitted[name] = pipe

    results_df = pd.DataFrame(results)
    # Select based on a balanced combination of RMSE and R2, while documenting all models.
    best_name = results_df.sort_values(["RMSE", "R2"], ascending=[True, False]).iloc[0]["Model"]
    best_model = fitted[best_name]

    MODELS.mkdir(exist_ok=True)
    PREDICTIONS.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODELS / "salary_model.pkl")
    results_df.to_csv(PREDICTIONS / "salary_model_comparison.csv", index=False)

    return results_df, best_name

def train_attendance_risk_model():
    df = pd.read_csv(PROCESSED / "employee_features.csv")

    def get_col(row, name):
        if name in row.index:
            return row[name]
        if f"{name}_y" in row.index:
            return row[f"{name}_y"]
        if f"{name}_x" in row.index:
            return row[f"{name}_x"]
        raise KeyError(name)

    def risk(row):
        attendance = get_col(row, "Attendance_Percentage")
        absent = get_col(row, "Days_Absent")
        late_count = get_col(row, "Late_Count")
        # Thresholds are calibrated for the 12-month simulated dataset.
        if attendance < 85 or absent >= 15 or late_count >= 28:
            return "High"
        if attendance < 92 or absent >= 8 or late_count >= 18:
            return "Medium"
        return "Low"

    df["Attendance_Risk"] = df.apply(risk, axis=1)

    # Resolve duplicated feature names if an older feature file exists.
    rename_map = {}
    for base in ["Days_Absent", "Days_On_Leave", "Days_Present"]:
        if base not in df.columns:
            for candidate in [f"{base}_y", f"{base}_x"]:
                if candidate in df.columns:
                    rename_map[candidate] = base
                    break
    df = df.rename(columns=rename_map)

    features = ["Age", "Department", "Job_Role", "Experience_Years",
                "Attendance_Percentage", "Days_Absent", "Days_On_Leave",
                "Average_Work_Hours", "Total_Overtime_Hours", "Average_Late_Minutes"]
    X = df[features]
    y = df["Attendance_Risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    numeric = ["Age", "Experience_Years", "Attendance_Percentage",
               "Days_Absent", "Days_On_Leave", "Average_Work_Hours",
               "Total_Overtime_Hours", "Average_Late_Minutes"]
    categorical = ["Department", "Job_Role"]

    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced")
    }

    results = []
    fitted = {}
    for name, estimator in models.items():
        pipe = Pipeline([
            ("preprocessor", _preprocessor(numeric, categorical)),
            ("model", estimator)
        ])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        results.append({
            "Model": name,
            "Accuracy": accuracy_score(y_test, pred),
            "Precision": precision_score(y_test, pred, average="weighted", zero_division=0),
            "Recall": recall_score(y_test, pred, average="weighted", zero_division=0),
            "F1": f1_score(y_test, pred, average="weighted", zero_division=0),
        })
        fitted[name] = pipe

    results_df = pd.DataFrame(results)
    best_name = results_df.sort_values(["F1", "Recall"], ascending=[False, False]).iloc[0]["Model"]
    best_model = fitted[best_name]

    joblib.dump(best_model, MODELS / "attendance_risk_model.pkl")
    results_df.to_csv(PREDICTIONS / "attendance_risk_model_comparison.csv", index=False)

    pred_all = best_model.predict(X)
    risk_output = df[["Employee_ID", "Employee_Name"]].copy()
    risk_output["Attendance_Risk"] = pred_all
    risk_output.to_csv(PREDICTIONS / "attendance_risk_predictions.csv", index=False)

    return results_df, best_name

if __name__ == "__main__":
    salary_results, salary_best = train_salary_models()
    risk_results, risk_best = train_attendance_risk_model()
    print("Salary models:")
    print(salary_results.to_string(index=False))
    print(f"\nSelected salary model: {salary_best}")
    print("\nAttendance risk models:")
    print(risk_results.to_string(index=False))
    print(f"\nSelected attendance risk model: {risk_best}")
