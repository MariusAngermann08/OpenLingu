import flet as ft
import requests

class LanguageChooser(ft.Container):
    def __init__(self, page, mainpage):
        super().__init__()
        self.page = page
        self.mainpage = mainpage
        self.selected_language = None
        
        #Setup empty language list
        self.languages = []

        #Get server url from client storage
        self.server_url = self.page.client_storage.get("server_url")
        if not self.server_url:
            # Language options
            self.languages = [
                {"code": "default", "name": "Default"},
            ]
        else:
            #Use server url to get languages from server
            #Returns an array of languages
            response = requests.get(f"{self.server_url}/languages", timeout=5)
            if not response.status_code == 200:
                self.languages = [
                    {"code": "default", "name": "Default"},
                ]
            else:
                # Get languages list from JSON response
                languages_list = response.json()
                self.languages.clear()
                # Use language name as both code and name
                for lang in languages_list:
                    self.languages.append({"code": lang, "name": lang})

            


        
        
        # Create dropdown options
        self.dropdown_options = [
            ft.dropdown.Option(lang["code"], text=lang["name"])
            for lang in self.languages
        ]
        
        # UI Components
        self.title = ft.Text(
            "Choose a language",
            size=28,
            weight="w700",
            color="#1a1c1e"
        )
        
        self.subtitle = ft.Text(
            "Select your preferred language from the list below",
            size=16,
            color="#5f6368",
            text_align="center"
        )
        
        self.language_dropdown = ft.Dropdown(
            options=self.dropdown_options,
            value="en",  # Set English as default
            hint_text="Select language",
            border_color="#dadce0",
            border_radius=8,
            filled=True,
            bgcolor="#f8f9fa",
            text_size=16,
            content_padding=16,
            on_change=self.on_language_select,
            width=300
        )
        self.selected_language = "en"  # Set initial selected language
        
        self.select_button = ft.ElevatedButton(
            text="Select",
            bgcolor="#1a73e8",
            color="white",
            on_click=self.on_select_click,
            disabled=False,
            width=140,
            height=48,
            style=ft.ButtonStyle(
                shape={"": ft.RoundedRectangleBorder(radius=8)},
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
                    ft.Container(height=40),
                    self.language_dropdown,
                    ft.Container(height=40),
                    self.select_button,
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
        self.bgcolor = "#f5f5f5"
        
    def on_language_select(self, e):
        self.selected_language = self.language_dropdown.value
        self.select_button.disabled = False
        self.select_button.update()
    
    # When a language is selected
    async def on_select_click(self, e):
        print(f"[DEBUG] Selected language: {self.selected_language}")
        if not self.selected_language:
            print("[DEBUG] No language selected")
            return
            
        try:
            
            # Save the selected language to client storage
            await self.page.client_storage.set_async("selected_language", self.selected_language)
            print(f"[DEBUG] Saved language to storage: {self.selected_language}")
            
            # Update the current page if mainpage is available
            if hasattr(self, 'mainpage') and self.mainpage:
                print(f"[DEBUG] Calling update_language with: {self.selected_language}")
                # Call the async method and wait for it to complete
                await self.mainpage.update_language(self.selected_language)
                print("[DEBUG] Language update completed")
                
            # Navigate back to main page
            self.page.go("/main")
            
        except Exception as ex:
            print(f"[ERROR] Error in on_select_click: {str(ex)}")
            # Still try to navigate even if there was an error
            self.page.go("/main")
        
    def on_cancel_click(self, e):
        # Placeholder for cancel action
        self.page.go("/main")