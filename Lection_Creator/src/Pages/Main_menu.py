import flet as ft
from math import pi
import requests
import threading

class LectionButton(ft.ElevatedButton):
    def __init__(self, page, language: str, lection: str, index: int, on_select):
        super().__init__()
        self.page = page
        self.language = language
        self.lection = lection
        self.index = index
        self.on_select_callback = on_select
        self.selected = False

        self.text = f"Lektion {index + 1}: {lection}"
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
    def __init__(self, page: ft.Page, language: str, lections: list, on_lection_select):
        super().__init__(animate_rotation=True)
        self.page = page
        self.expanded = False
        self.language = language
        self.lections = lections
        self.on_lection_select = on_lection_select
        self.lection_buttons = {}

        self.expand_icon = ft.Icon(
            "chevron_right",
            animate_rotation=ft.Animation(300, curve="ease"),
            color="#5f6368"
        )


        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(language, size=20, weight=ft.FontWeight.BOLD, color="#202124"),
                    ft.Container(expand=True),
                    self.expand_icon
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=20),
            border_radius=12,
            bgcolor="#ffffff",
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
                index=i,
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
        
        # Main content container
        self.language_sections_container = ft.Column(
            [
                ft.Text("Meine Lektionen", size=28, weight=ft.FontWeight.BOLD),
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
        )
        
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
                self._show_error("No languages found on the server.")
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
                    lang_name = lang_code.capitalize()
                
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
                            self.languages[lang_name].append(lec.get("title", str(lec)))
                        else:
                            self.languages[lang_name].append(str(lec))
                    
                    # Create language section
                    language_section = ExpandableLanguage(
                        page=self.page,
                        language=lang_name,
                        lections=self.languages[lang_name],
                        on_lection_select=self.handle_lection_select
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
        # Clear existing content but keep the title
        self.language_sections_container.controls = [
            self.language_sections_container.controls[0],  # Keep the title
            ft.Divider(height=24, color="transparent"),
            *language_sections
        ]
        self.content = self._main_content
        self.page.update()
    
    def on_create_click(self, e):
        # Handle create button click
        pass
    
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
            # TODO: Implement edit functionality
    
    def on_delete_lection(self, e):
        if self.selected_lections:
            language, lection = next(iter(self.selected_lections))
            print(f"Deleting {language} - {lection}")
            # TODO: Implement delete functionality
            # After deletion, clear selection
            self.clear_selection()
    
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