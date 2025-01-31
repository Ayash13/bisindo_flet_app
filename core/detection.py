import cv2
import threading
import pickle
import numpy as np
import json
import os
import base64
import sys
import pyvirtualcam  # OBS Virtual Camera

# Lazy import for TensorFlow-related dependencies
mp = None  
model = [None]
labels_dict = [None]
model_loaded = [False]

# Disable virtual camera on macOS
ENABLE_VIRTUAL_CAM = sys.platform != "darwin"  # False for macOS, True for Windows

def load_heavy_dependencies():
    """Load TensorFlow and MediaPipe only when needed."""
    global mp
    import mediapipe as mp  
    model_loaded[0] = True

def load_model():
    """Load the trained model and label dictionary asynchronously."""
    try:
        model_path = os.path.join(os.path.dirname(__file__), "../model.p")
        labels_path = os.path.join(os.path.dirname(__file__), "../label_dict.json")

        model_dict = pickle.load(open(model_path, 'rb'))
        model[0] = model_dict['model']

        with open(labels_path, 'r') as f:
            labels_dict[0] = json.load(f)

        model_loaded[0] = True
        print("✅ Model and labels loaded successfully.")

    except Exception as e:
        print(f"❌ Error loading model: {e}")

def generate_placeholder_image():
    """Generates a blank white image as a placeholder."""
    blank_image = np.ones((480, 800, 3), dtype=np.uint8) * 255  
    _, buffer = cv2.imencode(".png", blank_image)
    return base64.b64encode(buffer).decode("utf-8")

def fix_feature_vector_length(data_aux, expected_length):
    """Ensure feature vector has the correct length for the model."""
    if len(data_aux) < expected_length:
        data_aux += [0] * (expected_length - len(data_aux))  
    elif len(data_aux) > expected_length:
        data_aux = data_aux[:expected_length]  
    return data_aux
