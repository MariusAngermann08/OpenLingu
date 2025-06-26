import flet as ft


lass LoginPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.email = ft.TextField(label="Email", width=300, autofocus=True)
        self.password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        self.message = ft.Text("", color=ft.colors.RED)

    def login_click(self, e):
        if self.email.value == "user@example.com" and self.password.value == "secret":
            self.message.value = "Login successful!"
            self.message.color = ft.colors.GREEN
        else:
            self.message.value = "Invalid credentials"
            self.message.color = ft.colors.RED
        self.page.update()

    def build(self):
        self.page.title = "Login"
        self.page.bgcolor = ft.colors.SURFACE
        self.page.window_width = 400
        self.page.window_height = 400
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        login_button = ft.ElevatedButton(
            text="Login",
            on_click=self.login_click,
            width=300,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=15,
            )
        )

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BOLD),
                    self.email,
                    self.password,
                    login_button,
                    self.message
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=30,
            border_radius=12,
            bgcolor=ft.colors.WHITE,
            width=350,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.colors.BLACK12)
        )


    page.add(card)

ft.app(target=main)
