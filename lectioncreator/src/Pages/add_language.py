import flet as ft
import requests
import asyncio

class AddLanguagePage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        
        # UI Elements
        self.language_input = ft.TextField(
            label="Language Name",
            hint_text="e.g., german, spanish, french",
            autofocus=True,
            border_radius=12,
            border_color="#e0e0e0",
            focused_border_color="#1a73e8",
            on_submit=self._add_language,
        )
        
        self.submit_button = ft.ElevatedButton(
            "Add Language",
            on_click=lambda e: self.page.run_task(self._add_language, e),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=32, vertical=16),
                bgcolor="#1a73e8",
            ),
            height=48,
        )
        
        self.error_text = ft.Text(
            "",
            color="red",
            visible=False,
        )
        
        self.progress_ring = ft.ProgressRing(
            width=24,
            height=24,
            stroke_width=2,
            visible=False,
            color="#1a73e8",
        )
        
        # Layout
        self.content = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Add New Language", size=24, weight=ft.FontWeight.BOLD),
                        ft.Divider(height=24),
                        self.language_input,
                        ft.Container(height=16),
                        ft.Row(
                            [
                                self.progress_ring,
                                self.error_text,
                                ft.Container(expand=True),
                                ft.TextButton(
                                    "Cancel",
                                    on_click=lambda _: self.page.go("/main"),
                                    style=ft.ButtonStyle(
                                        padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                    ),
                                ),
                                self.submit_button,
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.padding.all(32),
                border_radius=12,
                bgcolor="#ffffff",
                width=500,
            ),
            elevation=2,
        )
    
    async def _add_language(self, e):
        language_name = self.language_input.value.strip()
        if not language_name:
            self._show_error("Please enter a language name")
            return
            
        # Show loading state
        self.progress_ring.visible = True
        self.submit_button.disabled = True
        self.error_text.visible = False
        await self._update_ui()
        
        try:
            # Get values from client storage asynchronously
            server_url = await self.page.client_storage.get_async("server_url")
            auth_token = await self.page.client_storage.get_async("auth_token")
            username = await self.page.client_storage.get_async("username")
            
            if not server_url or not auth_token:
                raise Exception("Server URL or authentication token not found")
                
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Include the username in the request body as per API spec
            response = requests.post(
                f"{server_url.rstrip('/')}/add_language/{language_name}",
                headers=headers,
                json={"username": username or ""},
                timeout=10  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            
            # Return to main page on success
            self.page.go("/main")
            
        except requests.Timeout:
            self._show_error("Request timed out. Please check your connection and try again.")
        except requests.RequestException as ex:
            error_msg = f"Failed to add language: {str(ex)}"
            if hasattr(ex, 'response') and ex.response is not None:
                try:
                    error_data = ex.response.json()
                    error_msg = f"{error_msg}\n{error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"{error_msg}\nStatus code: {ex.response.status_code}"
            self._show_error(error_msg)
            
        except Exception as ex:
            self._show_error(f"An error occurred: {str(ex)}")
            
        finally:
            self.progress_ring.visible = False
            self.submit_button.disabled = False
            await self._update_ui()
    
    def _show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        if self.page:
            self.page.run_task(self._update_ui)
    
    async def _update_ui(self):
        if self.page:
            self.page.update()
            # Small delay to ensure UI updates are processed
            await asyncio.sleep(0.1)
    
    def update(self):
        if self.page:
            self.page.update()
