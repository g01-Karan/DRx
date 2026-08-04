"""
==============================================================================
Healing Time Prediction — ANN Model Training Script
==============================================================================
Trains a simple Artificial Neural Network (ANN) on synthetic medically-sourced
data to predict estimated bone fracture healing time.
==============================================================================
"""

import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import json

# Output paths
MODEL_DIR = 'saved_model'
MODEL_PATH = os.path.join(MODEL_DIR, 'healing_ann.keras')
SCALER_PATH = os.path.join(MODEL_DIR, 'healing_scaler.json')


# ==============================================================================
# 1. GENERATE SYNTHETIC TRAINING DATA
# ==============================================================================
def generate_training_data(n_samples=3000):
    """
    Generate synthetic training data based on medically-sourced healing time ranges.

    Features (6 inputs):
        0: Age (18-85)
        1: Fracture Type (0=Hairline, 1=Transverse, 2=Oblique, 3=Comminuted, 4=Spiral)
        2: Bone (0=Finger, 1=Wrist, 2=Forearm, 3=Ankle, 4=Tibia, 5=Femur, 6=Hip)
        3: Smoking Status (0=No, 1=Yes)
        4: Diabetes (0=No, 1=Yes)
        5: Severity (0=Low, 1=Moderate, 2=High, 3=Critical)

    Output:
        Healing time in weeks (continuous)
    """
    np.random.seed(42)

    # Base healing times by bone type (in weeks)
    bone_base_weeks = {
        0: 3,    # Finger
        1: 6,    # Wrist
        2: 8,    # Forearm
        3: 6,    # Ankle
        4: 12,   # Tibia
        5: 14,   # Femur
        6: 16    # Hip
    }

    # Fracture type multiplier
    fracture_multiplier = {
        0: 0.7,   # Hairline — heals faster
        1: 1.0,   # Transverse — baseline
        2: 1.1,   # Oblique
        3: 1.4,   # Comminuted — complex, slower
        4: 1.2    # Spiral
    }

    # Severity multiplier
    severity_multiplier = {
        0: 0.8,   # Low
        1: 1.0,   # Moderate
        2: 1.3,   # High
        3: 1.6    # Critical
    }

    X = []
    y = []

    for _ in range(n_samples):
        age = np.random.randint(18, 86)
        fracture_type = np.random.randint(0, 5)
        bone = np.random.randint(0, 7)
        smoking = np.random.choice([0, 1], p=[0.75, 0.25])
        diabetes = np.random.choice([0, 1], p=[0.85, 0.15])
        severity = np.random.randint(0, 4)

        # Calculate healing time
        base = bone_base_weeks[bone]
        healing_weeks = base * fracture_multiplier[fracture_type] * severity_multiplier[severity]

        # Age factor: older patients heal slower
        if age > 50:
            healing_weeks *= 1.0 + (age - 50) * 0.01
        elif age < 25:
            healing_weeks *= 0.85  # Younger patients heal faster

        # Smoking delays healing by ~15-30%
        if smoking:
            healing_weeks *= 1.0 + np.random.uniform(0.15, 0.30)

        # Diabetes delays healing by ~10-25%
        if diabetes:
            healing_weeks *= 1.0 + np.random.uniform(0.10, 0.25)

        # Add some natural variance
        healing_weeks += np.random.normal(0, healing_weeks * 0.08)
        healing_weeks = max(2, healing_weeks)  # Minimum 2 weeks

        X.append([age, fracture_type, bone, smoking, diabetes, severity])
        y.append(round(healing_weeks, 1))

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


# ==============================================================================
# 2. BUILD AND TRAIN ANN
# ==============================================================================
def train_model():
    """Build, train, and save the ANN healing time prediction model."""
    print("Generating synthetic training data...")
    X, y = generate_training_data(3000)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler parameters
    scaler_params = {
        'mean': scaler.mean_.tolist(),
        'scale': scaler.scale_.tolist()
    }

    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Build ANN model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(6,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear')  # Regression output
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )

    model.summary()

    # Train
    print("\nTraining Healing Time ANN...")
    history = model.fit(
        X_train_scaled, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.15,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=15, restore_best_weights=True
            )
        ],
        verbose=1
    )

    # Evaluate
    test_loss, test_mae = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"\nTest MAE: {test_mae:.2f} weeks")
    print(f"Test MSE: {test_loss:.4f}")

    # Save model and scaler
    os.makedirs(MODEL_DIR, exist_ok=True)
    model.save(MODEL_PATH)
    print(f"Model saved to: {MODEL_PATH}")

    with open(SCALER_PATH, 'w') as f:
        json.dump(scaler_params, f)
    print(f"Scaler saved to: {SCALER_PATH}")

    # Test predictions
    print("\nSample Predictions:")
    test_cases = [
        [25, 0, 1, 0, 0, 0],   # Young, hairline, wrist, no risk factors
        [45, 1, 3, 0, 0, 1],   # Middle-aged, transverse, ankle, moderate
        [65, 3, 5, 1, 1, 3],   # Elderly, comminuted, femur, smoker+diabetic, critical
    ]
    test_labels = [
        "25yo, hairline wrist fracture, low severity",
        "45yo, transverse ankle fracture, moderate severity",
        "65yo, comminuted femur fracture, critical, smoker+diabetic"
    ]

    for case, label in zip(test_cases, test_labels):
        case_scaled = scaler.transform(np.array([case], dtype=np.float32))
        pred = model.predict(case_scaled, verbose=0)[0][0]
        print(f"  {label}: ~{pred:.1f} weeks")

    print("\nDone!")


if __name__ == '__main__':
    train_model()
