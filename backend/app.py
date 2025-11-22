from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import joblib
import numpy as np
import os
from datetime import datetime, timedelta
import random
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Akatsuki — Hospital Traffic Predictor")

# ---------------------------------------------------------
# CORS (Frontend → Backend communication)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files at /static and provide a simple UI entry at /ui
# The `frontend` folder sits next to `backend`, so compute an absolute path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static_frontend")


@app.get("/ui")
def ui():
    # Serve the primary frontend file (index1.html) so users can open /ui
    index_path = os.path.join(FRONTEND_DIR, "index1.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"error": "frontend not found"}

# ---------------------------------------------------------
# MAPPINGS (must be ABOVE heuristic_predict)
# ---------------------------------------------------------
PROBLEM_SEVERITY = {
    "fever": 1,
    "cough_cold": 1,
    "stomach_pain": 2,
    "fracture": 3,
    "chest_pain": 4,
    "accident": 4,
    "pregnancy": 2,
    "child_illness": 2,
    "general_checkup": 0,
    "others": 1
}

HOSPITAL_PROFILES = {
    "Manipal": {"size": 3, "base_capacity": 100},
    "Apollo": {"size": 3, "base_capacity": 120},
    "Fortis": {"size": 3, "base_capacity": 110},
    "Govt PHC": {"size": 1, "base_capacity": 40},
    "Aster Clinic": {"size": 1, "base_capacity": 30}
}

# ---------------------------------------------------------
# Try loading trained models (optional)
# ---------------------------------------------------------
MODEL_CROWD_PATH = "model_crowd.joblib"
MODEL_WAIT_PATH = "model_wait.joblib"

model_crowd = None
model_wait = None

if os.path.exists(MODEL_CROWD_PATH):
    try:
        model_crowd = joblib.load(MODEL_CROWD_PATH)
        print("Crowd model loaded.")
    except Exception as e:
        print("Failed to load crowd model:", e)

if os.path.exists(MODEL_WAIT_PATH):
    try:
        model_wait = joblib.load(MODEL_WAIT_PATH)
        print("Wait model loaded.")
    except Exception as e:
        print("Failed to load wait model:", e)

# ---------------------------------------------------------
# NEW Improved Heuristic Model  (MAIN FIX)
# ---------------------------------------------------------
def heuristic_predict(
    hospital: str,
    hour: int,
    weekday: int,
    problem: str,
    pincode: Optional[str] = None
) -> Dict[str, Any]:

    hour = int(hour) % 24
    weekday = int(weekday) % 7

    severity = PROBLEM_SEVERITY.get(problem, 1)
    profile = HOSPITAL_PROFILES.get(hospital, {"size": 2, "base_capacity": 60})
    base_capacity = profile["base_capacity"]

    # More realistic time multipliers
    if 7 <= hour <= 10:
        t_mult = 1.6
    elif 17 <= hour <= 20:
        t_mult = 1.8
    elif 11 <= hour <= 16:
        t_mult = 1.2
    else:
        t_mult = 0.9

    # Weekends slightly lower
    w_mult = 0.85 if weekday >= 5 else 1.0

    # Simulated inflow
    inflow = max(5, int(base_capacity * (0.3 + random.random() * 0.6) * t_mult * w_mult))

    # Emergency based on severity
    emergency = max(
        1,
        int(inflow * (0.08 + 0.02 * severity) * (0.8 + random.random() * 0.8))
    )

    load_ratio = inflow / max(1, base_capacity)

    crowd_score = min(
        10.0,
        (load_ratio * 8) + (severity * 1.6) + ((emergency / inflow) * 4)
    )
    crowd_score = round(crowd_score, 2)

    wait_minutes = int(
        8 + (load_ratio * 75) + (severity * 10) + (emergency * 3)
    )

    # alternative hospital suggestions
    suggestions = []
    for hname, prof in HOSPITAL_PROFILES.items():
        if hname == hospital:
            continue
        cap = prof["base_capacity"]
        infl = max(5, int(cap * (0.2 + random.random() * 0.5)))
        ratio = infl / max(1, cap)
        est_wait = int(8 + ratio * 75 + 5)
        suggestions.append({"hospital": hname, "est_wait": est_wait})

    suggestions = sorted(suggestions, key=lambda x: x["est_wait"])[:3]

    return {
        "crowd_score": crowd_score,
        "wait_minutes": wait_minutes,
        "inflow_est": inflow,
        "emergency_est": emergency,
        "suggestions": suggestions
    }

# ---------------------------------------------------------
# Response Models
# ---------------------------------------------------------
class PredictRequest(BaseModel):
    hospital: str
    hour: Optional[int] = None
    weekday: Optional[int] = None
    problem: Optional[str] = "general_checkup"
    pincode: Optional[str] = None
    want_booking: Optional[bool] = False


class PredictResponse(BaseModel):
    hospital: str
    crowd_score: float
    crowd_category: str
    wait_minutes: int
    inflow_est: int
    emergency_est: int
    suggestions: List[Dict[str, Any]]
    recommended_slots: Optional[List[str]] = None


class BookRequest(BaseModel):
    hospital: str
    slot: str
    name: str
    phone: str
    fee_paid: float


class BookResponse(BaseModel):
    booking_id: str
    hospital: str
    slot: str
    token: str
    estimated_wait: int


# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------
def score_to_category(score: float) -> str:
    if score < 3.5:
        return "Low"
    if score < 6.5:
        return "Moderate"
    return "High"


def available_slots_for_hospital(hospital: str, after_minutes=0, count=6):
    now = datetime.now() + timedelta(minutes=after_minutes)
    slots = []
    for i in range(count):
        s = (now + timedelta(minutes=30 * i)).strftime("%Y-%m-%d %H:%M")
        slots.append(s)
    return slots


# ---------------------------------------------------------
# API ENDPOINTS
# ---------------------------------------------------------

@app.get("/")
def home():
    return {"status": "ok", "message": "Akatsuki API running"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):

    hour = req.hour if req.hour is not None else datetime.now().hour
    weekday = req.weekday if req.weekday is not None else datetime.now().weekday()

    hospital = req.hospital
    problem = req.problem or "general_checkup"

    # Always use heuristic (ML is optional)
    fallback = heuristic_predict(hospital, hour, weekday, problem, req.pincode)

    recommended = available_slots_for_hospital(hospital, after_minutes=10, count=4)

    return PredictResponse(
        hospital=hospital,
        crowd_score=fallback["crowd_score"],
        crowd_category=score_to_category(fallback["crowd_score"]),
        wait_minutes=fallback["wait_minutes"],
        inflow_est=fallback["inflow_est"],
        emergency_est=fallback["emergency_est"],
        suggestions=fallback["suggestions"],
        recommended_slots=recommended
    )


@app.post("/book", response_model=BookResponse)
def book(req: BookRequest):

    booking_id = "BK" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10, 99))
    token = str(random.randint(1000, 9999))

    fallback = heuristic_predict(req.hospital, datetime.now().hour, datetime.now().weekday(), "general_checkup")
    est_wait = max(5, int(fallback["wait_minutes"] * 0.7))

    return BookResponse(
        booking_id=booking_id,
        hospital=req.hospital,
        slot=req.slot,
        token=token,
        estimated_wait=est_wait
    )
