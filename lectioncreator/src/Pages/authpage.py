import flet as ft
import requests
import threading

class LoginPage(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.bgcolor = "#eceff1"  # Soft light background
        
        # Get server URL from client storage
        self.server_url = self.page.client_storage.get("server_url") or "Not set"
        
        super().__init__(
            expand=True,
            padding=20,
            alignment=ft.alignment.center,
        )

        # Create app bar with server button
        self.server_button = ft.ElevatedButton(
            text=f"Server: {self._get_server_display_name(self.server_url)}",
            icon="dns",
            on_click=self.go_to_server_page,
            style=ft.ButtonStyle(
                color="#1a73e8",
                bgcolor="#e8f0fe",
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            scale=0.9
        )
        
        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white"),
            center_title=False,
            bgcolor="#1a73e8",
            actions=[
                ft.Container(
                    content=self.server_button,
                    margin=ft.margin.only(right=8)
                )
            ]
        )

        self.username = ft.TextField(
            label="Username",
            width=320,
            border_radius=10,
            border_color="#cfd8dc",
            focused_border_color="#2196f3",
            bgcolor="#f9f9f9",
            autofocus=True,
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
            on_submit=self.login_click,
        )

        self.message = ft.Text(
            "",
            color="#e53935",
            size=12,
            weight=ft.FontWeight.W_500,
        )
        
        self.login_button = ft.ElevatedButton(
            text="Login as Contributor",
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
        
        # Loading indicator
        self.loading = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Authenticating...")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            visible=False,
            alignment=ft.alignment.center,
            bgcolor="#80000000",
            border_radius=10,
        )

        self.content = ft.Container(
            content=ft.Stack(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "Welcome Back 👋",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color="#263238",
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "Login as a contributor",
                                size=14,
                                color="#607d8b",
                                text_align=ft.TextAlign.CENTER
                            ),
                            self.username,
                            self.password,
                            self.login_button,
                            self.message
                        ],
                        spacing=18,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    self.loading
                ]
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
    
    def _get_server_display_name(self, url):
        if not url or url == "Not set":
            return "Not set"
        # Remove protocol and trailing slashes
        clean_url = url.replace('https://', '').replace('http://', '').rstrip('/')
        # Truncate if too long
        return clean_url[:20] + '...' if len(clean_url) > 23 else clean_url
    
    def go_to_server_page(self, e):
        self.page.go("/server")
    
    def on_view_pop(self, e):
        # Update server URL when returning to this page
        self.server_url = self.page.client_storage.get("server_url") or "Not set"
        self.server_button.text = f"Server: {self._get_server_display_name(self.server_url)}"
        self.page.update()
    
    def login_click(self, e):
        username = self.username.value.strip()
        password = self.password.value
        
        if not username or not password:
            self.message.value = "Please enter both username and password"
            self.message.color = "#e53935"
            self.message.update()
            return
            
        if self.server_url == "Not set":
            self.message.value = "Please set a server URL first"
            self.message.color = "#e53935"
            self.message.update()
            return
        
        # Show loading indicator
        self.loading.visible = True
        self.page.update()
        
        # Start authentication in a separate thread
        threading.Thread(target=self.authenticate, args=(username, password), daemon=True).start()
    
    async def _navigate_to_main(self):
        """Navigate to the main page"""
        self.page.go("/main")
    
    def authenticate(self, username, password):
        try:
            # Get the server URL from client storage
            server_url = self.page.client_storage.get("server_url")
            if not server_url:
                self._update_ui_with_error("Server URL not set")
                return
                
            # Call the login endpoint
            params = {"username": username, "password": password}
            response = requests.get(f"{server_url}/login_contributer", params=params)
            
            if response.status_code == 200:
                # Save the token and username
                token_data = response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    self.page.client_storage.set("auth_token", access_token)
                    self.page.client_storage.set("username", username)
                    # Schedule navigation on the main thread
                    self.page.run_task(self._navigate_to_main)
                else:
                    self._update_ui_with_error("Invalid response from server")
            else:
                error_msg = "Invalid credentials"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
                self._update_ui_with_error(error_msg)
                
        except requests.exceptions.RequestException as e:
            self._update_ui_with_error(f"Connection error: {str(e)}")
        except Exception as e:
            self._update_ui_with_error(f"An error occurred: {str(e)}")
    
    async def _update_ui_async(self, message):
        """Update UI with error message and hide loading indicator"""
        if hasattr(self, 'message') and self.message is not None:
            self.message.value = message
            self.message.color = "#e53935"
            if hasattr(self, 'loading') and self.loading is not None:
                self.loading.visible = False
            if hasattr(self, 'page') and self.page is not None:
                await self.page.update()
    
    def _update_ui_with_error(self, message):
        """Wrapper to run UI updates on the main thread"""
        if hasattr(self, 'page') and self.page is not None:
            self.page.run_task(self._update_ui_async, message)
    
    def show_error(self, message):
        """Deprecated: Use _update_ui_with_error instead"""
        self._update_ui_with_error(message)