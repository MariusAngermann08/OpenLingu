import flet as ft
import requests

class ProfileSetupPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the Profile Setup Page!", size=24, weight="bold"),
                ft.Text("Set up your profile here", size=16, color="grey"),
                ft.Divider(),
                ft.ElevatedButton(
                    "Next",
                    on_click=self.page.next_page,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )