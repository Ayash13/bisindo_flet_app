import flet as ft
from assets.colors.custom_colors import CustomColor

class CustomSidebar(ft.Container):
    def __init__(self, items, on_item_click):
        super().__init__()
        self.items = items
        self.on_item_click = on_item_click
        self.sidebar_controls = []

        def update_selection(index):
            for i, item in enumerate(self.sidebar_controls):
                item.bgcolor = CustomColor.SECONDARY if i == index else CustomColor.BACKGROUND
                item.content.controls[1].color = CustomColor.TEXT

        # Create sidebar items
        for idx, (label, emoji) in enumerate(self.items):
            container = ft.Container(
                border_radius=20,
                padding=ft.Padding(8, 8, 20, 8),
                bgcolor=CustomColor.SECONDARY if idx == 0 else CustomColor.BACKGROUND,
                content=ft.Row(
                    spacing=15,
                    controls=[
                        # Larger, perfectly square background for emoji
                        ft.Container(
                            width=48,
                            height=48,
                            bgcolor=CustomColor.CARD,
                            border_radius=16,
                            alignment=ft.alignment.center,
                            content=ft.Text(emoji, size=24, weight=ft.FontWeight.BOLD)
                        ),
                        ft.Text(label, size=18, color=CustomColor.TEXT, weight=ft.FontWeight.BOLD)
                    ]
                ),
                # Use `idx=idx` to properly bind the correct index value
                on_click=lambda e, idx=idx: [update_selection(idx), self.on_item_click(idx)],
            )
            self.sidebar_controls.append(container)

        self.content = ft.Container(
            padding=30,
            content=ft.Column(
                controls=[
                    ft.Container(
                        bgcolor=CustomColor.SECONDARY,
                        border_radius=20,
                        padding=16,
                        content=ft.Text("🚀 Logo", weight=ft.FontWeight.BOLD, size=20, color=CustomColor.TEXT)
                    )
                ] + self.sidebar_controls,
                spacing=30  # More spacing for better layout
            )
        )

    def update_selection(self, index):
        for i, item in enumerate(self.sidebar_controls):
            item.bgcolor = CustomColor.SECONDARY if i == index else CustomColor.BACKGROUND
            item.content.controls[1].color = CustomColor.TEXT
