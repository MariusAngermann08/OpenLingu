import flet as ft
import requests

try:
    from Widgetlibary.Lectionwidgets import UnderlinedText
    from Widgetlibary.Lectionwidgets import MatchablePairs
    from Widgetlibary.Lectionwidgets import PictureDrag

except ImportError:
    from pages.Widgetlibary.Lectionwidgets import UnderlinedText
    from pages.Widgetlibary.Lectionwidgets import MatchablePairs
    from pages.Widgetlibary.Lectionwidgets import PictureDrag

class DailyTasksPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                PictureDrag(
                    page,
                    image_path="",
                    options=["Katze", "Hund", "Maus"],
                    correct_option_index=1,
                ).build()
                

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
