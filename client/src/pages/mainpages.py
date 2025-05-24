import flet as ft

class MainPage(ft.Container):
    def __init__(self, page, route):
        super().__init__()
        self.page = page
        self.route = route

        self.content = ft.Column(
            [
                ft.Text("This is the main page of the app a users encounters after login", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                ft.ElevatedButton(
                    "Sign Out",
                    on_click=self.sign_out,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    
    def sign_out(self, e):
        self.page.go("/")
