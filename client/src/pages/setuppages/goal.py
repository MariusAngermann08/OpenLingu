import flet as ft
import requests

class GoalSetupPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the Goal Setup Page!", size=24, weight="bold"),
                ft.Text("Set up your goal here", size=16, color="grey"),
                ft.Divider(),
                ft.ElevatedButton(
                    "Finish Setup",
                    on_click=self.page.finish_setup,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )