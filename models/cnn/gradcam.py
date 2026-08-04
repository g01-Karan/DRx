"""
==============================================================================
Grad-CAM Heatmap Generator (Keras 3 & Keras 2 Compatible)
==============================================================================
Generates Gradient-weighted Class Activation Maps (Grad-CAM) to visualize
which regions of the X-ray image the CNN model focuses on during prediction.
==============================================================================
"""

import os
import time
import numpy as np
import tensorflow as tf
import cv2


def generate_gradcam(model, img_array, original_img_path, save_dir='uploads'):
    """
    Generate a Grad-CAM heatmap overlay on the original X-ray image.

    Args:
        model: Loaded Keras CNN model
        img_array: Preprocessed image array (1, 224, 224, 3), normalized [0, 1]
        original_img_path: Path to the original uploaded image
        save_dir: Directory to save the heatmap image

    Returns:
        str: Filename of the saved heatmap image
    """
    try:
        # Find the index of the last Conv2D layer in model.layers
        last_conv_idx = -1
        for i, layer in enumerate(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv_idx = i

        if last_conv_idx == -1:
            print("Warning: No Conv2D layer found in model.")
            return None

        # Split layers into conv pipeline and remaining classification pipeline
        conv_pipeline = model.layers[:last_conv_idx + 1]
        classifier_pipeline = model.layers[last_conv_idx + 1:]

        # Record operations for gradient computation
        with tf.GradientTape() as tape:
            x = img_array
            for layer in conv_pipeline:
                x = layer(x)
            conv_outputs = x
            tape.watch(conv_outputs)

            y = conv_outputs
            for layer in classifier_pipeline:
                y = layer(y)
            preds = y
            top_class_channel = preds[:, 0]

        # Calculate gradients of top predicted class w.r.t. feature map
        grads = tape.gradient(top_class_channel, conv_outputs)
        if grads is None:
            return None

        # Mean intensity of the gradient over feature map channels
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Weighted combination of feature maps
        conv_outputs_val = conv_outputs[0]
        heatmap = conv_outputs_val @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # Apply ReLU activation and normalize to [0, 1]
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
        heatmap = heatmap.numpy()

        # Load original image for visualization
        original_img = cv2.imread(original_img_path)
        if original_img is None:
            print(f"Warning: Could not read image at {original_img_path}")
            return None

        img_h, img_w = original_img.shape[:2]

        # Resize heatmap to match original image dimensions
        heatmap_resized = cv2.resize(heatmap, (img_w, img_h))

        # Apply JET colormap
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET
        )

        # Create blended overlay with 60% original image + 40% heatmap
        overlay = cv2.addWeighted(original_img, 0.6, heatmap_colored, 0.4, 0)

        # Save heatmap image file
        os.makedirs(save_dir, exist_ok=True)
        timestamp = int(time.time() * 1000)
        heatmap_filename = f"heatmap_{timestamp}.png"
        heatmap_path = os.path.join(save_dir, heatmap_filename)
        cv2.imwrite(heatmap_path, overlay)

        return heatmap_filename

    except Exception as e:
        import traceback
        print(f"Grad-CAM generation error: {e}")
        traceback.print_exc()
        return None


def generate_gradcam_heatmap(model, image_path, target_output_path):
    """
    Wrapper function for saving heatmap to a specific target output path.
    """
    img = tf.keras.utils.load_img(image_path, target_size=(224, 224))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    save_dir = os.path.dirname(target_output_path) or 'uploads'
    filename = generate_gradcam(model, img_array, image_path, save_dir=save_dir)
    if filename:
        generated_path = os.path.join(save_dir, filename)
        if generated_path != target_output_path and os.path.exists(generated_path):
            os.replace(generated_path, target_output_path)
        return target_output_path
    return None
