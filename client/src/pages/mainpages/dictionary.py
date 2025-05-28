
import flet as ft
import requests

class DictionaryPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the Dictionary!", size=24, weight="bold"),
                ft.Text("Your Language Companion is on the way", size=16, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )