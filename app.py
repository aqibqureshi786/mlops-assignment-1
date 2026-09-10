import os
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI(title="student-ml-api")

# Read version from the VERSION file
VERSION_FILE = Path(__file__).parent / "VERSION"
APP_VERSION = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "1.0.0"

# Load the trained model if present
MODEL_FILE = Path(__file__).parent / "model.joblib"
model = joblib.load(MODEL_FILE) if MODEL_FILE.exists() else None


class PredictionRequest(BaseModel):
    value: float


class PredictionResponse(BaseModel):
    input: float
    prediction: float


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": "student-ml-api",
        "version": APP_VERSION
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    if model is not None:
        pred = round(float(model.predict([[payload.value]])[0]), 4)
    else:
        pred = round(float(payload.value * 2), 4)
    return {
        "input": payload.value,
        "prediction": pred
    }