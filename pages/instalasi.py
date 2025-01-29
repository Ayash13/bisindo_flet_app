import flet as ft
import subprocess
import sys
import os
import time
from threading import Thread
from assets.colors.custom_colors import CustomColor


def InstalasiPage(page: ft.Page):
    progress_bar = ft.ProgressBar(
        width=600,
        height=14,
        border_radius=20,
        color=CustomColor.PRIMARY,
        bgcolor=CustomColor.SECONDARY,
        value=0.0
    )

    status_text = ft.Text(
        "Menunggu proses pemeriksaan...",
        size=18,
        color=CustomColor.TEXT,
        weight=ft.FontWeight.BOLD
    )

    # Load dependencies from requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    dependencies = []

    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as file:
            dependencies = [line.strip() for line in file if line.strip() and not line.startswith("#")]

    # UI checkboxes for dependencies
    dependency_status = [
        {"name": dep, "checkbox": ft.Checkbox(value=False, disabled=True), "label": ft.Text(dep, color=CustomColor.TEXT)}
        for dep in dependencies
    ]

    is_running = [False]

    def check_python_installed():
        """Check if Python is installed properly."""
        try:
            python_exec = sys.executable
            result = subprocess.run([python_exec, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                print(f"✅ Python ditemukan: {result.stdout.strip()}")
                return True

            command = "where python" if sys.platform == "win32" else "which python3"
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.stdout.strip():
                print(f"✅ Python ditemukan di: {result.stdout.strip()}")
                return True

        except Exception as e:
            print(f"❌ Error checking Python installation: {e}")

        return False

    def check_library_installed(library_name):
        """Check if a library is installed in the current Python environment."""
        try:
            command = [sys.executable, "-m", "pip", "show", library_name]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error checking library {library_name}: {e}")
            return False

    def check_obs_installed():
        """Check if OBS Studio is installed on Windows or macOS."""
        try:
            if sys.platform == "win32":
                possible_paths = [
                    "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
                    "C:\\Program Files (x86)\\obs-studio\\bin\\64bit\\obs64.exe"
                ]
                obs_installed = any(os.path.exists(path) for path in possible_paths)
                if not obs_installed:
                    result = subprocess.run("where obs", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    obs_installed = result.returncode == 0
            else:  # macOS
                possible_paths = [
                    "/Applications/OBS.app",
                    "/Applications/OBS Studio.app"
                ]
                obs_installed = any(os.path.exists(path) for path in possible_paths)
                if not obs_installed:
                    result = subprocess.run("which obs", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    obs_installed = result.returncode == 0

            if obs_installed:
                print("✅ OBS Studio ditemukan.")
            else:
                print("❌ OBS Studio tidak ditemukan!")

            return obs_installed

        except Exception as e:
            print(f"❌ Error checking OBS installation: {e}")
            return False

    def check_dependencies():
        """Check if all dependencies in requirements.txt are installed."""
        status_text.value = "🔍 Memeriksa dependensi..."
        page.update()

        for idx, dependency in enumerate(dependencies):
            if check_library_installed(dependency):
                dependency_status[idx]["checkbox"].value = True
                dependency_status[idx]["label"].color = CustomColor.TEXT
            else:
                dependency_status[idx]["checkbox"].value = False
                dependency_status[idx]["label"].color = "#FF6B6B"  # Red for missing dependencies

            progress_bar.value = (idx + 1) / len(dependencies)
            page.update()

        status_text.value = "✅ Pemeriksaan dependensi selesai."
        page.update()

    def run_installation(e):
        """Execute the dependency and OBS check process."""
        if is_running[0]:
            is_running[0] = False
            start_button.text = "🔍 Periksa Dependensi"
            start_button.bgcolor = CustomColor.PRIMARY
            start_button.update()
            return

        is_running[0] = True
        start_button.text = "🛑 Berhenti"
        start_button.bgcolor = "#FF6B6B"
        start_button.update()

        def check_thread():
            check_dependencies()
            obs_installed = check_obs_installed()

            if obs_installed:
                obs_status_label.value = "📡 OBS Studio Terdeteksi! 🚀 Siap digunakan!"
                obs_status_label.color = CustomColor.TEXT
            else:
                obs_status_label.value = "🚨 OBS Studio Tidak Ditemukan! 😢"
                obs_status_label.color = "#FF6B6B"  # Red text

            is_running[0] = False
            start_button.text = "🔍 Periksa Dependensi"
            start_button.bgcolor = CustomColor.PRIMARY
            start_button.update()
            page.update()

        Thread(target=check_thread).start()

    start_button = ft.ElevatedButton(
        text="🔍 Periksa Dependensi",
        bgcolor=CustomColor.PRIMARY,
        color=CustomColor.CARD,
        height=65,
        width=230,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25),
            padding=ft.Padding(18, 25, 18, 25)
        ),
        on_click=run_installation
    )

    # Fun OBS Status section (Replacing estimated time)
    obs_status_label = ft.Text(
        "🕵️‍♂️ Mencari OBS Studio... 🔎",
        color="#AAAAAA"  # Gray text while searching
    )

    return ft.Container(
        expand=True,
        width=float("inf"),
        bgcolor=CustomColor.BACKGROUND,
        border_radius=30,
        padding=40,
        alignment=ft.alignment.center,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=28,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=100,
                    controls=[
                        step_item("🐍", "Environment"),
                        step_item("📦", "Library"),
                        step_item("🎥", "OBS"),
                    ]
                ),
                status_text,
                progress_bar,
                # Replacing estimated time with fun OBS Status
                obs_status_label,
                # Dependency checkboxes and labels
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.Row(
                            spacing=5,
                            controls=[status["checkbox"], status["label"]]
                        ) for status in dependency_status
                    ]
                ),
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=20,
                    content=start_button
                )
            ]
        )
    )


def step_item(emoji, label):
    return ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.Container(
                width=110,
                height=110,
                bgcolor=CustomColor.CARD,
                border_radius=25,
                alignment=ft.alignment.center,
                content=ft.Text(emoji, size=50)
            ),
            ft.Text(label, size=18, color=CustomColor.TEXT, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD)
        ]
    )
