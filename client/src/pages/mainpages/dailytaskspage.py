import flet as ft
import requests

try:
    from Widgetlibary.Lectionwidgets import UnderlinedText
    from Widgetlibary.Lectionwidgets import MatchablePairs
    from Widgetlibary.Lectionwidgets import PictureDrag
    from Widgetlibary.Lectionwidgets import DraggableText

except ImportError:
    from pages.Widgetlibary.Lectionwidgets import UnderlinedText
    from pages.Widgetlibary.Lectionwidgets import MatchablePairs
    from pages.Widgetlibary.Lectionwidgets import PictureDrag
    from pages.Widgetlibary.Lectionwidgets import DraggableText

class DailyTasksPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
               MatchablePairs(
                   page,
                   left_items=["Dog", "Cat", "Fish"],
                   right_items=["Hund","Katze","Fisch"],
               ).build()
               
                

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
