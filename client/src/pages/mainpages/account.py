import flet as ft
import requests

class AccountPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
           controls = [
                ft.Text("Account Page", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("This is where you can manage your account settings."),
                ft.Text("Currently, this page is under construction.")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )