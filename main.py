import flet as ft
from assets.colors.custom_colors import CustomColor
from components.main_content import CustomMainContent
from components.sidebar import CustomSidebar
from pages.instalasi import InstalasiPage
from pages.petunjuk import PetunjukPage
from pages.pengaturan import PengaturanPage

def main(page: ft.Page):
    page.title = "Dashboard"
    page.bgcolor = CustomColor.BACKGROUND
    page.padding = 0

    # Dynamically import TensorFlow-heavy dependencies when "Mulai" is accessed
    def get_page_content(route):
        if route == "/petunjuk":
            return "Petunjuk", PetunjukPage()
        elif route == "/instalasi":
            return "Instalasi", InstalasiPage(page=page)
        elif route == "/mulai":
            from pages.mulai import MulaiPage  # Lazy import to delay TensorFlow loading
            return "Mulai", MulaiPage(page=page)
        elif route == "/pengaturan":
            return "Pengaturan", PengaturanPage()
        else:
            return "Page Not Found", ft.Text("Page not found", size=20, color=CustomColor.TEXT)

    # Update main content and sidebar selection
    def route_change(e):
        route_to_index = {
            "/petunjuk": 0,
            "/instalasi": 1,
            "/mulai": 2,
            "/pengaturan": 3
        }
        route_index = route_to_index.get(page.route, 0)
        title, content = get_page_content(page.route)
        main_content.update_content(title, content)
        sidebar.update_selection(route_index)
        page.update()

    # Sidebar items with emojis
    sidebar_items = [
        ("Petunjuk", "📄"),
        ("Instalasi", "🚀"),
        ("Mulai", "😆"),
        ("Pengaturan", "🔧")
    ]

    # Sidebar with callback to update route
    def on_item_click(index):
        routes = ["/petunjuk", "/instalasi", "/mulai", "/pengaturan"]
        page.go(routes[index])

    sidebar = CustomSidebar(sidebar_items, on_item_click=on_item_click)
    main_content = CustomMainContent()

    page.add(ft.Row([sidebar, main_content], expand=True))
    page.on_route_change = route_change
    page.go("/petunjuk")

ft.app(target=main)
