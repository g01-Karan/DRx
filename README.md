# 🩺 Dr X — AI-Powered Orthopaedic Assistant

[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth_%26_DB-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

An enterprise-grade, full-stack AI medical web application designed for instant bone fracture diagnosis from X-ray scans, visual interpretability with Grad-CAM heatmaps, ANN-driven healing time estimations, custom rehabilitation plans, and nearby orthopedic specialist radar.

---

## 🌟 Key Features

- **🔬 Deep Learning Fracture Detection (CNN)**
  - MobileNetV2 architecture trained on thousands of bone X-ray images.
  - Detects fractures with high sensitivity and provides real-time confidence scores.

- **🎯 Grad-CAM Visual Heatmaps**
  - Gradient-weighted Class Activation Mapping highlights exact anomaly locations directly on the X-ray for full clinical transparency.

- **⏱️ ANN Bone Healing Time Estimator**
  - Artificial Neural Network regression model predicting recovery duration based on patient age, bone type, fracture geometry, smoking, and diabetes parameters.

- **🧘 Automated Rehabilitation & Exercise Plans**
  - Phase-by-phase recovery schedules (Phases 1–4) tailored to severity, complete with exercise descriptions, precautions, and follow-up timelines.

- **📍 Nearby Orthopedic Specialist Radar**
  - Haversine geolocation-based search for nearest orthopedic trauma centers, rating filters, and direct contact details.

- **🔒 Supabase Authentication & Isolated Data Storage**
  - Secure user authentication with isolated SQLite prediction history, supporting CSV & PDF report exports per user account.

---

## 📁 Modular Project Structure

```
AI-Orthopaedic-Assistant/
├── frontend/
│   ├── landing/          # Hero Landing Page (index.html, landing.css, landing.js)
│   ├── auth/             # Live Supabase Auth Page (login.html, login.css, login.js)
│   ├── templates/        # Main Dashboard & History Templates (index.html, history.html)
│   └── static/
│       ├── css/          # Application Stylesheets (style.css)
│       ├── js/           # Frontend Client Logic (script.js)
│       └── images/       # Medical Badges & Hero Preview Assets (logo.png, hero-xray.png)
│
├── backend/
│   ├── app.py            # Flask API & Web Controller
│   ├── routes/           # Database Blueprints & History APIs (history.py)
│   ├── services/         # Geolocation Trauma Center Finder (doctors_data.py)
│   └── uploads/          # Image & Heatmap Upload Storage
│
├── models/
│   ├── cnn/              # Fracture Classifier (best_model.keras, predict.py, gradcam.py)
│   ├── ann/              # Bone Healing Model (healing_ann.keras, healing_scaler.json, healing_model.py)
│   └── ml/               # Rehabilitation Engine (rehabilitation.py)
│
├── database/             # SQLite History Database (predictions.db)
├── app.py                # Root Entry Point Launcher
└── requirements.txt      # Python Dependencies
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11+
- Virtual Environment (`venv` recommended)

### 3. Run Application

```bash
# Launch Flask Application Server
python app.py
```

The application will start on **`http://localhost:5050/`**.

---

## 🌐 Application Navigation & Routes

| Path | Description |
| :--- | :--- |
| **`http://localhost:5050/`** | Hero Landing Page |
| **`http://localhost:5050/login`** | Sign In / Create Account |
| **`http://localhost:5050/dashboard`** | AI Diagnostic Dashboard & Bone Analysis |
| **`http://localhost:5050/history`** | Patient History Records & PDF/CSV Exports |

---

## 🔌 API Endpoints Summary

- `POST /predict`: Upload bone X-ray image for CNN classification & Grad-CAM heatmap generation.
- `POST /api/healing-prediction`: ANN prediction of recovery weeks based on health factors.
- `POST /api/rehab-recommendation`: Phase-by-phase rehabilitation exercise generator.
- `GET /api/nearby-doctors`: Location-sorted orthopedic hospitals & specialists.
- `GET /api/history`: User-isolated prediction history list with pagination.
- `GET /api/history/export/csv` & `/pdf`: Export patient reports.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+), GSAP (GreenSock Animations), FontAwesome.
- **Backend**: Python 3.11, Flask, SQLite3, ReportLab (PDF generation).
- **AI / Machine Learning**: TensorFlow, Keras 3, MobileNetV2, OpenCV, NumPy, Scikit-Learn.
- **Authentication**: Supabase Auth SDK.

---

## ⚠️ Medical Disclaimer

*Dr X is an AI decision-support tool designed for educational and preliminary screening purposes. It is **not** a substitute for professional medical diagnosis. Always consult a qualified orthopedic physician or radiologist for clinical evaluation.*

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more details.
