import cv2
import threading
import pickle
import numpy as np
import json
import os
import base64
import sys
import flet as ft
import sklearn
import pyvirtualcam  # OBS Virtual Camera
from collections import deque, Counter
import time

mp = None  # Lazy import for TensorFlow-related dependencies
model = [None]
labels_dict = [None]
model_loaded = [False]
ENABLE_VIRTUAL_CAM = sys.platform != "darwin"  # Disable virtual camera on macOS

# Buffer for predictions to construct sentences
prediction_buffer = deque(maxlen=10)
constructed_sentence = ""
word_delay = 10  # Number of frames before adding a new word
frame_counter = 0
last_detection_time = time.time()
hand_detected = False

# Adjustable variables
RECTANGLE_MARGIN_BOTTOM = 120  # Controls the margin from the bottom of the frame
TEXT_SIZE = 1.0  # Controls the size of the subtitle text
TEXT_THICKNESS = 2  # Controls text thickness
LINE_SPACING = 40  # Controls spacing between lines


def load_heavy_dependencies():
    global mp
    import mediapipe as mp  
    model_loaded[0] = True


def load_model():
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
    blank_image = np.ones((480, 800, 3), dtype=np.uint8) * 255  
    _, buffer = cv2.imencode(".png", blank_image)
    return base64.b64encode(buffer).decode("utf-8")


def fix_feature_vector_length(data_aux, expected_length):
    if len(data_aux) < expected_length:
        data_aux += [0] * (expected_length - len(data_aux))
    elif len(data_aux) > expected_length:
        data_aux = data_aux[:expected_length]
    return data_aux


def reset_subtitle():
    global constructed_sentence, prediction_buffer, frame_counter, hand_detected
    constructed_sentence = ""
    prediction_buffer.clear()
    frame_counter = 0
    hand_detected = False


def update_sentence():
    global constructed_sentence, frame_counter
    if len(prediction_buffer) == prediction_buffer.maxlen:
        most_common = Counter(prediction_buffer).most_common(1)[0][0]
        if most_common != "Unknown":
            if not constructed_sentence or most_common != constructed_sentence.split()[-1]:
                constructed_sentence += (" " + most_common) if constructed_sentence else most_common
    prediction_buffer.clear()
    frame_counter = 0


def wrap_text(text, max_width, font_scale, thickness):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        text_size = cv2.getTextSize(test_line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        if text_size[0] > max_width:
            lines.append(current_line)
            current_line = word
            if len(lines) >= 2:  # Maximum of two lines
                return lines, True
        else:
            current_line = test_line
    
    lines.append(current_line)
    return lines, False


def start_inference(stop_flag, model_ready, virtual_cam, camera_placeholder, camera_frame, status_text, page):
    def inference_thread():
        status_text.value = "🔄 Model dimuat. Memulai deteksi..."
        page.update()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            status_text.value = "❌ Kamera tidak ditemukan!"
            page.update()
            return
        _, test_frame = cap.read()
        H, W, _ = test_frame.shape  

        import mediapipe as mp  
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        stop_flag[0] = False

        if ENABLE_VIRTUAL_CAM:
            virtual_cam[0] = pyvirtualcam.Camera(width=W, height=H, fps=30, fmt=pyvirtualcam.PixelFormat.RGB)
            print(f"✅ Virtual Camera started! Resolution: {W}x{H}")

        camera_placeholder.content = camera_frame
        page.update()

        global frame_counter, last_detection_time, hand_detected
        while not stop_flag[0]:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)  
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert for virtual cam
            data_aux, x_, y_ = [], [], []
            results = hands.process(frame_rgb)
            predicted_character = "Unknown"

            if results.multi_hand_landmarks:
                if not hand_detected:
                    reset_subtitle()
                hand_detected = True
                last_detection_time = time.time()
                for hand_landmarks in results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                    )
                    for i in range(len(hand_landmarks.landmark)):
                        x_.append(hand_landmarks.landmark[i].x)
                        y_.append(hand_landmarks.landmark[i].y)
                    for i in range(len(hand_landmarks.landmark)):
                        data_aux.append(hand_landmarks.landmark[i].x - min(x_))
                        data_aux.append(hand_landmarks.landmark[i].y - min(y_))
                data_aux = fix_feature_vector_length(data_aux, 21 * 2 * 2)
                if model_ready[0]:
                    prediction = model[0].predict([np.asarray(data_aux)])
                    predicted_class = int(prediction[0])
                    predicted_character = labels_dict[0].get(str(predicted_class), "Unknown")
                    prediction_buffer.append(predicted_character)
            
            frame_counter += 1
            if frame_counter >= word_delay:
                update_sentence()
            
            if hand_detected and time.time() - last_detection_time < 3:
                lines, exceeded = wrap_text(constructed_sentence, W - 100, TEXT_SIZE, TEXT_THICKNESS)
                text_width = max([cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, TEXT_THICKNESS)[0][0] for line in lines]) + 40
                subtitle_bg_height = len(lines) * LINE_SPACING + 30
                subtitle_y = H - RECTANGLE_MARGIN_BOTTOM - (len(lines) - 1) * LINE_SPACING
                text_x = (W - text_width) // 2
                overlay = frame.copy()
                cv2.rectangle(overlay, (text_x, subtitle_y), (text_x + text_width, subtitle_y + subtitle_bg_height), (0, 0, 0, 180), -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                for i, line in enumerate(lines):
                    cv2.putText(frame, line, (text_x + 20, subtitle_y + 45 + i * LINE_SPACING), cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, (255, 255, 255), TEXT_THICKNESS, cv2.LINE_AA)
                if exceeded:
                    reset_subtitle()
            else:
                reset_subtitle()

            # **Send the frame with the prediction overlay to OBS Virtual Camera**
            if ENABLE_VIRTUAL_CAM and virtual_cam[0]:
                virtual_cam[0].send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # Send processed frame
                virtual_cam[0].sleep_until_next_frame()

            # Update UI with the latest frame
            _, buffer = cv2.imencode(".png", frame)
            camera_frame.src_base64 = base64.b64encode(buffer).decode("utf-8")
            page.update()

        cap.release()
        stop_inference(stop_flag, virtual_cam, camera_placeholder, status_text, page)

    threading.Thread(target=inference_thread, daemon=True).start()
    status_text.value = "🔄 Deteksi dimulai..."
    page.update()


def stop_inference(stop_flag, virtual_cam, camera_placeholder, subtitle_text, page):
    """Stops the sign language detection."""
    stop_flag[0] = True
    subtitle_text.value = "⏹️ Deteksi dihentikan."
    camera_placeholder.content = ft.Text("📷", size=100)  

    if ENABLE_VIRTUAL_CAM and virtual_cam[0]:
        virtual_cam[0].close()
        virtual_cam[0] = None
        print("❌ Virtual Camera stopped.")

    page.update()
