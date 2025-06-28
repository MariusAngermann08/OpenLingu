import flet as ft
from math import pi
import requests
import threading
import sys
import os

# Add Components directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Components.language_chooser import LanguageChooser

class LectionButton(ft.ElevatedButton):
    def __init__(self, page, language: str, lection: str, on_select):
        super().__init__()
        self.page = page
        self.language = language
        self.lection = lection
        self.on_select_callback = on_select
        self.selected = False

        self.text = lection  # Just show the lection name
        self.width = 300
        self.height = 50
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            bgcolor="#ffffff",
            color="#1a1a1a",
            overlay_color="#e3f2fd",
            shadow_color="#dadce0",
            elevation=1,
            animation_duration=200,
        )
        self.on_click = self.handle_click

    def handle_click(self, e):
        self.selected = not self.selected
        self.update_style()
        self.on_select_callback(self, self.language, self.lection, self.selected)

    def update_style(self):
        if self.selected:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                bgcolor="#e8f0fe",
                color="#1a73e8",
                overlay_color="#d2e3fc",
                side=ft.border.BorderSide(2, "#1a73e8"),
                shadow_color="#c6dafc",
                elevation=2,
                animation_duration=200,
            )
        else:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                bgcolor="#ffffff",
                color="#1a1a1a",
                overlay_color="#e3f2fd",
                shadow_color="#dadce0",
                elevation=1,
                animation_duration=200,
            )
        self.update()

