import flet as ft
import requests

class LearningPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Spanish", size=30, weight="w600",),
                    margin=10,
                    padding=10,
                    alignment=ft.alignment.center,
                    bgcolor="#d65b09",
                    expand=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: print("Clickable with Ink clicked!"),
                ),

                ft.Container(
                    content=ft.Text("English",size=30, weight="w600"),
                    margin=10,
                    padding=10,
                    alignment=ft.alignment.center,
                    bgcolor="#1059e0",
                    expand=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: print("Clickable with Ink clicked!"),
                ),

                ft.Image(
                    src="assets/flags/Spain.png",
                    width=100,
                    height=60
                    fit=ft.ImageFit.CONTAIN
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
