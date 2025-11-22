# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import joblib
import numpy as np
import os
from datetime import datetime, timedelta
import random

app = FastAPI(title="Akatsuki — Hospital Traffic Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load models if available (two models: crowd_score and wait_minutes)
MODEL_CROWD_PATH = "model_crowd.joblib"     # optional
MODEL_WAIT_PATH = "model_wait.joblib"       # optional

model_crowd = None
model_wait = None
if os.path.exists(MODEL_CROWD_PATH):
    try:
        model_crowd = joblib.load(MODEL_CROWD_PATH)
    except Exception as e:
        print("Failed to load crowd model:", e)
if os.path.exists(MODEL_WAIT_PATH):
    try:
        model_wait = joblib.load(MODEL_WAIT_PATH)
    except Exception as e:
        print("Failed to load wait model:", e)


# --- Helper mappings & fallback heuristics ---------------------------------
# Map problem types to severity (higher -> more wait)
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
    # Add the hospitals you simulated / want to demo
    "Manipal": {"size": 3, "base_capacity": 100},
    "Apollo": {"size": 3, "base_capacity": 120},
    "Fortis": {"size": 3, "base_capacity": 110},
    "Govt PHC": {"size": 1, "base_capacity": 40},
    "Aster Clinic": {"size": 1, "base_capacity": 30}
}

def safe_int(x, default=0):
    try:
        return int(x)
    except:
        return default

def heuristic_predict(hospital: str, hour: int, weekday: int, problem: str, pincode: Optional[str]=None) -> Dict[str, Any]:
    """Simple fallback heuristic to produce crowd_score (0-10) and wait_minutes"""
    hour = int(hour) % 24
    weekday = int(weekday) % 7
    severity = PROBLEM_SEVERITY.get(problem, 1)
    profile = HOSPITAL_PROFILES.get(hospital, {"size":2,"base_capacity":60})
    base_capacity = profile["base_capacity"]

    # time multiplier (peak morning and evening)
    if 8 <= hour <= 11:
        t_mult = 1.4
    elif 17 <= hour <= 20:
        t_mult = 1.6
    else:
        t_mult = 1.0

    # weekday effect: weekends slightly lower for many hospitals
    if weekday >= 5:
        w_mult = 0.8
    else:
        w_mult = 1.0

    # random rough "current inflow" simulation
    inflow = max(5, int(base_capacity * 0.2 * t_mult * w_mult * (0.8 + random.random()*0.8)))
    emergency = max(0, int(inflow * 0.08 * (1 + severity*0.2)))

    # crowd score roughly proportional to inflow / capacity + severity
    load_ratio = inflow / base_capacity
    crowd_score = min(10.0, (load_ratio * 6.0 + severity * 0.8) )
    # waiting time hacked formula
    wait_minutes = int(10 + (load_ratio * 60) + severity * 8 + emergency * 3)

    # suggestions: pick alternatives with lower simulated load
    suggestions = []
    for hname, prof in HOSPITAL_PROFILES.items():
        if hname == hospital:
            continue
        other_capacity = prof["base_capacity"]
        other_inflow = max(5, int(other_capacity * 0.18 * (0.9 + random.random()*0.6)))
        if other_inflow / other_capacity < load_ratio:
            suggestions.append({"hospital": hname, "est_wait": int(10 + (other_inflow/other_capacity)*60)})

    suggestions = sorted(suggestions, key=lambda x: x["est_wait"])[:3]

    return {"crowd_score": round(crowd_score,2),
            "wait_minutes": int(wait_minutes),
            "inflow_est": inflow,
            "emergency_est": emergency,
            "suggestions": suggestions}

# --- Request / Response models ---------------------------------------------
class PredictRequest(BaseModel):
    hospital: str
    hour: Optional[int] = None   # if missing, backend uses current hour
    weekday: Optional[int] = None  # 0=Mon
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


# --- Utility functions ----------------------------------------------------
def score_to_category(score: float) -> str:
    if score < 3.5: return "Low"
    if score < 6.5: return "Moderate"
    return "High"

def available_slots_for_hospital(hospital: str, after_minutes: int = 0, count: int = 6):
    """Generate some demo slots (strings)"""
    now = datetime.now() + timedelta(minutes=after_minutes)
    slots = []
    for i in range(count):
        s = (now + timedelta(minutes=30*i)).strftime("%Y-%m-%d %H:%M")
        slots.append(s)
    return slots

# --- API Endpoints --------------------------------------------------------
@app.get("/", tags=["health"])
def home():
    return {"status": "ok", "message": "Akatsuki Hospital Traffic Predictor API running"}

@app.post("/predict", response_model=PredictResponse, tags=["predict"])
def predict(req: PredictRequest):
    # fill defaults
    cur = datetime.now()
    hour = req.hour if req.hour is not None else cur.hour
    weekday = req.weekday if req.weekday is not None else cur.weekday()
    problem = req.problem or "general_checkup"
    hospital = req.hospital or list(HOSPITAL_PROFILES.keys())[0]

    # Build feature vector (same order your model expects)
    features = [hour, weekday, PROBLEM_SEVERITY.get(problem,1)]
    # If your model expects more features, extend here.

    # If models exist, use them
    try:
        if model_crowd is not None and model_wait is not None:
            X = np.array([ [hour, weekday, PROBLEM_SEVERITY.get(problem,1), 1] ])  # adjust shape to your trained features
            # Protect: if model expects different n_features, fallback to heuristic
            try:
                crowd = float(model_crowd.predict(X)[0])
                wait = int(model_wait.predict(X)[0])
            except Exception as e:
                # fallback
                fallback = heuristic_predict(hospital, hour, weekday, problem, req.pincode)
                crowd = fallback["crowd_score"]
                wait = fallback["wait_minutes"]
                suggestions = fallback["suggestions"]
                recommended = available_slots_for_hospital(hospital, after_minutes=10, count=4)
                return PredictResponse(
                    hospital=hospital,
                    crowd_score=crowd,
                    crowd_category=score_to_category(crowd),
                    wait_minutes=wait,
                    inflow_est=fallback["inflow_est"],
                    emergency_est=fallback["emergency_est"],
                    suggestions=suggestions,
                    recommended_slots=recommended
                )
            # if models worked
            suggestions = heuristic_predict(hospital, hour, weekday, problem, req.pincode)["suggestions"]
            recommended = available_slots_for_hospital(hospital, after_minutes=10, count=4)
            return PredictResponse(
                hospital=hospital,
                crowd_score=round(crowd,2),
                crowd_category=score_to_category(crowd),
                wait_minutes=wait,
                inflow_est=int(max(5, wait//4)),  # rough mapping for demo
                emergency_est=int(max(0, wait//20)),
                suggestions=suggestions,
                recommended_slots=recommended
            )
        else:
            # fallback heuristic
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/book", response_model=BookResponse, tags=["booking"])
def book(req: BookRequest):
    # Basic mock booking: generate booking id and token
    booking_id = "BK" + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(10,99))
    token = str(random.randint(1000,9999))
    # Estimated wait = heuristic / small random
    fallback = heuristic_predict(req.hospital, datetime.now().hour, datetime.now().weekday(), "general_checkup")
    est_wait = max(5, int(fallback["wait_minutes"] * 0.7))
    return BookResponse(
        booking_id=booking_id,
        hospital=req.hospital,
        slot=req.slot,
        token=token,
        estimated_wait=est_wait
    )
