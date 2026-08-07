"""
==============================================================================
Binary Bone Fracture Detection - Image Prediction Script
==============================================================================
Loads the trained CNN model (best_model.pt or best_model.keras),
takes an input X-ray image path, processes it, and predicts
whether the bone is Fractured or Not Fractured with confidence.
==============================================================================
"""

import os
import sys
import numpy as np
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PYTORCH_MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn", "best_model.pt")
KERAS_MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn", "best_model.keras")

def predict_single_image(image_path):
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' does not exist.")
        return

    # 1. Try PyTorch Model
    if os.path.exists(PYTORCH_MODEL_PATH):
        try:
            import torch
            sys.path.append(BASE_DIR)
            from models.cnn.train_pytorch_model import get_mobilenet_model, DEVICE
            from backend.utils.helpers import preprocess_image

            model = get_mobilenet_model().to(DEVICE)
            model.load_state_dict(torch.load(PYTORCH_MODEL_PATH, map_location=DEVICE))
            model.eval()

            img_tensor = preprocess_image(image_path)
            input_tensor = torch.tensor(img_tensor, dtype=torch.float32).to(DEVICE)

            with torch.no_grad():
                output_logit = model(input_tensor).squeeze().item()
                normal_prob = float(torch.sigmoid(torch.tensor(output_logit)).item())

            if normal_prob >= 0.5:
                confidence = normal_prob * 100.0
                print("\nPrediction: Not Fractured")
                print(f"Confidence: {confidence:.2f}%")
            else:
                confidence = (1.0 - normal_prob) * 100.0
                print("\nPrediction: Fractured Bone")
                print(f"Confidence: {confidence:.2f}%")
            return
        except Exception as err:
            print(f"PyTorch prediction error: {err}")

    # 2. Try Keras Model
    if os.path.exists(KERAS_MODEL_PATH):
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(KERAS_MODEL_PATH)
            img = Image.open(image_path).convert("RGB").resize((224, 224))
            arr = np.array(img, dtype=np.float32) / 255.0
            input_tensor = np.expand_dims(arr, axis=0)

            prediction = model.predict(input_tensor, verbose=0)
            output_value = float(prediction[0][0])

            if output_value < 0.5:
                confidence = (1.0 - output_value) * 100.0
                print("\nPrediction: Fractured Bone")
                print(f"Confidence: {confidence:.2f}%")
            else:
                confidence = output_value * 100.0
                print("\nPrediction: Not Fractured")
                print(f"Confidence: {confidence:.2f}%")
            return
        except Exception as err:
            print(f"Keras prediction error: {err}")

    print("Error: No trained model file found. Please run 'python models/cnn/train_pytorch_model.py' first.")

def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter Image Path: ").strip().strip('"').strip("'")
    predict_single_image(image_path)

if __name__ == "__main__":
    main()
