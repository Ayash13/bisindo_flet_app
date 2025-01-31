import flet as ft
import cv2
import threading
import sys
from assets.colors.custom_colors import CustomColor
from core.detection import (
    load_heavy_dependencies,
    load_model,
    generate_placeholder_image,
    fix_feature_vector_length,
    model,
    labels_dict,
    model_loaded,
    ENABLE_VIRTUAL_CAM
)
import pyvirtualcam
import numpy as np
import base64

def MulaiPage(page: ft.Page):
    stop_flag = [False]
    model_ready = [False]  
    virtual_cam = [None]  

    def start_background_loading():
        """Load TensorFlow and model in the background after UI is displayed."""
        def background_task():
            load_heavy_dependencies()  
            load_model()  
            model_ready[0] = True  
            camera_placeholder.content = ft.Text("📷", size=100)  
            status_text.value = "Klik tombol mulai untuk mulai mendeteksi."  
            page.update()

        threading.Thread(target=background_task, daemon=True).start()

    def start_inference(e):
        """Starts the sign language detection and updates the camera frame in Flet UI."""
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
                virtual_cam[0] = pyvirtualcam.Camera(width=W, height=H, fps=30)
                print(f"✅ Virtual Camera started! Resolution: {W}x{H}")

            camera_placeholder.content = camera_frame  
            page.update()

            while not stop_flag[0]:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)  
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                data_aux = []
                x_ = []
                y_ = []

                results = hands.process(frame_rgb)
                predicted_character = "⏳ Loading..." if not model_ready[0] else "Unknown"

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                        )

                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            x_.append(x)
                            y_.append(y)

                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_aux.append(x - min(x_))
                            data_aux.append(y - min(y_))

                    data_aux = fix_feature_vector_length(data_aux, 21 * 2 * 2)

                    if model_ready[0]:
                        prediction = model[0].predict([np.asarray(data_aux)])
                        predicted_class = int(prediction[0])
                        predicted_character = labels_dict[0].get(str(predicted_class), "Unknown")

                    x1 = int(min(x_) * W) - 10
                    y1 = int(min(y_) * H) - 10
                    x2 = int(max(x_) * W) + 10
                    y2 = int(max(y_) * H) + 10
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, predicted_character, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if ENABLE_VIRTUAL_CAM and virtual_cam[0]:
                    virtual_cam[0].send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    virtual_cam[0].sleep_until_next_frame()

                _, buffer = cv2.imencode(".png", frame)
                encoded_image = base64.b64encode(buffer).decode("utf-8")
                camera_frame.src_base64 = encoded_image
                status_text.value = f"🔍 {predicted_character}"  
                page.update()

            cap.release()
            stop_inference(None)

        threading.Thread(target=inference_thread, daemon=True).start()
        status_text.value = "🔄 Deteksi dimulai..."
        page.update()

    def stop_inference(e):
        stop_flag[0] = True
        status_text.value = "⏹️ Deteksi dihentikan."
        camera_placeholder.content = ft.Text("📷", size=100)  

        if ENABLE_VIRTUAL_CAM and virtual_cam[0]:
            virtual_cam[0].close()
            virtual_cam[0] = None
            print("❌ Virtual Camera stopped.")

        page.update()

    camera_frame = ft.Image(
        fit=ft.ImageFit.COVER,
        aspect_ratio=16 / 10.5,
        src_base64=generate_placeholder_image()
    )

    camera_placeholder = ft.Container(
        expand=True,
        aspect_ratio=16 / 10.5,
        border_radius=32,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
        bgcolor=CustomColor.CARD,
        alignment=ft.alignment.center,
        content=ft.ProgressRing(width=60, height=60, stroke_width=5)  
    )

    start_button = ft.ElevatedButton(
        text="▶️ Mulai",
        bgcolor=CustomColor.PRIMARY,
        color=CustomColor.CARD,
        height=60,
        width=200,
        on_click=start_inference
    )

    stop_button = ft.ElevatedButton(
        text="🛑 Stop",
        bgcolor="#FF6B6B",
        color=CustomColor.CARD,
        height=60,
        width=200,
        on_click=stop_inference
    )

    status_text = ft.Text(
        "⏳ Memuat model...",  
        size=18,
        color=CustomColor.TEXT,
        text_align=ft.TextAlign.CENTER
    )

    start_background_loading()

    return ft.Container(
        expand=True,
        width=float("inf"),
        bgcolor=CustomColor.BACKGROUND,
        border_radius=30,
        padding=32,
        alignment=ft.alignment.center,
        content=ft.Row([
            ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=40, controls=[camera_placeholder, status_text]),
            ft.Container(width=16),
            ft.Column(alignment=ft.MainAxisAlignment.CENTER, spacing=20, controls=[start_button, stop_button])
        ])
    )
