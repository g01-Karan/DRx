"""
==============================================================================
User Authentication — SQLite Database & Flask Blueprint
==============================================================================
Provides secure user signup, password hashing, credential verification,
and login endpoints for Dr X AI Orthopaedic Assistant.
==============================================================================
"""

import os
import sqlite3
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# Database path configuration
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IS_SERVERLESS = os.environ.get('VERCEL') is not None or not os.access(ROOT_DIR, os.W_OK)

if IS_SERVERLESS:
    DB_DIR = os.path.join(tempfile.gettempdir(), 'database')
else:
    DB_DIR = os.path.join(ROOT_DIR, 'database')

DB_PATH = os.path.join(DB_DIR, 'predictions.db')


def init_users_db():
    """Ensure the users table exists in the database."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as err:
        print(f"Users DB init warning: {err}")


def get_db():
    """Get a database connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user account with hashed password."""
    init_users_db()
    data = request.get_json(force=True, silent=True) or request.form.to_dict()
    
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    name = (data.get("name") or "").strip() or email.split("@")[0]

    if not email or "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "Please enter a valid email address."}), 400

    if not password or len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long."}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return jsonify({"status": "error", "message": "An account with this email address already exists. Please sign in."}), 409

    user_id = f"usr_{int(datetime.now().timestamp() * 1000)}"
    password_hash = generate_password_hash(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO users (id, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, email, password_hash, created_at)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Account created successfully!",
        "user": {
            "id": user_id,
            "name": name,
            "email": email
        }
    }), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate existing user credentials."""
    init_users_db()
    data = request.get_json(force=True, silent=True) or request.form.to_dict()

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"status": "error", "message": "No account found with this email address. Please create an account first."}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Incorrect password. Please try again."}), 401

    return jsonify({
        "status": "success",
        "message": "Successfully authenticated!",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200
