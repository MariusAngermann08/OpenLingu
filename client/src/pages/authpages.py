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
        
        # Error message text (initially hidden)
        self.error_text = ft.Text(
            "",
            color="red",
            size=12,
            visible=False,
            weight="w500"
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
                        
                        # Error message container (initially empty)
                        self.error_text,
                        
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
        # Hide any previous error message
        self.error_text.visible = False
        self.error_text.update()
        
        # Reset field borders
        self.username_field.border_color = None
        self.password_field.border_color = None
        
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
            # Update the error text and make it visible
            self.error_text.value = message
            self.error_text.visible = True
            
            # Clear any previous error state from fields
            self.username_field.border_color = None
            self.password_field.border_color = None
            
            # Add red border to fields to highlight the error
            if not self.username_field.value.strip():
                self.username_field.border_color = "red"
            if not self.password_field.value.strip():
                self.password_field.border_color = "red"
                
            self.page.update()
            
        except Exception as e:
            print(f"Error showing error message: {str(e)}")
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

        self.username_field = ft.TextField(
            label="Username",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="person",
            hint_text="Enter your username",
            focused_border_color="#1565C0",
            focused_color="#1565C0",
        )
        
        self.email_field = ft.TextField(
            label="Email",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="email",
            hint_text="Enter your email",
            focused_border_color="#1565C0",
            focused_color="#1565C0",
        )
        
        self.password_field = ft.TextField(
            label="Password",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="lock",
            password=True,
            can_reveal_password=True,
            hint_text="Enter your password",
            focused_border_color="#1565C0",
            focused_color="#1565C0",
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="lock",
            password=True,
            can_reveal_password=True,
            hint_text="Confirm your password",
            focused_border_color="#1565C0",
            focused_color="#1565C0",
        )
        
        self.sign_up_button = ft.ElevatedButton(
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
        )


        self.sign_up_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        ft.Text("Create your account", size=14, color="#616161"),
                        ft.Divider(height=15, color="transparent"),
                        self.username_field,
                        self.email_field,
                        self.password_field,
                        self.confirm_password_field,
                        self.sign_up_button,
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
            
            content=self.sign_up_card,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#E3F2FD", "white"],
            ),
            expand=True,
        )

    
    def _reset_sign_up_button(self):
        """Reset the sign-up button to its original state."""
        self.sign_up_button.disabled = False
        self.sign_up_button.content = ft.Row(
            [
                ft.Text("SIGN UP", size=14, weight=ft.FontWeight.BOLD),
                ft.Icon("arrow_forward"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )
        self.page.update()
    
    def show_error(self, message):
        """Show an error message below the form."""
        try:
            if not hasattr(self, 'error_text'):
                # Create error text if it doesn't exist
                self.error_text = ft.Text(
                    "",
                    color="red",
                    size=12,
                    visible=False,
                    weight="w500"
                )
                # Insert error text above the sign up button
                self.sign_up_card.content.controls.insert(
                    self.sign_up_card.content.controls.index(self.sign_up_button),
                    self.error_text
                )
            
            # Update error text and make it visible
            self.error_text.value = message
            self.error_text.visible = True
            self.page.update()
            
        except Exception as e:
            print(f"Error showing error message: {str(e)}")
    
    def _is_valid_email(self, email):
        """Check if the email has a valid format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def sign_up(self, e):
        # Hide any previous error message
        if hasattr(self, 'error_text') and self.error_text.visible:
            self.error_text.visible = False
        
        # Reset field borders
        self.username_field.border_color = None
        self.email_field.border_color = None
        self.password_field.border_color = None
        self.confirm_password_field.border_color = None
        
        # Get form values
        username = self.username_field.value.strip()
        email = self.email_field.value.strip()
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value
        
        # Validate form
        if not username:
            self.username_field.border_color = "red"
            self.show_error("Username is required")
            return
            
        if not email:
            self.email_field.border_color = "red"
            self.show_error("Email is required")
            return
            
        if not self._is_valid_email(email):
            self.email_field.border_color = "red"
            self.show_error("Please enter a valid email address")
            return
            
        if not password:
            self.password_field.border_color = "red"
            self.show_error("Password is required")
            return
            
        if password != confirm_password:
            self.password_field.border_color = "red"
            self.confirm_password_field.border_color = "red"
            self.show_error("Passwords do not match")
            return
        
        # Disable the sign-up button and show loading state
        self.sign_up_button.disabled = True
        self.sign_up_button.content = ft.Row(
            [
                ft.ProgressRing(width=20, height=20, stroke_width=2, color="white"),
                ft.Text("Creating account...", size=14, weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        self.page.update()

        try:
            # Get server URL from client storage
            server_url = await self.page.client_storage.get_async("server_url")
            
            if not server_url:
                self.show_error("Server URL not configured. Please select a server first.")
                self._reset_sign_up_button()
                self.page.go("/server")
                return
                
            # Ensure the URL has a scheme
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"http://{server_url}"
            
            # Make the API request
            response = requests.post(
                f"{server_url}/register",
                params={
                    "username": username,
                    "email": email,
                    "password": password
                },
                timeout=10
            )

            print("Signup URL: ", response.url)
            print("Status Code: ", response.status_code)
            print("Response: ", response.text)
            
            if response.status_code == 200:
                # Registration successful, redirect to sign in
                self.show_error("Registration successful! Please sign in.")
                self._reset_sign_up_button()
                # Redirect to sign in after a short delay
                import asyncio
                await asyncio.sleep(2)
                self.page.go("/sign-in")
            else:
                # Try to get error details from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Registration failed")
                except:
                    error_msg = "Registration failed. Please try again."
                
                self.show_error(error_msg)
                self._reset_sign_up_button()
                
        except requests.exceptions.RequestException as e:
            self.show_error(f"Connection error: {str(e)}")
            self._reset_sign_up_button()
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
            self._reset_sign_up_button()







