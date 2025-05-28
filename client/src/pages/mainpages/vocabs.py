import flet as ft
import requests

import flet as ft
import requests

class VocabsPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the Vocabulary Trainer!", size=24, weight="bold"),
                ft.Text("Your Personal Trainer will be ready soon", size=16, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
