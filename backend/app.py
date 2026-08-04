"""
==============================================================================
AI Bone Fracture Detection — Flask Web Application Backend
==============================================================================
Senior AI Engineer Implementation incorporating:
- MobileNetV2 Trained Bone Fracture CNN Classifier
- Grad-CAM Keras 3 Heatmap Activation Engine
- SQLite Prediction History with CSV/PDF Exports
- ANN Healing Time Estimator Model
- Rehabilitation & Recovery Recommendations Engine
- Nearby Orthopedic Doctors Geolocation Service
==============================================================================
"""

import os
import sys
import time
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory

# Suppress verbose C++ TensorFlow log messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Base Root Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add model and service paths to sys.path for clean modular imports
sys.path.extend([
    os.path.join(BASE_DIR, 'backend', 'routes'),
    os.path.join(BASE_DIR, 'backend', 'services'),
    os.path.join(BASE_DIR, 'models', 'cnn'),
    os.path.join(BASE_DIR, 'models', 'ann'),
    os.path.join(BASE_DIR, 'models', 'ml'),
])

# Imports from modular packages
from history import history_bp, save_prediction, init_db
from gradcam import generate_gradcam_heatmap
from healing_model import load_healing_model, predict_healing_time_ann
from rehabilitation import get_rehabilitation_plan
from doctors_data import get_nearby_doctors

# Folder Paths
STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend', 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'frontend', 'templates')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'uploads')
SAVED_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'cnn', 'best_model.keras')

# Initialize Flask App
app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)

# Register Blueprints
app.register_blueprint(history_bp)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize Database
init_db()

# Load Models
print(f"Loading trained CNN model from {SAVED_MODEL_PATH}...")
cnn_model = tf.keras.models.load_model(SAVED_MODEL_PATH)
print("CNN Model loaded successfully!")

healing_ann_model = load_healing_model()


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess image for CNN model."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def compute_severity(confidence, prediction):
    """Compute severity level based on prediction and confidence score."""
    if prediction == 'Not Fractured':
        return 'N/A'

    if confidence < 70.0:
        return 'Low'
    elif confidence < 85.0:
        return 'Moderate'
    elif confidence < 95.0:
        return 'High'
    else:
        return 'Critical'


def compute_suggestion(severity, prediction):
    """Generate clinical AI suggestion based on diagnosis."""
    if prediction == 'Not Fractured':
        return 'No fracture detected. Normal bone structure observed. Follow up if pain persists.'

    suggestions = {
        'Low': 'Mild/Hairline fracture suspected. Rest, ice, and consult an orthopedic specialist for X-ray confirmation.',
        'Moderate': 'Moderate fracture detected. Orthopedic consultation recommended within 24-48 hours. Immobilize the affected area.',
        'High': 'Significant fracture detected. Prompt orthopedic consultation strongly recommended. Avoid putting weight on the affected area.',
        'Critical': 'Severe fracture detected. Immediate emergency orthopedic consultation required. Seek medical attention immediately.'
    }
    return suggestions.get(severity, suggestions['Moderate'])


def compute_emergency_level(severity, prediction):
    """Compute emergency level from severity."""
    if prediction == 'Not Fractured':
        return 'None'

    emergency_map = {
        'Low': 'Low',
        'Moderate': 'Medium',
        'High': 'High',
        'Critical': 'High'
    }
    return emergency_map.get(severity, 'Medium')


# ==============================================================================
# FLASK ROUTES
# ==============================================================================
@app.route("/")
def landing():
    """Render the Landing Page."""
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'landing'), 'index.html')


@app.route("/login")
def login_page():
    """Render the Login & Auth Page."""
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'auth'), 'login.html')


@app.route("/dashboard")
def dashboard_page():
    """Render the Main Dashboard Application."""
    return render_template("index.html")


@app.route("/landing/<path:filename>")
def serve_landing_assets(filename):
    """Serve static assets for Landing Page."""
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'landing'), filename)


@app.route("/auth/<path:filename>")
def serve_auth_assets(filename):
    """Serve static assets for Auth Page."""
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'auth'), filename)


