import flet as ft

class LoginPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            width=400,
            height=500,
            bgcolor="#f5f5f5",
            padding=20,
            alignment=ft.alignment.center
        )
        self.page = page
        self.email = ft.TextField(label="Email", width=300, autofocus=True)
        self.password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        self.message = ft.Text("", color="#ea4335")

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BOLD),
                    self.email,
                    self.password,
                    ft.ElevatedButton(
                        text="Login",
                        on_click=self.login_click,
                        width=300,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=15,
                        )
                    ),
                    self.message
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=30,
            border_radius=12,
            bgcolor="#ffffff",
            width=350,
            shadow=ft.BoxShadow(blur_radius=15, color="#1a1a1a1f")
        )

    def login_click(self, e):
        # For now, just navigate to main menu without validation
        self.page.go("/main")
        # Uncomment below for actual login validation
        # if self.email.value == "user@example.com" and self.password.value == "secret":
        #     self.message.value = "Login successful!"
        #     self.message.color = "#34a853"
        #     self.page.go("/main")
        # else:
        #     self.message.value = "Invalid credentials"
        #     self.message.color = "#ea4335"
        # self.page.update()
        