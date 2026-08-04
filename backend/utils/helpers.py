"""
==============================================================================
Utility & Helper Functions
==============================================================================
Provides sanitization, image preprocessing, severity computation, clinical
suggestions, and emergency level assessment.
==============================================================================
"""

import os
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename
from backend.config.settings import ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if uploaded file extension is permitted."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal or unsafe characters."""
    clean_name = secure_filename(filename)
    return clean_name if clean_name else "upload_file.png"


def preprocess_image(image_path, target_size=(224, 224)):
    """Preprocess X-ray image array for CNN model input."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def compute_severity(confidence, prediction):
    """Compute severity level based on diagnosis prediction and confidence score."""
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
    """Generate clinical AI recommendation based on fracture severity."""
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
    """Determine emergency level for triaging."""
    if prediction == 'Not Fractured':
        return 'None'

    emergency_map = {
        'Low': 'Low',
        'Moderate': 'Medium',
        'High': 'High',
        'Critical': 'High'
    }
    return emergency_map.get(severity, 'Medium')
