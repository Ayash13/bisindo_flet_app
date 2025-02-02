import flet as ft
import threading
import sklearn
from assets.colors.custom_colors import CustomColor
from core.detection import (
    load_heavy_dependencies,
    load_model,
    generate_placeholder_image,
    start_inference,
    stop_inference,
    model_loaded,
    ENABLE_VIRTUAL_CAM
)

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

    camera_frame = ft.Image(
        fit=ft.ImageFit.COVER,
        aspect_ratio=16 / 10.6,
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
        on_click=lambda e: start_inference(stop_flag, model_ready, virtual_cam, camera_placeholder, camera_frame, status_text, page)
    )

    stop_button = ft.ElevatedButton(
        text="🛑 Stop",
        bgcolor="#FF6B6B",
        color=CustomColor.CARD,
        height=60,
        width=200,
        on_click=lambda e: stop_inference(stop_flag, virtual_cam, camera_placeholder, status_text, page)
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
