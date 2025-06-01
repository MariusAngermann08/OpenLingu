import flet as ft
import requests
import os

class LearningPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                    controls=[
                        ft.Text("Spanish", size=90, weight="w600",),
                        ft.Image(
                        src=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "flags", "Spain.png")),
                        width=200,
                        height=120,
                        fit=ft.ImageFit.CONTAIN
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=20,
                    padding=20,
                    alignment=ft.alignment.center,
                    bgcolor="#d65b09",
                    expand=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: print("Clickable with Ink clicked!"),
                ),

                ft.Container(
                    content=ft.Row(
                    controls=[
                        ft.Text("English", size=90, weight="w600",),
                        ft.Image(
                        src=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "flags", "England.png")),
                        width=200,
                        height=120,
                        fit=ft.ImageFit.CONTAIN
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=20,
                    padding=20,
                    alignment=ft.alignment.center,
                    bgcolor="#726362",
                    expand=True,
                    border_radius=10,
                    ink=True,
                    on_click=lambda e: print("Clickable with Ink clicked!"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