class ExpandableLanguage(ft.Container):
    def __init__(self, page: ft.Page, language: str, lections: list, on_lection_select, on_delete_language=None):
        super().__init__(animate_rotation=True)
        self.page = page
        self.expanded = False
        self.language = language
        self.lections = lections
        self.on_lection_select = on_lection_select
        self.on_delete_language = on_delete_language
        self.lection_buttons = {}

        self.expand_icon = ft.Icon(
            "chevron_right",
            animate_rotation=ft.Animation(300, curve="ease"),
            color="#5f6368"
        )
        
        self.delete_button = ft.IconButton(
            "delete_outline",
            icon_color="#5f6368",
            icon_size=20,
            tooltip="Delete language",
            on_click=self._on_delete_click,
            visible=False,
            bgcolor="#f5f5f5",
        )
        
        # Show delete button on hover
        self.header_row = ft.Row(
            [
                ft.Text(language, size=20, weight=ft.FontWeight.BOLD, color="#202124"),
                ft.Container(expand=True),
                self.delete_button,
                self.expand_icon
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        self.header = ft.Container(
            content=self.header_row,
            padding=ft.padding.symmetric(vertical=14, horizontal=20),
            border_radius=12,
            bgcolor="#ffffff",
            on_hover=self._on_header_hover,
            on_click=self.toggle_expand,
            border=ft.border.all(1, "#e0e0e0"),
            shadow=ft.BoxShadow(
                blur_radius=4,
                spread_radius=1,
                color="#00000012",
                offset=ft.Offset(0, 1),
            )
        )

        self.lection_buttons_container = ft.Column(
            spacing=8,
            visible=False,
            animate_opacity=ft.Animation(200, "easeInOut"),
        )

        for i, lection in enumerate(lections):
            btn = LectionButton(
                page=page,
                language=language,
                lection=lection,
                on_select=self.on_lection_select
            )
            self.lection_buttons[lection] = btn
            self.lection_buttons_container.controls.append(btn)

        self.content = ft.Column(
            [
                self.header,
                ft.Container(
                    content=self.lection_buttons_container,
                    padding=ft.padding.only(left=20, top=8, bottom=8, right=0),
                )
            ],
            spacing=0,
        )
    def toggle_expand(self, e):
        self.expanded = not self.expanded
        self.lection_buttons_container.visible = self.expanded
        self.expand_icon.rotate = pi / 2 if self.expanded else 0
        self.update()
    
    def _on_header_hover(self, e):
        self.delete_button.visible = e.data == "true"
        self.update()
        
    def _on_delete_click(self, e):
        # Disable the button to prevent multiple clicks
        e.control.disabled = True
        e.control.icon_color = "#9e9e9e"
        self.update()
        
        # Proceed directly with deletion
        if self.on_delete_language:
            self.on_delete_language(self.language)
        
    def select_lection(self, lection_name, selected):
        if lection_name in self.lection_buttons:
            self.lection_buttons[lection_name].selected = selected
            self.lection_buttons[lection_name].update_style()

class MainMenu(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor="#f5f5f5"
        )
        self.page = page
        self.page.on_view_pop = self.on_view_pop
        self.selected_lections = set()  # Store (language, lection) tuples
        self.app_bar_actions = []
        self.languages = {}  # Will be populated from server
        self.language_sections = {}
        
        # Server info button
        self.server_url = self.page.client_storage.get("server_url") or "Not set"
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
        
        # Initialize loading overlay
        self._loading_status_text = ft.Text("", size=16, color="#5f6368")
        self.loading_overlay = ft.Container(
            expand=True,
            bgcolor="#ffffff",
            alignment=ft.alignment.center,
            content=ft.Column([
                ft.Text("Loading languages and lections...", size=20, color="#1a73e8"),
                ft.ProgressBar(width=400, color="#1a73e8", bgcolor="#e0e0e0", value=0, 
                             ref=ft.Ref[ft.ProgressBar]()),
                self._loading_status_text
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
        )
        
        # Add Language button
        self.add_language_button = ft.ElevatedButton(
            "Add Language",
            icon="add",
            on_click=lambda e: self.page.go("/add_language"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor="#1a73e8",
                color="#ffffff",
            ),
            height=48,
        )
        
        # Main content container
        self.language_sections_container = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Meine Lektionen", size=28, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        self.add_language_button
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Divider(height=24, color="transparent"),
            ],
            spacing=16,
            expand=True
        )
        
        # Create button
        self.create_button = ft.FloatingActionButton(
            icon="add",
            text="Create",
            on_click=self.on_create_click,
            bgcolor="#1a73e8",
            width=140,
            height=48,
            shape=ft.RoundedRectangleBorder(radius=24),
            disabled=True,  # Start disabled until we have languages
        )
        # Set disabled color through theme
        self.create_button.disabled = True
        
        # Main content
        self._main_content = ft.Column(
            [
                self.language_sections_container,
                ft.Container(
                    content=self.create_button,
                    alignment=ft.alignment.bottom_right,
                    padding=ft.padding.all(20),
                )
            ],
            expand=True
        )
        
        # Initially show loading overlay
        self.content = self.loading_overlay
        
        # Start fetching data in a separate thread
        threading.Thread(target=self.fetch_languages_and_lections, daemon=True).start()
    
    def fetch_languages_and_lections(self):
        server_url = self.page.client_storage.get("server_url")
        progress_bar = self.loading_overlay.content.controls[1]
        self._loading_status_text.value = "Fetching languages from server..."
        self.page.update()
        
        if not server_url:
            self._show_error("No server URL configured. Please set a server URL first.")
            return
            
        try:
            # Fetch languages
            self._update_loading_status("Fetching languages...", 0.1)
            resp = requests.get(f"{server_url.rstrip('/')}/languages")
            resp.raise_for_status()
            languages_data = resp.json()
            languages = languages_data if isinstance(languages_data, list) else languages_data.get("languages", [])
            
            if not languages:
                # Update UI to show empty state
                self._update_ui_with_languages([])
                return
                
            # Fetch lections for each language
            total_languages = len(languages)
            language_sections = []
            self.language_sections = {}
            
            for idx, lang in enumerate(languages):
                if isinstance(lang, dict):
                    lang_code = lang.get("code", str(lang))
                    lang_name = lang.get("name", lang_code)
                else:
                    lang_code = str(lang)
                    lang_name = lang_code  # Keep original case
                
                # Fetch lections for this language
                self._update_loading_status(f"Loading lections for {lang_name}...", (idx + 1) / (total_languages + 1))
                
                try:
                    lec_resp = requests.get(f"{server_url.rstrip('/')}/languages/{lang_code}/lections")
                    lec_resp.raise_for_status()
                    lections_data = lec_resp.json()
                    lections = lections_data if isinstance(lections_data, list) else lections_data.get("lections", [])
                    
                    # Store lections for this language
                    self.languages[lang_name] = []
                    for lec in lections:
                        if isinstance(lec, dict):
                            # Try to get the title, fall back to name, then to string representation
                            lection_name = lec.get("title") or lec.get("name") or str(lec)
                            self.languages[lang_name].append(lection_name)
                        else:
                            self.languages[lang_name].append(str(lec))
                    
                    # Create language section with delete handler
                    language_section = ExpandableLanguage(
                        page=self.page,
                        language=lang_name,
                        lections=self.languages[lang_name],
                        on_lection_select=self.handle_lection_select,
                        on_delete_language=self._delete_language
                    )
                    self.language_sections[lang_name] = language_section
                    language_sections.append(language_section)
                    
                except Exception as ex:
                    print(f"Error fetching lections for {lang_name}: {ex}")
            
            # Update UI with fetched data
            self._update_ui_with_languages(language_sections)
            
        except requests.RequestException as ex:
            self._show_error(f"Failed to fetch data from server: {ex}")
        except Exception as ex:
            self._show_error(f"An unexpected error occurred: {ex}")
    
    def _update_loading_status(self, message, progress):
        self._loading_status_text.value = message
        progress_bar = self.loading_overlay.content.controls[1]
        progress_bar.value = progress
        self.page.update()
    
    def _show_error(self, message):
        self.language_sections_container.controls = [
            ft.Text("Error", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=24, color="transparent"),
            ft.Text(message, color="red")
        ]
        self.content = self._main_content
        self.page.update()
    
    def _update_ui_with_languages(self, language_sections):
        # Update create button state based on whether there are any languages
        has_languages = len(language_sections) > 0
        self.create_button.disabled = not has_languages
        
        # Update button style based on disabled state
        self.create_button.bgcolor = "#1a73e8" if has_languages else "#e0e0e0"
        
        # Create empty state message if no languages
        empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon("language_off", size=48, color="#9e9e9e"),
                    ft.Text("No languages found", size=20, weight=ft.FontWeight.W_500, color="#5f6368"),
                    ft.Text("Be the first to add a language!", size=16, color="#9e9e9e"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
            padding=ft.padding.all(40),
            border_radius=12,
            bgcolor="#ffffff",
            border=ft.border.all(1, "#e0e0e0"),
            visible=not has_languages,
        )
        
        # Update the content
        self.language_sections_container.controls = [
            self.language_sections_container.controls[0],  # Keep the title row
            ft.Divider(height=24, color="transparent"),
            empty_state,
            *language_sections
        ]
        
        self.content = self._main_content
        self.page.update()
    
    def on_create_click(self, e):
        # Show language chooser dialog
        def on_language_selected(language_code):
            # Navigate to editor with selected language
            self.page.go(f"/editor?new=true&lection_name=&language={language_code}")
            
        def on_cancel():
            # Just close the dialog
            self.content = self._main_content
            self.page.update()
        
        # Create and show language chooser
        language_chooser = LanguageChooser(
            page=self.page,
            on_language_selected=on_language_selected,
            on_cancel=on_cancel
        )
        
        # Show the language chooser
        self.content = language_chooser
        self.page.update()
    
    def create_app_bar(self):
        # Create action buttons (initially hidden)
        self.edit_button = ft.IconButton(
            "edit",
            tooltip="Edit Lection",
            icon_color="white",
            on_click=self.on_edit_lection,
            visible=False
        )
        
        self.delete_button = ft.IconButton(
            "delete",
            tooltip="Delete Lection",
            icon_color="white",
            on_click=self.on_delete_lection,
            visible=False
        )
        
        self.cancel_button = ft.IconButton(
            "close",
            tooltip="Cancel",
            icon_color="white",
            on_click=self.on_cancel_selection,
            visible=False
        )
        
        # Update server button text
        self.server_button.text = f"Server: {self._get_server_display_name(self.server_url)}"
        
        self.app_bar_actions = [
            self.edit_button,
            self.delete_button,
            self.cancel_button,
            ft.Container(
                content=self.server_button,
                margin=ft.margin.only(right=8)
            ),
            ft.IconButton(
                "account_circle",
                tooltip="Profile",
                icon_color="white"
            ),
        ]
        
        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white"),
            center_title=False,
            bgcolor="#1a73e8",
            actions=self.app_bar_actions
        )
        return self.app_bar
    
    def handle_lection_select(self, button, language, lection, selected):
        lection_key = (language, lection)
        
        if selected:
            self.selected_lections.add(lection_key)
            # Deselect all other lections
            for lang, sect in self.language_sections.items():
                for lec in self.languages[lang]:
                    if (lang, lec) != lection_key:
                        sect.select_lection(lec, False)
                        self.selected_lections.discard((lang, lec))
        else:
            self.selected_lections.discard(lection_key)
        
        # Update app bar actions visibility
        has_selection = len(self.selected_lections) > 0
        self.edit_button.visible = len(self.selected_lections) == 1
        self.delete_button.visible = has_selection
        self.cancel_button.visible = has_selection
        
        if self.app_bar:
            self.app_bar.update()
    
    def on_edit_lection(self, e):
        if self.selected_lections:
            language, lection = next(iter(self.selected_lections))
            print(f"Editing {language} - {lection}")
            # Navigate to editor with new=False, lection_name, and language
            self.page.go(f"/editor?new=false&lection_name={lection}&language={language}")
    
    def on_delete_lection(self, e):
        if not self.selected_lections:
            return
            
        language, lection = next(iter(self.selected_lections))
        self._delete_lection(language, lection)
    
    def _delete_lection(self, language: str, lection: str):
        """Handle the actual deletion of a lection"""
        server_url = self.page.client_storage.get("server_url")
        auth_token = self.page.client_storage.get("auth_token")
        
        if not server_url or not auth_token:
            self._show_error("Server URL or authentication token not found. Please log in again.")
            return
        
        # Show loading overlay
        self.content = self.loading_overlay
        self._loading_status_text.value = f"Deleting {lection}..."
        self.loading_overlay.content.controls[1].value = 0.5  # Update progress bar
        self.page.update()
        
        try:
            # Use language name directly in the URL as done in the CLI
            headers = {"Authorization": f"Bearer {auth_token}"}
            url = f"{server_url.rstrip('/')}/delete_lection/{language}/{lection}"
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Successfully deleted '{lection}'"),
                bgcolor="#4caf50"
            )
            self.page.snack_bar.open = True
            
            # Refresh the lections list
            self._refresh_lections()
            
        except requests.RequestException as ex:
            error_msg = f"Failed to delete lection: {str(ex)}"
            if hasattr(ex, 'response') and ex.response is not None:
                try:
                    error_data = ex.response.json()
                    error_msg += f"\n{error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg += f"\nStatus code: {ex.response.status_code}"
            
            self._show_error(error_msg)
            self.content = self._main_content
            self.page.update()
        except Exception as ex:
            self._show_error(f"An error occurred: {str(ex)}")
            self.content = self._main_content
            self.page.update()
    
        # Removed _on_add_language_click and _add_language methods as they're now handled by AddLanguagePage
    
    def _delete_language(self, language_name: str):
        """Delete a language"""
        server_url = self.page.client_storage.get("server_url")
        auth_token = self.page.client_storage.get("auth_token")
        
        if not server_url or not auth_token:
            self._show_error("Server URL or authentication token not found. Please log in again.")
            return
            
        # Show loading overlay
        self.content = self.loading_overlay
        self._loading_status_text.value = f"Deleting {language_name}..."
        self.loading_overlay.content.controls[1].value = 0.5
        self.page.update()
        
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            url = f"{server_url.rstrip('/')}/delete_language/{language_name}"
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Successfully deleted language '{language_name}'"),
                bgcolor="#4caf50"
            )
            self.page.snack_bar.open = True
            
            # Refresh the languages list
            self._refresh_lections()
            
        except requests.RequestException as ex:
            error_msg = f"Failed to delete language: {str(ex)}"
            if hasattr(ex, 'response') and ex.response is not None:
                try:
                    error_data = ex.response.json()
                    error_msg += f"\n{error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg += f"\nStatus code: {ex.response.status_code}"
            
            self._show_error(error_msg)
            self.content = self._main_content
            self.page.update()
        except Exception as ex:
            self._show_error(f"An error occurred: {str(ex)}")
            self.content = self._main_content
            self.page.update()
    
    def _refresh_lections(self):
        """Refresh the list of languages and lections from the server"""
        self.content = self.loading_overlay
        self._loading_status_text.value = "Refreshing..."
        self.loading_overlay.content.controls[1].value = 0  # Reset progress bar
        self.page.update()
        
        # Clear current selection and fetch fresh data
        self.selected_lections.clear()
        self.languages = {}
        self.language_sections = {}
        self.language_sections_container.controls = [
            self.language_sections_container.controls[0],  # Keep the title row
            ft.Divider(height=24, color="transparent"),
        ]
        
        # Fetch fresh data in a new thread
        threading.Thread(target=self.fetch_languages_and_lections, daemon=True).start()
    
    def on_cancel_selection(self, e):
        self.clear_selection()
    
    def clear_selection(self):
        self.selected_lections.clear()
        for language, section in self.language_sections.items():
            for lection in self.languages[language]:
                section.select_lection(lection, False)
        
        # Hide action buttons
        self.edit_button.visible = False
        self.delete_button.visible = False
        self.cancel_button.visible = False
        
        if self.app_bar:
            self.app_bar.update()
    
    def _get_server_display_name(self, url):
        if not url:
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
        if hasattr(self, 'server_button'):
            self.server_button.text = f"Server: {self._get_server_display_name(self.server_url)}"
            self.page.update()