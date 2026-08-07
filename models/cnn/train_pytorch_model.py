"""
==============================================================================
Binary Bone Fracture Detection - PyTorch MobileNetV2 Model Training Script
==============================================================================
This script trains a high-accuracy MobileNetV2 CNN model in PyTorch
for binary classification of bone X-ray images (Fractured vs Not Fractured).
Saves the best performing model weights to models/cnn/best_model.pt.
==============================================================================
"""

import os
import sys
import time
import glob
import random
import ssl

# Bypass SSL certificate verification for downloading pre-trained weights
ssl._create_default_https_context = ssl._create_unverified_context

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.models as models
from PIL import Image, ImageFile, ImageEnhance

# Allow PIL to load truncated/damaged medical images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Detect Device (Apple Silicon MPS / CUDA / CPU)
if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_DIR = os.path.join(BASE_DIR, "Bone_Fracture_Dataset")
TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VAL_DIR = os.path.join(DATASET_DIR, "val")
TEST_DIR = os.path.join(DATASET_DIR, "test")
SAVED_MODEL_PATH = os.path.join(BASE_DIR, "models", "cnn", "best_model.pt")

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 128
EPOCHS = 3
LEARNING_RATE = 0.0008


class BoneDataset(Dataset):
    """
    Dataset loader for Bone Fracture X-ray images.
    Class Mapping:
    - 'fractured': 0
    - 'not fractured': 1
    """
    def __init__(self, root_dir, augment=False):
        self.samples = []
        self.augment = augment
        
        frac_files = glob.glob(os.path.join(root_dir, "fractured", "*"))
        not_frac_files = glob.glob(os.path.join(root_dir, "not fractured", "*"))
        
        for f in frac_files:
            self.samples.append((f, 0))
        for f in not_frac_files:
            self.samples.append((f, 1))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            img = Image.open(path).convert("RGB").resize(IMAGE_SIZE)
            
            if self.augment:
                # Random Horizontal Flip
                if random.random() > 0.5:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                # Random slight contrast shift
                if random.random() > 0.5:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(random.uniform(0.9, 1.1))
            
            # Standard ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            arr = np.array(img, dtype=np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            arr = (arr - mean) / std
            arr = arr.transpose(2, 0, 1) # HWC -> CHW
            
            return torch.tensor(arr, dtype=torch.float32), torch.tensor(label, dtype=torch.float32)
        except Exception:
            return torch.zeros((3, 224, 224), dtype=torch.float32), torch.tensor(label, dtype=torch.float32)


def get_mobilenet_model():
    """Build MobileNetV2 model architecture for binary classification."""
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    # Replace final linear layer for single logit output
    num_ftrs = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(num_ftrs, 1)
    )
    return model


def train_model():
    print(f"Device set to: {DEVICE}")
    print("Loading Datasets...")

    train_ds = BoneDataset(TRAIN_DIR, augment=True)
    val_ds = BoneDataset(VAL_DIR, augment=False)
    test_ds = BoneDataset(TEST_DIR, augment=False)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"Dataset Counts -> Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")

    model = get_mobilenet_model().to(DEVICE)
    torch.save(model.state_dict(), SAVED_MODEL_PATH)
    print(f" -> Initialized MobileNetV2 model saved to '{SAVED_MODEL_PATH}'")
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    best_val_acc = 0.0
    os.makedirs(os.path.dirname(SAVED_MODEL_PATH), exist_ok=True)

    print("\nStarting MobileNetV2 Model Training...\n" + "=" * 55)
    for epoch in range(EPOCHS):
        start_time = time.time()
        model.train()
        running_loss, correct, total = 0.0, 0, 0

        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(imgs).squeeze(1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            preds = (torch.sigmoid(outputs) >= 0.5).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            running_loss += loss.item() * labels.size(0)

        train_acc = (correct / total) * 100.0
        train_loss = running_loss / total

        # Validation Phase
        model.eval()
        val_correct, val_total, val_running_loss = 0, 0, 0.0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs = model(imgs).squeeze(1)
                loss = criterion(outputs, labels)

                preds = (torch.sigmoid(outputs) >= 0.5).float()
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
                val_running_loss += loss.item() * labels.size(0)

        val_acc = (val_correct / val_total) * 100.0
        val_loss = val_running_loss / val_total

        elapsed = time.time() - start_time

        print(f"Epoch {epoch+1:02d}/{EPOCHS:02d} [{elapsed:.1f}s] | "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), SAVED_MODEL_PATH)
            print(f" -> Saved best MobileNetV2 checkpoint to '{SAVED_MODEL_PATH}' (Val Acc: {val_acc:.2f}%)")

    # Final Test Evaluation
    print("\n" + "=" * 55)
    print("Evaluating Best MobileNetV2 Model on Unseen Test Dataset...")
    if os.path.exists(SAVED_MODEL_PATH):
        model.load_state_dict(torch.load(SAVED_MODEL_PATH, map_location=DEVICE))
        model.eval()
        test_correct, test_total = 0, 0
        nf_correct, nf_total = 0, 0
        f_correct, f_total = 0, 0

        with torch.no_grad():
            for imgs, labels in test_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                outputs = model(imgs).squeeze(1)
                preds = (torch.sigmoid(outputs) >= 0.5).float()

                test_correct += (preds == labels).sum().item()
                test_total += labels.size(0)

                for p, l in zip(preds, labels):
                    if l.item() == 1.0: # Not Fractured
                        nf_total += 1
                        if p.item() == 1.0:
                            nf_correct += 1
                    else: # Fractured
                        f_total += 1
                        if p.item() == 0.0:
                            f_correct += 1

        overall_acc = (test_correct / test_total) * 100.0
        nf_acc = (nf_correct / nf_total) * 100.0 if nf_total > 0 else 0
        f_acc = (f_correct / f_total) * 100.0 if f_total > 0 else 0

        print(f"Test Set Overall Accuracy   : {overall_acc:.2f}% ({test_correct}/{test_total})")
        print(f"Not Fractured Class Accuracy: {nf_acc:.2f}% ({nf_correct}/{nf_total})")
        print(f"Fractured Class Accuracy    : {f_acc:.2f}% ({f_correct}/{f_total})")

if __name__ == "__main__":
    train_model()
