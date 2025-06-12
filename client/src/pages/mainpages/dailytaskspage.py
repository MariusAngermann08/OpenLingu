import flet as ft
import requests

try:
    from Widgetlibary.Lectionwidgets import UnderlinedText
    from Widgetlibary.Lectionwidgets import MatchablePairs

except ImportError:
    from pages.Widgetlibary.Lectionwidgets import UnderlinedText
    from pages.Widgetlibary.Lectionwidgets import MatchablePairs

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
                    left_items=["Aufgabe 1", "Aufgabe 2", "Aufgabe 3", "Aufgabe 4"],
                    right_items=["Beschreibung 1", "Beschreibung 2", "Beschreibung 3", "Beschreibung 4"]
                ).build(),
                UnderlinedText("Lösen sie folgende Aufgabe", 
                               {1: "green", 3: "red"},
                               32,
                               "white").render(),
                MatchablePairs(
                    page,
                    left_items=["Aufgabe 1", "Aufgabe 2", "Aufgabe 3", "Aufgabe 4"],
                    right_items=["Beschreibung 1", "Beschreibung 2", "Beschreibung 3", "Beschreibung 4"]
                ).build(),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
