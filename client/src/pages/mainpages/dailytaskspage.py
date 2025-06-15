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
               DraggableText(
                   page=page,
                   text= "Hello, this page is called because we are silly as ",
                   gaps_idx= [5, 10],
                   options = {"Daily Tasks" : 0, "hell": 1},
               ).build()
                

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
