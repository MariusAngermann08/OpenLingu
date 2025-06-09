import flet as ft
import requests

try:
    from Widgetlibary.Lectionwidgets import UnderlinedText

except ImportError:
    from pages.Widgetlibary.Lectionwidgets import UnderlinedText

class DailyTasksPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                UnderlinedText(
                    "This is a test for research purposes.",
                    {3 : "red", 5: "blue"},
                    32,
                    "green",
                ).render(),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
