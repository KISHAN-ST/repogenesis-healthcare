# 🚀 Akatsuki — Hospital Traffic Predictor
AI-powered system predicting hospital crowd levels & wait times.

Akatsuki is an ML-powered solution designed to help patients, hospitals, and emergency services predict real-time traffic, reduce wait time, and schedule visits efficiently. Built using FastAPI + Python + a lightweight HTML/CSS/JS frontend.

---

## 🎯 Problem We Are Solving
Hospitals often face:
- Unpredictable patient flow  
- Long waiting times  
- Poor resource allocation  
- No visibility for patients before arrival  

Akatsuki fixes this by predicting:
- Crowd level  
- Estimated wait time  
- Best hour to visit  
- Possible peak timings  

---

## 💡 Our Solution
Akatsuki combines:
- Historical data / dummy vitals  
- Machine learning forecasting  
- FastAPI inference backend  
- Simple, fast frontend  

Users get instant predictions with one click.

---

## ⭐ Core Features
### 🔮 AI-Based Crowd Prediction  
Forecasts hourly patient inflow + wait times.

### ⚡ FastAPI Prediction API  
Ultra-quick backend response.

### 🌐 Clean, Simple Frontend  
HTML/CSS/JS with easy interaction.

### 📊 Demo Booking Flow  
Shows how prediction integrates into real hospital systems.

### 🏥 Lightweight & Deployable  
Perfect for hackathons, demos, and integration testing.

---

## 🧱 Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python, Joblib, Uvicorn |
| ML | NumPy, Scikit-learn |
| Frontend | HTML, CSS, JS |
| Data | JSON dummy data |
| Deployment | Render / Railway / Deta (optional) |

---

## 🏗️ Project Structure
akatsuki/
│
├── backend/
│ ├── app.py
│ ├── train_model.py
│ ├── generate_data.py
│ ├── model.joblib
│ └── requirements.txt
│
├── frontend/
│ ├── index.html
│ ├── booking.html
│ ├── predict.html
│ └── script.js
│
├── starter/
│ └── dummy-data/
│
├── .gitignore
└── README.md

---

## 🚦 How to Run Locally

1️⃣ Install Backend Dependencies
```bash
cd akatsuki/backend
pip install -r requirements.txt

2️⃣ Run FastAPI Server
uvicorn app:app --reload

API runs at:
http://127.0.0.1:8000

3️⃣ Open Frontend
Open:
akatsuki/frontend/index.html
in your browser.

📈 Future Scope

Real hospital data integration

Mobile app for alerts & bookings

Advanced ML (LSTM, Prophet, Neural models)

Multi-hospital comparison dashboard

Real-time OPD counter integration

👥 Team

Kishan S T
Soumya Ranjan Behera
Vidhika Singh
Anubhav Gurung

📬 Contact

For collaboration or queries:
👉 GitHub: https://github.com/KISHAN-ST