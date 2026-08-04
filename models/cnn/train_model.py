"""
==============================================================================
Binary Bone Fracture Detection - CNN Model Training Script
==============================================================================
This script builds and trains a Convolutional Neural Network (CNN) from scratch
using TensorFlow/Keras to classify bone X-ray images into two classes:
- Fractured
- Not Fractured
==============================================================================
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import ImageFile
from sklearn.metrics import classification_report, confusion_matrix

# Allow PIL to load truncated/damaged images in dataset
ImageFile.LOAD_TRUNCATED_IMAGES = True


# ==============================================================================
# 1. PATHS & HYPERPARAMETERS CONFIGURATION
# ==============================================================================
# Define dataset directories
DATASET_DIR = "Bone_Fracture_Dataset"
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")

# Directory and file name for saving the best trained model
SAVED_MODEL_DIR = "saved_model"
SAVED_MODEL_PATH = os.path.join(SAVED_MODEL_DIR, "best_model.keras")

# Training hyperparameters
IMAGE_SIZE = (224, 224)  # Height x Width for image resizing
BATCH_SIZE = 32          # Number of images processed per step
EPOCHS = 20              # Total training iterations over the dataset
LEARNING_RATE = 0.001    # Adam optimizer learning rate


# ==============================================================================
# 2. DATA PREPROCESSING & AUGMENTATION
# ==============================================================================
# ImageDataGenerator for Training set with Data Augmentation techniques
# Augmentation generates modified versions of images to prevent overfitting
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1.0 / 255.0,        # Normalize pixel values from [0, 255] to [0.0, 1.0]
    rotation_range=20,          # Randomly rotate images up to 20 degrees
    zoom_range=0.2,             # Randomly zoom into images up to 20%
    width_shift_range=0.1,      # Randomly shift images horizontally up to 10%
    height_shift_range=0.1,     # Randomly shift images vertically up to 10%
    horizontal_flip=True        # Randomly flip images horizontally
)

# ImageDataGenerator for Validation and Test sets (Only rescaling, no augmentation)
validation_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1.0 / 255.0         # Normalize pixel values from [0, 255] to [0.0, 1.0]
)

print("Loading Training Images...")
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",        # Binary mode for 2 classes (0 or 1)
    shuffle=True
)

print("Loading Validation Images...")
val_generator = validation_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

print("Loading Test Images...")
test_generator = validation_datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False               # Set shuffle=False to match predictions with ground truth
)


# ==============================================================================
# 3. BUILD CNN MODEL ARCHITECTURE FROM SCRATCH
# ==============================================================================
# Constructing a simple Convolutional Neural Network
model = tf.keras.models.Sequential([
    # First Conv Block: Extract low-level features (edges, textures)
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

    # Second Conv Block: Extract mid-level features
    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

    # Third Conv Block: Extract high-level features
    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

    # Flatten Block: Convert 2D feature maps into a 1D vector
    tf.keras.layers.Flatten(),

    # Fully Connected Dense Layer
    tf.keras.layers.Dense(128, activation='relu'),

    # Dropout Layer: Randomly deactivate neurons during training to reduce overfitting
    tf.keras.layers.Dropout(0.5),

    # Dense Output Layer: 1 neuron with Sigmoid activation for Binary Classification
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Print detailed model architecture summary
model.summary()


# ==============================================================================
# 4. COMPILE MODEL & SETUP CHECKPOINT
# ==============================================================================
# Compile model with Adam optimizer, binary crossentropy loss, and accuracy metric
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Automatically create saved_model directory if it does not exist
os.makedirs(SAVED_MODEL_DIR, exist_ok=True)

# Setup ModelCheckpoint callback to save the best model based on validation accuracy
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath=SAVED_MODEL_PATH,
    monitor='val_accuracy',
    save_best_only=True,
    mode='max',
    verbose=1
)


# ==============================================================================
# 5. TRAIN THE CNN MODEL
# ==============================================================================
print("\nStarting CNN Model Training...\n")
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator,
    callbacks=[checkpoint]
)


# ==============================================================================
# 6. EVALUATE MODEL ON TEST DATASET
# ==============================================================================
print("\nEvaluating the Best Saved Model on Test Dataset...")

# Load the best model saved by ModelCheckpoint
best_model = tf.keras.models.load_model(SAVED_MODEL_PATH)

# Evaluate on test generator
test_loss, test_accuracy = best_model.evaluate(test_generator)

print(f"\n==================================================")
print(f"Test Loss    : {test_loss:.4f}")
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")
print(f"==================================================\n")

# Generate predictions for Confusion Matrix and Classification Report
test_generator.reset()
predictions_prob = best_model.predict(test_generator)
predictions = (predictions_prob > 0.5).astype(int).reshape(-1)
true_labels = test_generator.classes

# Map class names from generator
class_indices = test_generator.class_indices
class_names = list(class_indices.keys())

print("Classification Report:")
print(classification_report(true_labels, predictions, target_names=class_names))

print("Confusion Matrix:")
print(confusion_matrix(true_labels, predictions))


# ==============================================================================
# 7. DISPLAY ACCURACY & LOSS GRAPHS
# ==============================================================================
print("\nDisplaying Training & Validation Performance Graphs...")

plt.figure(figsize=(12, 5))

# Plot Accuracy Graph
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy', color='blue', linewidth=2)
plt.plot(history.history['val_accuracy'], label='Validation Accuracy', color='green', linewidth=2)
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.grid(True)

# Plot Loss Graph
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss', color='red', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss', color='orange', linewidth=2)
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.grid(True)

plt.tight_layout()
plt.show()
