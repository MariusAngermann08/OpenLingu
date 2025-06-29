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
            keyboard_type="url",
            on_change=self._validate_url,
            border_color="#e0e0e0",
            focused_border_color="#1a73e8"
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
    
    def _validate_url(self, e=None):
        """Validate the URL format"""
        if self.server_type.value == "custom":
            url = self.custom_url.value.strip()
            if url and not (url.startswith(('http://', 'https://')) or url == 'https://'):
                self.custom_url.error_text = "Please enter a valid URL starting with http:// or https://"
                self.custom_url.update()
                return False
            else:
                self.custom_url.error_text = ""
                self.custom_url.update()
                return True
        return True

    def save_server(self, e):
        """Handle server configuration save"""
        # Validate URL first
        if self.server_type.value == "custom" and not self._validate_url():
            return
            
        # Disable save button during verification
        self.save_button.disabled = True
        self.save_button.text = "Verifying..."
        self.save_button.icon = "autorenew"
        self.save_button.icon_color = "#1a73e8"
        
        # Show loading indicator
        if not hasattr(self, 'progress_ring'):
            self.progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=2, value=0.5, color="#1a73e8")
            self.save_button.content = ft.Row(
                [self.progress_ring, ft.Text("Verifying...")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            )
        
        # Create or update message control
        if not hasattr(self, 'message'):
            self.message = ft.Container(
                content=ft.Row([], spacing=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=4,
                visible=False
            )
            # Add it to the content if not already there
            if self.message not in self.content.controls:
                self.content.controls.append(self.message)
        else:
            # Hide any existing message
            self.message.visible = False
        
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
                        self._show_success("Server verified successfully!")
                        # Add a small delay before navigating to show success message
                        import time
                        time.sleep(0.5)
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
    
    def _show_message(self, message, is_error=True):
        """Show a message in the UI with appropriate styling"""
        if not hasattr(self, 'message'):
            return
            
        color = "#e53935" if is_error else "#388e3c"
        icon = "error_outline" if is_error else "check_circle_outline"
        
        self.message.content = ft.Row(
            [
                ft.Icon(icon, color=color, size=18),
                ft.Text(message, color=color, size=14, weight=ft.FontWeight.W_500)
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.message.bgcolor = "#ffebee" if is_error else "#e8f5e9"
        self.message.visible = True
        
        if self.page is not None:
            self.page.update()
    
    def _show_error(self, message):
        """Show an error message in the UI"""
        self._show_message(message, is_error=True)
    
    def _show_success(self, message):
        """Show a success message in the UI"""
        self._show_message(message, is_error=False)
    
    def _reset_save_button(self):
        """Reset the save button state"""
        if hasattr(self, 'save_button'):
            self.save_button.disabled = False
            self.save_button.text = "Save"
            self.save_button.icon = "save"
            self.save_button.icon_color = None
            if hasattr(self, 'progress_ring'):
                self.save_button.content = None  # Remove progress ring
            self.page.update()