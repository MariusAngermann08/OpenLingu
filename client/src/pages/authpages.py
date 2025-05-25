import flet as ft
import requests

async def save_token(page, token):
    await page.client_storage.set_async("token", token)

class SignInPage(ft.Container):
    def __init__(self, page, route):
        super().__init__()
        self.page = page
        self.route = route

        self.username_field = ft.TextField(
            label="Username",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="person",
            hint_text="Enter your username",
            focused_border_color="#1565C0",
            focused_color="#1565C0"
        )
        
        # Password field with icon
        self.password_field = ft.TextField(
            label="Password",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="lock",
            password=True,
            can_reveal_password=True,
            hint_text="Enter your password",
            focused_border_color="#1565C0",
            focused_color="#1565C0"
        )

        # Create sign-in button
        self.sign_in_button = ft.ElevatedButton(
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
        )

        # Create a card for the sign-in form
        sign_in_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome Back", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        ft.Text("Sign into your OpenLingu Account", size=14, color="#616161"),
                        ft.Divider(height=25, color="transparent"),
                        
                        # Username field with icon
                        self.username_field,
                        
                        # Password field with icon
                        self.password_field,
                        
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
                        self.sign_in_button,
                        
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
    
    async def sign_in(self, e):
        # Disable the sign-in button and show loading state
        self.sign_in_button.disabled = True
        self.sign_in_button.content = ft.Row(
            [
                ft.ProgressRing(width=20, height=20, stroke_width=2, color="white"),
                ft.Text("Signing in...", size=14, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        self.page.update()

        try:
            username = self.username_field.value.strip()
            password = self.password_field.value

            if not username or not password:
                self.show_error("Please enter both username and password")
                self._reset_sign_in_button()
                return

            # Get server URL from client storage
            server_url = await self.page.client_storage.get_async("server_url")
            
            if not server_url:
                self.show_error("Server URL not configured. Please select a server first.")
                self.page.go("/server")
                self._reset_sign_in_button()
                return
                
            # Ensure the URL has a scheme
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"http://{server_url}"
            
            # Login to openlingu server with credentials to get token
            params = {
                "username": username,
                "password": password
            }
            response = requests.post(
                f"{server_url}/login",
                params=params,
                timeout=10
            )

            print("URL: ", response.url)
            print("Status Code: ", response.status_code)
            print("Response: ", response.text)
            
            if response.status_code == 200:
                # Save token to local page storage
                await save_token(self.page, response.json()["access_token"])
                self.page.go("/main")
            else:
                self.show_error("Invalid credentials")
                self._reset_sign_in_button()
                
        except requests.exceptions.RequestException as e:
            self.show_error(f"Connection error: {str(e)}")
            self._reset_sign_in_button()
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
            self._reset_sign_in_button()
    
    def _reset_sign_in_button(self):
        """Reset the sign-in button to its original state."""
        self.sign_in_button.disabled = False
        self.sign_in_button.content = ft.Row(
            [
                ft.Text("SIGN IN", size=14, weight=ft.FontWeight.BOLD),
                ft.Icon("arrow_forward"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )
        self.page.update()
            
    def show_error(self, message):
        try:
            if not self.page:
                print("Error: Page reference is None")
                return
                
            # Create a dialog
            dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(
                        "OK",
                        on_click=lambda e: self.page.close_dialog()
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Add the dialog to the page
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            
        except Exception as e:
            print(f"Error showing error dialog: {str(e)}")
            # Fallback to console log if dialog fails
            print(f"Error: {message}")
            
    def close_dialog(self):
        if self.page and hasattr(self.page, 'dialog'):
            self.page.dialog.open = False
            self.page.update()

            

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







