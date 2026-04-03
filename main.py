from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import os

app = FastAPI()

# 1. OPEN ALL GATES (Temporary for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. LOAD MODEL SAFELY
model = None
try:
    if os.path.exists("model.pkl"):
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
    else:
        print("Warning: model.pkl not found!")
except Exception as e:
    print(f"Error loading model: {e}")

@app.get("/")
def health_check():
    return {"status": "online", "message": "Nuclear AI Backend is reaching the frontend"}

@app.post("/predict")
async def predict_status(data: dict):
    # This 'dict' ensures we don't get 422 errors
    try:
        # Extract only what the model needs, providing defaults if missing
        temp = float(data.get('temp', 300))
        press = float(data.get('pressure', 15.0))
        vib = float(data.get('vibration', 0.1))
        rad = float(data.get('radiation', 100))
        flow = float(data.get('coolant_flow', 17000))

        if model:
            features = [[temp, press, vib, rad, flow]]
            prediction = model.predict(features)
            result = "CRITICAL" if prediction[0] == 1 else "STABLE"
        else:
            result = "Model not loaded, but connection successful!"

        return {
            "status": "success",
            "analysis": result,
            "received_data": data  # This helps us see what the UI sent
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
