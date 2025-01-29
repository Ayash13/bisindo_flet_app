import flet as ft
from assets.colors.custom_colors import CustomColor

def PetunjukPage():
    return ft.Container(
        expand=True,
        width=float("inf"),
        bgcolor=CustomColor.BACKGROUND,
        border_radius=15,
        padding=20,
        content=ft.Text("Petunjuk Content", size=18, color=CustomColor.TEXT)
    )
