import flet as ft
import requests
import threading

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
        # Disable save button during verification
        self.save_button.disabled = True
        self.save_button.text = "Verifying..."
        
        # Create or update error message control
        if not hasattr(self, 'message'):
            self.message = ft.Text("", color="#e53935")
            # Add it to the content if not already there
            if self.message not in self.content.controls:
                self.content.controls.append(self.message)
        else:
            # Clear any existing error
            self.message.value = ""
            
        self.update()
        
        if self.server_type.value == "localhost":
            server_url = "http://localhost:8000"
        else:
            server_url = self.custom_url.value.strip()
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"https://{server_url}"
        
        # Start verification in a separate thread
        threading.Thread(
            target=self.verify_server,
            args=(server_url,),
            daemon=True
        ).start()
    
    def verify_server(self, server_url):
        """Verify if the server is a valid OpenLingu server"""
        try:
            # Make a request to the server to verify it's an OpenLingu server
            response = requests.get(server_url.rstrip('/'), timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and data.get('msg') == 'OpenLingu':
                        # Server is valid, save and navigate to login
                        self.page.client_storage.set("server_url", server_url)
                        self.page.run_task(self._navigate_to_login)
                        return
                    else:
                        # Server responded but doesn't have the expected format
                        self._show_error("This server is not an OpenLingu server")
                except ValueError:
                    # Invalid JSON response
                    self._show_error("This server is not an OpenLingu server (invalid response format)")
            else:
                # Server responded with an error status code
                self._show_error(f"Server returned error: {response.status_code}")
            
        except requests.exceptions.Timeout:
            self._show_error("Connection timed out. Could not connect to the server.")
        except requests.exceptions.ConnectionError:
            self._show_error("Could not connect to the server. Please check the URL and try again.")
        except requests.exceptions.RequestException as e:
            self._show_error(f"Connection error: {str(e)}")
        except Exception as e:
            self._show_error(f"An unexpected error occurred: {str(e)}")
        finally:
            # Re-enable the save button
            self._reset_save_button()
    
    async def _navigate_to_login(self):
        """Navigate to login page"""
        self.page.go("/login")
    
    def _show_error(self, message):
        """Show error message in the UI, replacing any existing message"""
        if hasattr(self, 'message'):
            self.message.value = message
            self.message.color = "#e53935"
            if self.page is not None:
                self.page.update()
    
    def _reset_save_button(self):
        """Reset the save button state"""
        if hasattr(self, 'save_button'):
            self.save_button.disabled = False
            self.save_button.text = "Save"
            self.page.update()