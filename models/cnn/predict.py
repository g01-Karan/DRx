"""
==============================================================================
Binary Bone Fracture Detection - Image Prediction Script
==============================================================================
This script loads the trained best CNN model (saved_model/best_model.keras),
takes an input X-ray image path from the user, processes it, and predicts
whether the bone is Fractured or Not Fractured along with confidence percentage.
==============================================================================
"""

import os
import numpy as np
import tensorflow as tf
from PIL import ImageFile

# Allow PIL to load truncated/damaged images
ImageFile.LOAD_TRUNCATED_IMAGES = True


# Path to saved model checkpoint
MODEL_PATH = os.path.join("saved_model", "best_model.keras")

def main():
    # 1. Check if saved model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Trained model file not found at '{MODEL_PATH}'.")
        print("Please run 'python train_model.py' first to train and save the model.")
        return

    # 2. Load trained Keras model
    print("Loading trained model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!\n")

    # 3. Ask user for image path
    image_path = input("Enter Image Path: ").strip().strip('"').strip("'")

    # 4. Check if image file exists
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist. Please check the path and try again.")
        return

    try:
        # 5. Load and preprocess image
        # Load image and resize to 224x224 target size
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
        
        # Convert image to numpy array
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        
        # Normalize pixel values to range [0.0, 1.0] (matching training preprocessing)
        img_array = img_array / 255.0
        
        # Expand dimensions to add batch dimension (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)

        # 6. Predict image class
        prediction = model.predict(img_array, verbose=0)
        output_value = float(prediction[0][0])

        # 7. Display prediction and confidence
        # Keras class_indices: {'fractured': 0, 'not fractured': 1}
        if output_value < 0.5:
            confidence = (1.0 - output_value) * 100
            print("\nPrediction: Fractured Bone")
            print(f"Confidence: {confidence:.2f}%")
        else:
            confidence = output_value * 100
            print("\nPrediction: Not Fractured")
            print(f"Confidence: {confidence:.2f}%")


    except Exception as e:
        print(f"An error occurred while processing the image: {e}")

if __name__ == "__main__":
    main()
