import flet as ft

class LoginPage(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.bgcolor = "#eceff1"  # Soft light background

        super().__init__(
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
        )

        self.email = ft.TextField(
            label="Email",
            width=320,
            border_radius=10,
            border_color="#cfd8dc",
            focused_border_color="#2196f3",
            bgcolor="#f9f9f9",
        )

        self.password = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=320,
            border_radius=10,
            border_color="#cfd8dc",
            focused_border_color="#2196f3",
            bgcolor="#f9f9f9",
        )

        self.message = ft.Text(
            "",
            color="#e53935",
            size=12,
            weight=ft.FontWeight.W_500,
        )

        self.login_button = ft.ElevatedButton(
            text="Login",
            on_click=self.login_click,
            width=320,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(10, 5, 10, 5),
                bgcolor="#2196f3",
                color="white",
                overlay_color="#1976d2",
            )
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome Back 👋",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#263238",
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Login to continue",
                        size=14,
                        color="#607d8b",
                        text_align=ft.TextAlign.CENTER
                    ),
                    self.email,
                    self.password,
                    self.login_button,
                    self.message
                ],
                spacing=18,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.Padding(30, 40, 30, 40),
            border_radius=16,
            bgcolor="#ffffff",
            width=380,
            shadow=ft.BoxShadow(
                blur_radius=30,
                color="#00000020",
                offset=ft.Offset(0, 10),
                spread_radius=0.5,
            ),
            animate=ft.Animation(300, "easeInOut")
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
        