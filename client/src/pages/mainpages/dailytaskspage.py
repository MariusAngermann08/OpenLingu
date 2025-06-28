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

        self.button = ft.ElevatedButton(
            text="Go to the Lections",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_500,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=12),
                overlay_color=ft.Colors.BLUE_700,
            ),
            on_click= None
    )
        
        self.tutorial_button = ft.ElevatedButton(
            text="Start Tutorial",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE_500,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=12),
                overlay_color=ft.Colors.BLUE_700,
            ),
            on_click= None 
        )
        
        self.content = ft.Column(
            controls=[
               ft.Text("This Page is currently under Construction", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text("Please check back later for updates", size=20, weight=ft.FontWeight.NORMAL, color=ft.Colors.GREY_600),
                self.button,
                self.tutorial_button,
                

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
