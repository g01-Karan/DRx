"""
==============================================================================
Healing Time Prediction — ANN Inference Module
==============================================================================
Loads the trained ANN model and predicts estimated healing time based on
patient parameters.
==============================================================================
"""

import os
import json
import numpy as np
import tensorflow as tf


# Paths
ANN_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ANN_DIR, 'healing_ann.keras')
SCALER_PATH = os.path.join(ANN_DIR, 'healing_scaler.json')

# Global model reference (loaded once)
_healing_model = None
_scaler_params = None


# Encoding maps for human-readable inputs
FRACTURE_TYPE_MAP = {
    'Hairline': 0,
    'Transverse': 1,
    'Oblique': 2,
    'Comminuted': 3,
    'Spiral': 4
}

BONE_MAP = {
    'Finger': 0,
    'Wrist': 1,
    'Forearm': 2,
    'Ankle': 3,
    'Tibia': 4,
    'Femur': 5,
    'Hip': 6
}

SEVERITY_MAP = {
    'Low': 0,
    'Moderate': 1,
    'High': 2,
    'Critical': 3
}


def load_healing_model():
    """Load the trained ANN model and scaler parameters."""
    global _healing_model, _scaler_params

    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        print(f"Loading Healing ANN model from {MODEL_PATH}...")
        _healing_model = tf.keras.models.load_model(MODEL_PATH)

        with open(SCALER_PATH, 'r') as f:
            _scaler_params = json.load(f)

        print("Healing ANN model loaded successfully!")
        return _healing_model
    else:
        print(f"Warning: Healing ANN model not found at {MODEL_PATH}.")
        print("Run 'python train_healing_model.py' to train the model first.")
        return None


def predict_healing_time(age, fracture_type, bone, smoking, diabetes, severity):
    """
    Predict estimated healing time for a bone fracture.

    Args:
        age (int): Patient's age
        fracture_type (str): Type of fracture (e.g., 'Hairline', 'Transverse')
        bone (str): Affected bone (e.g., 'Wrist', 'Femur')
        smoking (bool): Whether patient smokes
        diabetes (bool): Whether patient has diabetes
        severity (str): Fracture severity (e.g., 'Low', 'High')

    Returns:
        dict: Prediction result with estimated weeks range and confidence
    """
    if _healing_model is None:
        return {
            'status': 'error',
            'message': 'Healing model not loaded. Please train the model first.'
        }

    try:
        # Encode categorical inputs
        fracture_code = FRACTURE_TYPE_MAP.get(fracture_type, 1)
        bone_code = BONE_MAP.get(bone, 1)
        severity_code = SEVERITY_MAP.get(severity, 1)
        smoking_code = 1 if smoking else 0
        diabetes_code = 1 if diabetes else 0

        # Prepare input
        features = np.array([[age, fracture_code, bone_code, smoking_code, diabetes_code, severity_code]],
                            dtype=np.float32)

        # Scale features using saved scaler parameters
        mean = np.array(_scaler_params['mean'])
        scale = np.array(_scaler_params['scale'])
        features_scaled = (features - mean) / scale

        # Predict
        prediction = _healing_model.predict(features_scaled, verbose=0)[0][0]
        predicted_weeks = max(2, round(float(prediction), 1))

        # Calculate range (±15% variance)
        min_weeks = max(2, round(predicted_weeks * 0.85))
        max_weeks = round(predicted_weeks * 1.15)

        # Confidence based on how typical the input is (simple heuristic)
        confidence = min(97, max(75, 95 - abs(age - 40) * 0.2 - severity_code * 3))

        return {
            'status': 'success',
            'estimated_weeks': predicted_weeks,
            'range_text': f"{min_weeks} - {max_weeks} weeks",
            'confidence': round(confidence, 1)
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f"Healing prediction error: {str(e)}"
        }


def predict_healing_time_ann(model, age, fracture_type, bone, smoking, diabetes, severity):
    """Wrapper function for predicting healing time."""
    return predict_healing_time(age, fracture_type, bone, smoking, diabetes, severity)
