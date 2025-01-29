import flet as ft
import subprocess
import sys
import os
import urllib.request
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
        value=0.0  # Default to 0%
    )

    status_text = ft.Text(
        "Menunggu proses instalasi...",
        size=18,
        color=CustomColor.TEXT,
        weight=ft.FontWeight.BOLD
    )

    est_time_text = ft.Text(
        "⏳ Perkiraan waktu tersisa: -- detik.",
        size=14,
        color=CustomColor.TEXT
    )

    # Read dependencies dynamically from requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r") as file:
            dependencies = [line.strip() for line in file if line.strip() and not line.startswith("#")]
    else:
        dependencies = []

    # Create dependency status row with checkboxes and labels
    dependency_status = [
        {"name": dep, "checkbox": ft.Checkbox(value=False, disabled=True), "label": ft.Text(dep, color=CustomColor.TEXT)}
        for dep in dependencies
    ]

    # Flag to manage process control
    is_running = [False]

    def check_python_installed():
        """Check if Python is installed on the system."""
        try:
            subprocess.run(["python3", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception:
            return False

    def install_python():
        """Automatically install Python if not found."""
        status_text.value = "⏳ Mengunduh dan menginstal Python..."
        page.update()

        if sys.platform == "win32":
            python_installer_url = "https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe"
            installer_path = "python_installer.exe"
        else:  # macOS
            python_installer_url = "https://www.python.org/ftp/python/3.9.9/python-3.9.9-macos11.pkg"
            installer_path = "python_installer.pkg"

        # Download the installer
        urllib.request.urlretrieve(python_installer_url, installer_path)

        # Run the installer
        if sys.platform == "win32":
            subprocess.run([installer_path, "/quiet", "PrependPath=1"])
        else:
            subprocess.run(["sudo", "installer", "-pkg", installer_path, "-target", "/"])

        time.sleep(5)  # Wait for Python to be installed
        return check_python_installed()

    def upgrade_pip():
        """Upgrade pip to the latest version inside the virtual environment."""
        status_text.value = "🔄 Memperbarui pip ke versi terbaru..."
        page.update()
        command = "bisindo_env/bin/python -m pip install --upgrade pip" if sys.platform != "win32" else "bisindo_env\\Scripts\\python -m pip install --upgrade pip"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Log the output
        with open("install.log", "a") as log:
            log.write("\n🔄 Upgrading pip:\n")
            log.write(result.stdout)
            log.write("\n🚨 Errors (if any):\n")
            log.write(result.stderr)

        if result.returncode == 0:
            print("✅ Pip upgraded successfully!")
        else:
            print("❌ Failed to upgrade pip:", result.stderr)

    def create_virtual_env():
        """Create a Python virtual environment."""
        if not os.path.exists("bisindo_env"):
            subprocess.run(["python3", "-m", "venv", "bisindo_env"])
            upgrade_pip()  # Upgrade pip right after creating the virtual environment
        return True

    def install_requirements():
        """Install requirements from requirements.txt and update dependency statuses."""
        log_file = "install.log"

        if len(dependencies) == 0:
            status_text.value = "❌ Tidak ada dependensi ditemukan di requirements.txt!"
            page.update()
            return False

        with open(log_file, "w") as log:
            log.write("📦 **Installation Log:**\n")

        start_time = time.time()  # Start time for overall installation
        time_per_dep = []  # List to track time per dependency

        for idx, dependency in enumerate(dependencies):  # Use correct index from enumerate
            if not is_running[0]:
                status_text.value = "❌ Instalasi dihentikan oleh pengguna."
                page.update()
                return False

            dep_start_time = time.time()  # Start time for current dependency

            status_text.value = f"📦 Menginstall dependensi: {dependency} ({idx + 1}/{len(dependencies)})..."
            page.update()

            # Install the current dependency
            command = f"bisindo_env/bin/pip install {dependency}" if sys.platform != "win32" else f"bisindo_env\\Scripts\\pip install {dependency}"
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Save logs
            with open(log_file, "a") as log:
                log.write(f"\n📦 Installing {dependency}:\n")
                log.write(result.stdout)
                log.write("\n🚨 Errors (if any):\n")
                log.write(result.stderr)

            # Check if the installation was successful
            if result.returncode != 0:
                status_text.value = f"❌ Gagal menginstall {dependency}! Lihat install.log untuk detail."
                page.update()
                return False

            # Update checkbox and label for the installed dependency
            dependency_status[idx]["checkbox"].value = True
            dependency_status[idx]["label"].color = CustomColor.TEXT
            page.update()

            # Calculate time taken for this dependency
            dep_end_time = time.time()
            time_taken = dep_end_time - dep_start_time
            time_per_dep.append(time_taken)

            # Update the progress bar
            progress_bar.value = (idx + 1) / len(dependencies)

            # Calculate estimated time remaining
            avg_time = sum(time_per_dep) / len(time_per_dep)
            remaining_time = avg_time * (len(dependencies) - (idx + 1))
            est_time_text.value = f"⏳ Perkiraan waktu tersisa: {max(1, int(remaining_time))} detik."
            page.update()

        total_time = time.time() - start_time
        status_text.value = f"✅ Semua dependensi terinstall dalam {int(total_time)} detik."
        page.update()
        return True

    def run_installation(e):
        """Execute the installation process step-by-step with progress updates."""
        if is_running[0]:  # Stop the installation if already running
            is_running[0] = False
            start_button.text = "▶️ Mulai Instal"
            start_button.bgcolor = CustomColor.PRIMARY
            start_button.update()
            return

        # Start the installation
        is_running[0] = True
        start_button.text = "🛑 Stop Instalasi"
        start_button.bgcolor = "#FF6B6B"  # Red color for stop
        start_button.update()

        def installation_thread():
            progress_bar.value = 0.0
            status_text.value = "🔍 Memeriksa Python..."
            page.update()

            # Step 1: Check if Python is installed
            if not check_python_installed():
                status_text.value = "❌ Python tidak ditemukan! Menginstal Python..."
                page.update()
                if not install_python():
                    status_text.value = "❌ Gagal menginstal Python! Silakan instal manual."
                    page.update()
                    return

            progress_bar.value = 0.2
            upgrade_pip()
            progress_bar.value = 0.3
            status_text.value = "✅ Python ditemukan. Membuat virtual environment..."
            page.update()

            # Step 2: Create Virtual Environment
            if not create_virtual_env():
                status_text.value = "❌ Gagal membuat virtual environment."
                page.update()
                return

            progress_bar.value = 0.5
            status_text.value = "📦 Menginstall dependensi..."
            page.update()

            # Step 3: Install Requirements
            if not install_requirements():
                status_text.value = "❌ Instalasi gagal. Lihat install.log untuk detail."
                page.update()
                return

            progress_bar.value = 1.0
            status_text.value = "✅ Instalasi selesai! Semua dependensi terinstall."
            start_button.text = "🚀 Mulai Instal"
            start_button.bgcolor = CustomColor.PRIMARY
            start_button.update()
            page.update()

        # Run installation in a separate thread
        Thread(target=installation_thread).start()

    start_button = ft.ElevatedButton(
        text="🚀 Mulai Instal",
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
                est_time_text,
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
