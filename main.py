from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Nuclear AI - ARCS Enterprise v2.0")

# --- SECURITY SETTINGS (CORS) ---
# This allows your Netlify site to talk to this backend
origins = [
    "https://nuclearaiphase1.netlify.app",
    "http://localhost:3000",
    "https://nuclear-ai.onrender.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the AI Brain
model = joblib.load('model.pkl')

class AdvancedReactorData(BaseModel):
    temp: float
    pressure: float
    vibration: float
    radiation: float
    coolant_flow: float

@app.get("/")
def status():
    return {"status": "Nuclear AI Online", "version": "2.0"}

@app.post("/predict")
def predict_status(data: dict):  # We use 'dict' to accept all incoming fields
    try:
        # 1. Print the data to the Render logs so you can see what is coming in
        print(f"Incoming Simulation Data: {data}")

        # 2. Extract the specific 5 fields your model needs to run
        # We use .get() to avoid crashing if a field is missing
        features = [[
            data.get('temp', 0),
            data.get('pressure', 0),
            data.get('vibration', 0),
            data.get('radiation', 0),
            data.get('coolant_flow', 0)
        ]]

        # 3. Run the AI prediction
        prediction = model.predict(features)
        prob = model.predict_proba(features)[0][prediction[0]] * 100

        result = "CRITICAL: MELTDOWN RISK" if prediction[0] == 1 else "STABLE"

        return {
            "status": "success",
            "analysis": result,
            "confidence_level": f"{prob:.2f}%",
            "received_fields": list(data.keys()) # Shows you what the UI sent
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}