@app.route("/static/<path:filename>")
def serve_static_assets(filename):
    """Serve static assets for Dashboard and common elements."""
    # Check direct match in frontend/static
    direct = os.path.join(BASE_DIR, 'frontend', 'static', filename)
    if os.path.isfile(direct):
        return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'static'), filename)

    # Check subfolders: images, css, js
    for sub in ['images', 'css', 'js']:
        candidate = os.path.join(BASE_DIR, 'frontend', 'static', sub, filename)
        if os.path.isfile(candidate):
            return send_from_directory(os.path.dirname(candidate), os.path.basename(candidate))

    # Check legacy root static folder
    legacy = os.path.join(BASE_DIR, 'static', filename)
    if os.path.isfile(legacy):
        return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'static'), filename)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded X-ray images and generated Grad-CAM heatmaps."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Primary Prediction Endpoint:
    Accepts X-ray image file + patient_name via POST, runs CNN inference,
    generates Grad-CAM heatmap, calculates severity & emergency level,
    saves record to SQLite history DB, and returns JSON payload.
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No image file provided."}), 400

    file = request.files["file"]
    patient_name = request.form.get("patient_name", "Unknown").strip() or "Unknown"
    user_id = request.headers.get("X-User-ID") or request.form.get("user_id", "")

    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file."}), 400

    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "Invalid file type. Please upload a valid image file (PNG, JPG, JPEG, BMP, WEBP)."}), 400

    try:
        start_time = time.time()

        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}_{file.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

        input_tensor = preprocess_image(image_path)

        raw_pred = cnn_model.predict(input_tensor)[0]

        if len(raw_pred) == 1:
            # Keras class_indices: {'fractured': 0, 'not fractured': 1}
            # Output value raw_pred[0] is probability of class 1 ('not fractured')
            normal_prob = float(raw_pred[0])
            fracture_prob = 1.0 - normal_prob
        else:
            fracture_prob = float(raw_pred[0])
            normal_prob = float(raw_pred[1])

        if fracture_prob > 0.5:
            prediction = "Fractured"
            confidence = round(fracture_prob * 100, 2)
        else:
            prediction = "Not Fractured"
            confidence = round(normal_prob * 100, 2)

        inference_time = round(time.time() - start_time, 3)
        severity = compute_severity(confidence, prediction)
        suggestion = compute_suggestion(severity, prediction)
        emergency_level = compute_emergency_level(severity, prediction)

        heatmap_filename = f"heatmap_{timestamp}.png"
        heatmap_path = os.path.join(app.config['UPLOAD_FOLDER'], heatmap_filename)
        heatmap_url = ""

        try:
            generate_gradcam_heatmap(cnn_model, image_path, heatmap_path)
            heatmap_url = f"/uploads/{heatmap_filename}"
        except Exception as grad_err:
            print(f"Grad-CAM Warning: {grad_err}")
            heatmap_url = f"/uploads/{filename}"

        image_url = f"/uploads/{filename}"

        record_data = {
            'user_id': user_id,
            'patient_name': patient_name,
            'bone_type': 'Bone X-ray',
            'prediction': prediction,
            'confidence': confidence,
            'severity': severity,
            'emergency_level': emergency_level,
            'inference_time': inference_time,
            'image_path': image_url,
            'heatmap_path': heatmap_url
        }
        save_prediction(record_data)

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "confidence": confidence,
            "severity": severity,
            "emergency_level": emergency_level,
            "suggestion": suggestion,
            "inference_time": inference_time,
            "image_url": image_url,
            "heatmap_url": heatmap_url
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Inference failed: {str(e)}"}), 500


@app.route("/api/healing-prediction", methods=["POST"])
def healing_prediction():
    """API: Predict bone healing time using ANN regression model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided."}), 400

        age = data.get('age', 30)
        fracture_type = data.get('fracture_type', 'Transverse')
        bone = data.get('bone', 'Wrist')
        smoking = data.get('smoking', False)
        diabetes = data.get('diabetes', False)
        severity = data.get('severity', 'Moderate')

        result = predict_healing_time_ann(
            healing_ann_model,
            age=age,
            fracture_type=fracture_type,
            bone=bone,
            smoking=smoking,
            diabetes=diabetes,
            severity=severity
        )

        return jsonify({
            "status": "success",
            "estimated_weeks": result['estimated_weeks'],
            "range_text": result['range_text'],
            "confidence": result['confidence']
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rehab-recommendation", methods=["POST"])
def rehab_recommendation():
    """API: Get rehabilitation recommendations based on diagnosis."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided."}), 400

        plan = get_rehabilitation_plan(
            prediction=data.get('prediction', 'Not Fractured'),
            severity=data.get('severity', 'N/A'),
            confidence=float(data.get('confidence', 0))
        )

        return jsonify({"status": "success", "plan": plan})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==============================================================================
# NEARBY DOCTORS API
# ==============================================================================
@app.route("/api/nearby-doctors")
def nearby_doctors():
    """API: Get nearby orthopedic doctors based on user's geolocation & filters."""
    try:
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        city = request.args.get('city', '').strip()
        search = request.args.get('search', '').strip()

        # Default fallback to Kolhapur / Ichalkaranji coordinates if not set
        if lat == 0 and lng == 0:
            lat = 16.7305
            lng = 74.4724

        doctors = get_nearby_doctors(user_lat=lat, user_lng=lng, limit=12, city_filter=city, search_query=search)
        return jsonify({"status": "success", "doctors": doctors})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
