import flet as ft
import requests

class LanguageChooser(ft.Container):
    def __init__(self, page, mainpage):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.mainpage = mainpage
        self.languages = []
        self.selected_language = None
        
        # Create UI elements
        self.progress_ring = ft.ProgressRing()
        self.error_text = ft.Text("", color="red")
        self.language_list = ft.ListView(
            spacing=10,
            width=300,
            height=400,
            auto_scroll=True,
        )
        
        # Create select language button
        self.select_language_button = ft.ElevatedButton(
            content=ft.Text("SELECT LANGUAGE", size=14, weight=ft.FontWeight.BOLD),
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#1565C0",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            on_click=self.select_language,
            width=320,
            disabled=True
        )
        
        # Add back button
        self.back_button = ft.ElevatedButton(
            "BACK",
            on_click=lambda e: page.go("/main"),
            style=ft.ButtonStyle(
                color="white",
                bgcolor="#757575",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            width=320,
        )
        
        # Set up the UI
        self.content = ft.Column(
            [
                ft.Text("Select a Language", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                self.progress_ring,
                self.error_text,
                self.language_list,
                ft.Container(height=20),
                self.select_language_button,
                ft.Container(height=10),
                self.back_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        # Add content to page first
        self.page.add(self)
        self.page.update()
        
        # Then load languages
        self.load_languages()
    
    def load_languages(self):
        # Show loading
        self.progress_ring.visible = True
        self.error_text.value = ""
        self.page.update()
        
        try:
            # Get server URL
            self.server_url = self.page.client_storage.get("server_url")
            if not self.server_url:
                raise Exception("Server URL not set")
                
            # Make request
            response = requests.get(f"{self.server_url}/languages", timeout=10)
            response.raise_for_status()
            self.languages = response.json()
            
            # Update UI with languages
            if hasattr(self, 'language_list') and self.language_list:
                current_lang = getattr(self.mainpage, 'current_language', None)
                self.language_list.controls = [
                    ft.ListTile(
                        title=ft.Text(
                            f"{lang} ✓" if lang == current_lang else lang,
                            weight="bold" if lang == current_lang else None
                        ),
                        on_click=lambda e, lang=lang: self.on_language_selected(lang)
                    )
                    for lang in self.languages
                ]
            
        except requests.RequestException as e:
            self.error_text.value = f"Network error: {str(e)}"
            self.languages = []
        except Exception as e:
            self.error_text.value = f"Error: {str(e)}"
            self.languages = []
        
        # Update UI
        self.progress_ring.visible = False
        self.select_language_button.disabled = not bool(self.languages)
        self.page.update()
    
    def on_language_selected(self, language):
        self.selected_language = language
        # Update UI to show selected language
        if hasattr(self, 'language_list') and self.language_list:
            for i, lang in enumerate(self.languages):
                tile = self.language_list.controls[i]
                tile.title = ft.Text(
                    f"{lang} ✓" if lang == language else lang,
                    weight="bold" if lang == language else None
                )
        self.page.update()
    
    def select_language(self, e):
        if not self.selected_language:
            return
            
        # Update main page's language
        self.mainpage.current_language = self.selected_language
        
        # Update the language button in the main page
        if hasattr(self.mainpage, 'language_button') and self.mainpage.language_button:
            self.mainpage.language_button.content.text = self.selected_language
            
            # Force update the main page's app bar
            if hasattr(self.mainpage, 'page') and self.mainpage.page:
                # Update the current view's app bar
                if self.mainpage.page.views and len(self.mainpage.page.views) > 0:
                    current_view = self.mainpage.page.views[-1]
                    if hasattr(self.mainpage, 'create_app_bar'):
                        current_view.appbar = self.mainpage.create_app_bar(self.mainpage.appbar_title)
        
        # Navigate back to main page
        self.page.go("/main")
