import flet as ft
import requests

class ServerPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        
        # Server type radio buttons
        self.server_type = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="localhost", label="Localhost"),
                ft.Radio(value="custom", label="Custom URL"),
            ]),
            value="localhost",
            on_change=self.toggle_url_field
        )
        
        # Custom URL field (initially hidden)
        self.custom_url = ft.TextField(
            label="Server URL",
            value="https://",
            visible=False,
            prefix_icon="public",
            hint_text="https://your-server-url.com",
            keyboard_type="url"
        )
        
        # Save button
        self.save_button = ft.ElevatedButton(
            text="Save",
            on_click=self.save_server,
            icon="save"
        )
        
        # Main content
        self.content = ft.Column(
            [
                ft.Text("Server Configuration", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(height=24, color="transparent"),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Select Server Type", size=16, weight=ft.FontWeight.W_500),
                                self.server_type,
                                self.custom_url,
                                ft.Container(height=16),
                                ft.Row([self.save_button], alignment=ft.MainAxisAlignment.END)
                            ],
                            spacing=12,
                        ),
                        padding=20,
                    ),
                    elevation=2,
                    width=500
                )
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def toggle_url_field(self, e):
        """Show/hide the custom URL field based on selection"""
        self.custom_url.visible = (self.server_type.value == "custom")
        self.update()
    
    def save_server(self, e):
        """Handle server configuration save"""
        if self.server_type.value == "localhost":
            server_url = "http://localhost:8000"
        else:
            server_url = self.custom_url.value.strip()
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"https://{server_url}"
        
        #Save server url to client storage
        self.page.client_storage.set("server_url", server_url)
        
        self.page.go("/main")