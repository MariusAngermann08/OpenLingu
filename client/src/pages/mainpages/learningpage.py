import flet as ft
import requests
import os


class LearningPage(ft.Container):
    def __init__(self, page, mainpage):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.main_page = mainpage
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Row(
            controls=[ 
                    ft.Container(
                        content=ft.Row(
                        controls=[
                            ft.Text("Lektion 1", size=70, weight="w600",),
                        ],
                        alignment = ft.MainAxisAlignment.CENTER,
                        ),
                        margin=50,
                        padding=20,
                        alignment=ft.alignment.center,
                        bgcolor="#d65b09",
                        width=500,
                        height=500,
                        border_radius=10,
                        ink=True,
                    )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
                
