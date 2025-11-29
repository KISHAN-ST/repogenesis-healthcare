# Akatsuki — Hospital Traffic Predictor

<<<<<<< HEAD
Akatsuki is a small demo/research project that predicts short-term hospital traffic (crowd and wait-time estimates) and provides a tiny booking API. It is implemented as a FastAPI backend with a minimal static frontend for demonstration and local testing.

This README explains how to run the API locally, how the frontend is served, and how to call the `/predict` and `/book` endpoints.

---

## Quick Links

- Backend entry: `backend/app.py`
- Frontend static files: `frontend/` (served at `/static` by the backend)
- UI entry endpoint: `/ui` (serves `index1.html`)

---

## Requirements

- Python 3.10+ recommended
- Create a virtual environment and install dependencies from `backend/requirements.txt`:

```powershell
cd akatsuki\backend
.\venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

If you don't have a `venv/` yet, create one first:

```powershell
python -m venv .venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run the API and serve the UI

From `akatsuki/backend` run:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

- Open `http://127.0.0.1:8000/ui` in your browser to load the frontend (`index1.html`).
- Static frontend files are mounted at `http://127.0.0.1:8000/static/*` (e.g. `predict.html` -> `/static/predict.html`).

---

## API Endpoints

All endpoints are defined in `backend/app.py` and accept/return JSON. Example requests below use `curl` or JavaScript `fetch`.

1) POST /predict

Request JSON (example):

```json
{
  "hospital": "Manipal",
  "hour": 14,
  "weekday": 2,
  "problem": "fever",
  "pincode": "560001",
  "want_booking": true
}
```

Response JSON (example):

```json
{
  "hospital": "Manipal",
  "crowd_score": 5.3,
  "crowd_category": "Moderate",
  "wait_minutes": 42,
  "inflow_est": 78,
  "emergency_est": 6,
  "suggestions": [{"hospital":"Apollo","est_wait":30}, ...],
  "recommended_slots": ["2025-11-22 14:00","2025-11-22 14:30"]
}
```

Example curl:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"hospital":"Manipal","hour":14,"weekday":2,"problem":"fever"}'
```

2) POST /book

Request JSON (example):

```json
{
  "hospital": "Manipal",
  "slot": "2025-11-22 14:00",
  "name": "Alice Example",
  "phone": "9876543210",
  "fee_paid": 199.0
}
```

Response JSON (example):

```json
{
  "booking_id": "BK2025112214304592",
  "hospital": "Manipal",
  "slot": "2025-11-22 14:00",
  "token": "4821",
  "estimated_wait": 35
}
```

Example curl:

```bash
curl -X POST http://127.0.0.1:8000/book \
  -H "Content-Type: application/json" \
  -d '{"hospital":"Manipal","slot":"2025-11-22 14:00","name":"Alice","phone":"9999999999","fee_paid":199}'
```

Notes:
- The backend currently uses a heuristic predictor (`heuristic_predict` in `app.py`) and random token generation for bookings. It is intended as a demo, not production-ready.
- CORS is enabled to allow the static frontend to call the API when served locally.

---

## Frontend

- The frontend is a small set of static HTML files in `frontend/` (`index1.html`, `predict.html`, `booking.html`).
- The frontend expects the backend to serve these files at `/static/` and call `/predict` and `/book` on the same origin.

If you prefer to serve the frontend separately (e.g., from a webserver or GitHub Pages), update the API base URL in the frontend JS from `"/predict"` to your backend host like `"https://api.example.com/predict"`.

---

## Development & Testing

- To run a quick local smoke test (after starting uvicorn):

```bash
curl -s -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{"hospital":"Manipal"}' | jq
```

- Use the UI (`/ui`) to exercise predict → booking flows manually.

---

## Contributing

- Open an issue or submit a pull request. Keep changes small and focused.
- If adding models or datasets, do not commit real patient data — use only synthetic or anonymized data.

---

## License

MIT License — see the `LICENSE` file in the repository root if present.

---

If you'd like, I can also add a `backend/README.md` with the exact run commands for Windows and Linux, and add a small `Makefile` or PowerShell script to run the server locally. Let me know if you want that.
=======
Akatsuki is a hospital traffic prediction project: a small research/demo app that models and predicts hospital visit volumes.

## About This Repository

This project lives inside the Repogenesis healthcare track and focuses on predicting hospital traffic using sample datasets and simple ML models. It includes a backend service, sample dataset, and a minimal frontend.

## Project Structure

```
backend/        # API, training & model files
frontend/       # Minimal web UI
docs/           # Project-specific docs and notes
README.md       # This file
```

## Usage

- See `backend/README.md` or `backend/app.py` for running the API.
- Use `train_model.py` to retrain on provided `dataset.csv`.

## Notes

- Do not use real patient data — use only anonymized or synthetic data.
- This is an educational/demo project and not for clinical use.

>>>>>>> 98a81f3064f6142823ee5a48298966c9bf3c0ec4
