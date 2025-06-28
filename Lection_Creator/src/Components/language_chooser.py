import flet as ft
import requests
from typing import Callable, Optional

class LanguageChooser(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_language_selected: Callable[[str], None],
        on_cancel: Optional[Callable[[], None]] = None
    ):
        super().__init__()
        self.page = page
        self.on_language_selected = on_language_selected
        self.on_cancel = on_cancel
        self.selected_language = None
        self.languages = []

        # UI Components
        self.title = ft.Text(
            "Select Language",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="#1a1c1e"
        )
        
        self.subtitle = ft.Text(
            "Choose the language for your new lection",
            size=16,
            color="#5f6368",
            text_align="center"
        )
        
        self.language_dropdown = ft.Dropdown(
            options=[],
            hint_text="Select language",
            border_color="#dadce0",
            border_radius=8,
            filled=True,
            bgcolor="#f8f9fa",
            text_size=16,
            content_padding=16,
            on_change=self.on_language_select,
            width=300,
            autofocus=True
        )
        
        self.select_button = ft.ElevatedButton(
            text="Continue",
            bgcolor="#1a73e8",
            color="white",
            on_click=self.on_select_click,
            disabled=True,
            width=140,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        
        self.cancel_button = ft.TextButton(
            text="Cancel",
            on_click=self.on_cancel_click,
            style=ft.ButtonStyle(
                padding=20,
            )
        )
        
        # Main content
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=20),
                    self.title,
                    ft.Container(height=8),
                    self.subtitle,
                    ft.Container(height=32),
                    self.language_dropdown,
                    ft.Container(height=32),
                    ft.Row(
                        [self.select_button],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    self.cancel_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=40,
            bgcolor="#ffffff",
            border_radius=16,
            width=500,
        )
        
        # Center the dialog
        self.alignment = ft.alignment.center
        self.margin = 40
        self.bgcolor = "#00000080"
        
        # Load languages in background
        self._load_languages()
    
    def _load_languages(self):
        """Load available languages from the server"""
        try:
            server_url = self.page.client_storage.get("server_url")
            if not server_url:
                self._show_error("Server URL not configured")
                return
                
            response = requests.get(f"{server_url.rstrip('/')}/languages", timeout=5)
            if response.status_code == 200:
                languages = response.json()
                self.languages = [{"code": lang, "name": lang} for lang in languages]
                
                # Update dropdown options
                self.language_dropdown.options = [
                    ft.dropdown.Option(
                        text=lang["name"],
                        key=lang["code"]
                    )
                    for lang in self.languages
                ]
                
                # Select first language by default if available
                if self.languages:
                    self.language_dropdown.value = self.languages[0]["code"]
                    self.selected_language = self.languages[0]["code"]
                    self.select_button.disabled = False
                
                self.page.update()
            else:
                self._show_error("Failed to load languages from server")
                
        except requests.exceptions.RequestException as e:
            self._show_error(f"Error connecting to server: {str(e)}")
        except Exception as e:
            self._show_error(f"An error occurred: {str(e)}")
    
    def _show_error(self, message):
        """Show an error message"""
        self.subtitle.value = message
        self.subtitle.color = "#f44336"
        self.page.update()
    
    def on_language_select(self, e):
        self.selected_language = self.language_dropdown.value
        self.select_button.disabled = not bool(self.selected_language)
        self.page.update()
    
    def on_select_click(self, e):
        if self.selected_language:
            self.on_language_selected(self.selected_language)
    
    def on_cancel_click(self, e):
        if self.on_cancel:
            self.on_cancel()
        else:
            self.page.views.pop()
            self.page.update()
