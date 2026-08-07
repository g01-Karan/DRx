"""
==============================================================================
Application Configuration & Environment Settings
==============================================================================
Centralized configuration management for Bone Fracture AI Assistant.
==============================================================================
"""

import os
import tempfile

# Base Root Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if environment is Vercel or Read-Only Serverless
IS_SERVERLESS = os.environ.get('VERCEL') is not None or not os.access(BASE_DIR, os.W_OK)

# App Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'bone-fracture-ai-secret-key-2026')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
PORT = int(os.environ.get('PORT', 5050))

# Folder Paths (Fallback to /tmp for serverless read-only filesystems)
STATIC_FOLDER = os.path.join(BASE_DIR, 'frontend', 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'frontend', 'templates')
LANDING_FOLDER = os.path.join(BASE_DIR, 'frontend', 'landing')
AUTH_FOLDER = os.path.join(BASE_DIR, 'frontend', 'auth')

if IS_SERVERLESS:
    TMP_DIR = tempfile.gettempdir()
    UPLOAD_FOLDER = os.path.join(TMP_DIR, 'uploads')
    DB_DIR = os.path.join(TMP_DIR, 'database')
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'uploads')
    DB_DIR = os.path.join(BASE_DIR, 'database')

DB_PATH = os.path.join(DB_DIR, 'predictions.db')

# Model Paths
SAVED_CNN_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'cnn', 'best_model.keras')
SAVED_PYTORCH_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'cnn', 'best_model.pt')
SAVED_ANN_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'ann', 'healing_ann.keras')
SAVED_ANN_SCALER_PATH = os.path.join(BASE_DIR, 'models', 'ann', 'healing_scaler.json')

# Upload Constraints
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
