import flet as ft

class SignInPage(ft.Container):
    def __init__(self, page, route):
        super().__init__()
        self.page = page
        self.route = route

        # Create a card for the sign-in form
        sign_in_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome Back", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        ft.Text("Sign into your OpenLingu Account", size=14, color="#616161"),
                        ft.Divider(height=25, color="transparent"),
                        
                        # Username field with icon
                        ft.TextField(
                            label="Username",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="person",
                            hint_text="Enter your username",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        
                        # Password field with icon
                        ft.TextField(
                            label="Password",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="lock",
                            password=True,
                            can_reveal_password=True,
                            hint_text="Enter your password",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        
                        # Forgot password link
                        ft.Container(
                            content=ft.Text(
                                "Forgot Password?",
                                color="#1565C0",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                            alignment=ft.alignment.center_right,
                            margin=ft.margin.only(top=5, bottom=20),
                        ),
                        
                        # Sign in button
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Text("SIGN IN", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Icon("arrow_forward"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#1565C0",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                            ),
                            on_click=self.sign_in,
                            width=320,
                        ),
                        
                        # Don't have an account section
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text("Don't have an account?", size=14, color="#616161"),
                                    ft.TextButton(
                                        "Sign Up",
                                        on_click=lambda e: self.page.go("/sign-up")
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            margin=ft.margin.only(top=20),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                padding=30,
                width=320,
            ),
            elevation=5,
        )

        # Add content to the container
        self.content = ft.Container(
            margin=ft.margin.only(top=50),
            content=sign_in_card,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#E3F2FD", "white"],
            ),
            expand=True,
        )
    
    def sign_in(self, e):
        self.page.go("/main")
        # You can add navigation logic here
        # self.page.go("/home")

class SignUpPage(ft.Container):
    def __init__(self, page, route):
        super().__init__()
        self.page = page
        self.route = route

        sign_up_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        ft.Text("Create your account", size=14, color="#616161"),
                        ft.Divider(height=15, color="transparent"),
                        ft.TextField(
                            label="Username",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="person",
                            hint_text="Enter your username",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        ft.TextField(
                            label="Email",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="email",
                            hint_text="Enter your email",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        ft.TextField(
                            label="Password",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="lock",
                            password=True,
                            can_reveal_password=True,
                            hint_text="Enter your password",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        ft.TextField(
                            label="Confirm Password",
                            border=ft.InputBorder.UNDERLINE,
                            prefix_icon="lock",
                            password=True,
                            can_reveal_password=True,
                            hint_text="Confirm your password",
                            focused_border_color="#1565C0",
                            focused_color="#1565C0",
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Text("SIGN UP", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Icon("arrow_forward"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#1565C0",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                            ),
                            on_click=self.sign_up,
                            width=320,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Already have an account?",
                                size=14,
                                color="#616161",
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=20),
                        ),
                        ft.Container(
                            content=ft.TextButton(
                                "Sign In",
                                on_click=lambda e: self.page.go("/sign-in")
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=5, bottom=10),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                padding=30,
                width=320,
            ),
            elevation=5,
        )

        self.content = ft.Container(
            
            content=sign_up_card,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#E3F2FD", "white"],
            ),
            expand=True,
        )

    
    def sign_up(self, e):
        print("Sign Up")







