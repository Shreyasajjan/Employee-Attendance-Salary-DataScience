"""Attendance anomaly detection using Isolation Forest."""

from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
OUTPUTS = ROOT / "outputs" / "predictions"

def detect_anomalies():
    att = pd.read_csv(PROCESSED / "cleaned_attendance.csv", parse_dates=["Date"])
    features = att[["Work_Hours", "Overtime_Hours", "Late_Minutes"]].fillna(0)
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42
    )
    prediction = model.fit_predict(X)
    score = model.decision_function(X)

    result = att[["Employee_ID", "Date", "Attendance_Status"]].copy()
    result["Anomaly_Score"] = score.round(5)
    result["Anomaly_Status"] = np.where(prediction == -1, "Anomaly", "Normal")

    MODELS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "scaler": scaler}, MODELS / "anomaly_model.pkl")
    result.to_csv(OUTPUTS / "attendance_anomalies.csv", index=False)
    return result

if __name__ == "__main__":
    result = detect_anomalies()
    print(result["Anomaly_Status"].value_counts())
