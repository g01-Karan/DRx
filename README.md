# 🦴 Dr X — AI Orthopaedic Assistant (Bone Fracture Detection)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)](https://flask.palletsprojects.org/)
[![TensorFlow](https://img.shields.io/badge/AI--ML-TensorFlow-orange.svg)](https://www.tensorflow.org/)
[![Deploy](https://img.shields.io/badge/Vercel-Ready-black.svg)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, production-grade AI Orthopaedic Assistant for automated **Bone Fracture Detection**, **Grad-CAM Heatmap Visualization**, **ANN Healing Time Estimation**, **ML Rehabilitation Recommendations**, **Nearby Orthopedic Doctor Geolocation**, and **Prediction History Reports**.

---

## 🚀 Key Features

- 🔬 **AI Bone Fracture Detection**: High-accuracy CNN classifier (MobileNetV2 architecture) trained on X-ray imaging.
- 🔥 **Grad-CAM Explainability Heatmaps**: Visualizes activation regions on X-rays showing precisely where fractures are detected.
- ⏱️ **ANN Healing Time Predictor**: Artificial Neural Network predicting recovery timelines in weeks based on age, bone type, fracture classification, and comorbidities.
- 🧘 **Rehabilitation Guidance Engine**: Knowledge-based recovery plans including stage-by-stage exercise protocols, precautions, and follow-up timelines.
- 🏥 **Nearby Orthopedic Locator**: Geolocation engine displaying top rated orthopedic specialists and trauma centers with direct turn-by-turn Google Maps navigation links.
- 🔐 **Supabase Authentication**: Secure user authentication and session management.
- 📊 **Prediction History & Export**: Complete database logging with filter, search, pagination, and one-click PDF/CSV medical report export.
- 🌐 **Vercel Serverless Ready**: Optimized WSGI entry point and standard routing for deployment on Vercel.

---

## 📁 Repository Structure

```
Bone-Fracture-AI/
├── api/
│   └── index.py             # Vercel Serverless Function entrypoint
├── backend/
│   ├── app.py               # Main Flask application & routes
│   ├── config/              # Centralized app configuration & environment settings
│   ├── controllers/         # Controller logic placeholders
│   ├── middleware/          # Security headers & CORS middleware
│   ├── routes/              # Blueprint routes (history, analytics)
│   ├── services/            # Geolocation hospital lookup engine
│   ├── utils/               # Sanitization & image preprocessing utilities
│   └── uploads/             # Runtime image upload & Grad-CAM output directory
├── frontend/
│   ├── auth/                # Login & Supabase authentication UI
│   ├── landing/             # Dynamic landing page with GSAP animations
│   ├── static/              # Dashboard CSS, JavaScript, and branding assets
│   └── templates/           # Jinja2 Flask templates (index.html, history.html)
├── models/
│   ├── ann/                 # ANN healing time prediction model & scaler
│   ├── cnn/                 # MobileNetV2 fracture classifier & Grad-CAM engine
│   ├── ml/                  # Knowledge-based rehabilitation engine
│   ├── preprocessing/       # Data preprocessing scripts
│   ├── inference/           # Standalone CLI prediction scripts
│   └── weights/             # Saved model checkpoints
├── datasets/                # Sample datasets & training images
├── docs/                    # Project documentation
├── scripts/                 # Utility & automation scripts
├── tests/                   # Test suite directory
├── .env.example             # Environment variables template
├── .gitignore               # Git exclusion rules
├── app.py                   # Root application launcher
├── vercel.json              # Vercel deployment configuration
├── requirements.txt         # Production Python dependencies
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, GSAP Animations, Chart.js, FontAwesome
- **Backend Framework**: Python 3.11+, Flask Web Framework, Werkzeug
- **Machine Learning & Vision**: TensorFlow / Keras 3, OpenCV (Headless), NumPy, Pillow, Scikit-Learn
- **Database & Auth**: SQLite 3, Supabase JS Authentication
- **Reporting**: ReportLab PDF Engine, CSV Streaming
- **Deployment**: Vercel Serverless Functions

---

## ⚙️ Local Setup & Installation

### 1. Prerequisites
- Python 3.11 or higher installed on your system.

### 2. Clone Repository
```bash
git clone https://github.com/your-username/Bone-Fracture-AI.git
cd Bone-Fracture-AI
```

### 3. Create & Activate Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables
Create a `.env` file in the root directory by copying `.env.example`:
```bash
cp .env.example .env
```

---

## 💻 Running the Application

### Start Flask Server
```bash
python app.py
```
Open your browser and navigate to:
- **Landing Page**: `http://localhost:5050/`
- **Login Page**: `http://localhost:5050/login`
- **Dashboard Application**: `http://localhost:5050/dashboard`

---

## 🤖 Running Machine Learning Inference via CLI

### Predict Image Classification
To test image prediction directly from the command line:
```bash
python models/cnn/predict.py
```

### Train Healing Time ANN Model
To retrain the healing time ANN model:
```bash
python models/ann/train_healing_model.py
```

---

## 🌐 Deployment to Vercel

1. Install the [Vercel CLI](https://vercel.com/cli):
   ```bash
   npm i -g vercel
   ```
2. Deploy directly from your terminal:
   ```bash
   vercel
   ```
3. Or link your GitHub repository to your [Vercel Dashboard](https://vercel.com/dashboard) for automatic deployments on push.

---

## 🛡️ Security & Privacy

- All user file uploads are sanitized using `secure_filename`.
- CORS and security response headers are strictly enforced.
- Database queries use parameterized bindings to protect against SQL injection.
- Secret keys and API credentials are kept out of source code via `.env`.

---

## 📜 License

This project is open-source and licensed under the [MIT License](LICENSE).
