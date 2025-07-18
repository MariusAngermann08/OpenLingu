import flet as ft
import requests
import os


class EnglishMainPage(ft.Container):
    def __init__(self, page,  mainpage):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.main_page = mainpage
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the English Page", size=24, weight="bold"),
                ft.Text("Youll be able to practice soon", size=16, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )