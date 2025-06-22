import flet as ft
import requests

class LanguageChooser(ft.Container):
    def __init__(self, page, mainpage):
        super().__init__()
        self.page = page
        self.mainpage = mainpage

        self.content = ft.Column(
            [
                ft.Text("Select a language", size=24, weight="bold"),
                ft.Text("Choose your language here", size=16, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )