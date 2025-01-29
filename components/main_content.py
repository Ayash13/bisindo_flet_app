import flet as ft
from assets.colors.custom_colors import CustomColor

class CustomMainContent(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            width=float("inf"),
            bgcolor=CustomColor.CARD,
            border_radius=20,
            padding=25,
            content=ft.Column([
                ft.Container(
                    height=80,
                    width=240,
                    bgcolor=CustomColor.SECONDARY,
                    border_radius=20,
                    padding=8,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        spacing=15,
                        controls=[
                            # Larger, perfectly square background for emoji
                            ft.Container(
                                width=64,
                                height=64,
                                bgcolor=CustomColor.CARD,
                                border_radius=16,
                                alignment=ft.alignment.center,
                                content=ft.Text("📄", size=28, weight=ft.FontWeight.BOLD)  # Default emoji
                            ),
                            ft.Text(
                                "Select a Page",  # Default text
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=CustomColor.TEXT,
                                key="title"
                            )
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    width=float("inf"),
                    bgcolor=CustomColor.BACKGROUND,
                    border_radius=15,
                    padding=20,
                )
            ], spacing=30)  # More spacing for a cleaner look
        )

    def update_content(self, title, new_content):
        # Map titles to their corresponding emojis
        title_emojis = {
            "Petunjuk": "📄",
            "Instalasi": "🚀",
            "Mulai": "😆",
            "Pengaturan": "🔧"
        }

        # Add the emoji inside a larger square box
        emoji = title_emojis.get(title, "📄")  # Default to 📄 if title not found
        self.content.controls[0].content.controls[0].content.value = emoji
        self.content.controls[0].content.controls[1].value = title

        # Update the main content
        self.content.controls[1] = new_content
