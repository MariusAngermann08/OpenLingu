import asyncio
import flet as ft
import requests

# Handle imports for both direct execution and module import
try:
    # When running as a module (through run.py)
    from pages.mainpages.learningpage import LearningPage
    from pages.mainpages.dailytaskspage import DailyTasksPage
    from pages.mainpages.vocabs import VocabsPage
    from pages.mainpages.dictionary import DictionaryPage
    from pages.mainpages.account import AccountPage
    from pages.mainpages.settings import SettingsPage
    from pages.Languagetrees.spanish_main import SpanishMainPage
    from pages.Languagetrees.english_main import EnglishMainPage
except ImportError:
    # When running directly with flet run
    from mainpages.learningpage import LearningPage
    from mainpages.dailytaskspage import DailyTasksPage
    from mainpages.vocabs import VocabsPage
    from mainpages.dictionary import DictionaryPage
    from mainpages.account import AccountPage
    from mainpages.settings import SettingsPage
    from Languagetrees.spanish_main import SpanishMainPage
    from Languagetrees.english_main import EnglishMainPage

#Function to remove the access token from the client storage
def remove_access_token(page):
    page.client_storage.remove("access_token")

class MainPage(ft.Container):
    def __init__(self, page, route):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.route = route
        self.appbar_title = "Daily Tasks"
        self.last_page = []
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Initialize language from client storage or default to English
        self.current_language = "English"  # Default value
        self.native_language_code = "en"   # Default code

        # Create language button reference for hover effect (for learning language)
        self.language_btn = ft.ElevatedButton(
            text=self.current_language,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                bgcolor="#1a73e8",
                color="white"
            ),
            on_click=lambda e: self.page.go("/languages"),
        )

        # Load saved native language asynchronously
        async def load_native_language():
            try:
                lang_code = await self.page.client_storage.get_async("native_language")
                if lang_code:
                    self.native_language_code = lang_code
                    # Map code to display name
                    self.current_language = self.get_language_name(lang_code)
                    print(f"[DEBUG] Loaded native language from storage: {self.current_language} ({lang_code})")
            except Exception as e:
                print(f"[ERROR] Error loading native language: {e}")
        # Run the async function in the event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(load_native_language)
        else:
            asyncio.create_task(load_native_language())

        # Helper to get display name from language code
        def get_language_name(self, code):
            lang_map = {"en": "English", "de": "German", "es": "Spanish", "fr": "French"}
            return lang_map.get(code, code)
        self.get_language_name = get_language_name.__get__(self)

        # Helper to set native language
        def set_native_language(self, name, code):
            self.current_language = name
            self.native_language_code = code
            self.page.client_storage.set("native_language", code)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Native language set to {name}"))
            self.page.snack_bar.open = True
            self.page.update()
        self.set_native_language = set_native_language.__get__(self)

        # Download Lection Dialog opener and dynamic logic
        def open_download_lection_dialog(self, e=None):
            server_url = self.page.client_storage.get("server_url")
            if not server_url:
                self.download_lection_dialog.content.controls[0].value = "No server URL set in client storage."
                self.download_lection_dialog.content.controls[1].controls.clear()
                self.page.dialog = self.download_lection_dialog
                self.download_lection_dialog.open = True
                self.page.update()
                return
            try:
                resp = requests.get(f"{server_url.rstrip('/')}/languages")
                resp.raise_for_status()
                languages = resp.json() if isinstance(resp.json(), list) else resp.json().get("languages", [])
            except Exception as ex:
                self.download_lection_dialog.content.controls[0].value = f"Failed to fetch languages: {ex}"
                self.download_lection_dialog.content.controls[1].controls.clear()
                self.page.dialog = self.download_lection_dialog
                self.download_lection_dialog.open = True
                self.page.update()
                return
            # Populate the ListView with ExpansionTiles for each language
            tiles = []
            for lang in languages:
                lang_code = lang.get("code") if isinstance(lang, dict) else lang
                lang_name = lang.get("name") if isinstance(lang, dict) else lang_code
                def make_expansion_tile(lang_code=lang_code, lang_name=lang_name):
                    # Title row with tap handler to load lections if not loaded
                    def on_title_tap(e):
                        self.fetch_and_show_lections(lang_code)
                    return ft.ExpansionTile(
                        title=ft.GestureDetector(
                            content=ft.Text(f"{lang_name} ({lang_code})"),
                            on_tap=on_title_tap
                        ),
                        controls=[]
                    )
                tiles.append(make_expansion_tile())
            self.download_lection_dialog.content.controls[0].value = "Select a language to expand and see available lections."
            self.download_lection_dialog.content.controls[1].controls = tiles
            # Robust dialog opening
            self.download_lection_dialog.open = False
            self.page.dialog = self.download_lection_dialog
            self.download_lection_dialog.open = True
            self.page.update()
        self.open_download_lection_dialog = open_download_lection_dialog.__get__(self)

        # Fetch lections for a language and update the respective ExpansionTile
        def fetch_and_show_lections(self, lang_code):
            server_url = self.page.client_storage.get("server_url")
            try:
                resp = requests.get(f"{server_url.rstrip('/')}/lections?language={lang_code}")
                resp.raise_for_status()
                lections = resp.json() if isinstance(resp.json(), list) else resp.json().get("lections", [])
            except Exception as ex:
                lections = [ft.Text(f"Failed to fetch lections: {ex}")]
            # Find the ExpansionTile for this lang_code
            for tile in self.download_lection_dialog.content.controls[1].controls:
                if hasattr(tile, 'title') and lang_code in tile.title.value:
                    # Populate with lection items
                    tile.controls.clear()
                    if isinstance(lections, list):
                        for lec in lections:
                            lec_title = lec.get("title") if isinstance(lec, dict) else lec
                            tile.controls.append(
                                ft.Row([
                                    ft.Text(lec_title),
                                    ft.IconButton(icon="download", tooltip="Download", on_click=None)  # Download action to be implemented
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                            )
                    else:
                        tile.controls.append(ft.Text("No lections found."))
            self.page.update()
        self.fetch_and_show_lections = fetch_and_show_lections.__get__(self)

        # Dialog close handler (must be defined before dialog assignment)
        def close_download_lection_dialog(self, e=None):
            self.download_lection_dialog.open = False
            self.page.update()
        self.close_download_lection_dialog = close_download_lection_dialog.__get__(self)

        # Download Lection Dialog (scaffold)
        self.download_lection_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Download Lections from Server"),
            content=ft.Column([
                ft.Text("Select a language to expand and see available lections."),
                ft.ListView([], expand=True, spacing=8, padding=8, auto_scroll=False, height=300),  # Will be populated dynamically
            ]),
            actions=[
                ft.TextButton("Close", on_click=self.close_download_lection_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Sign out button state and reference
        self.sign_out_button = None
        self.is_signing_out = False
        
        # Track if we are on a nested Page
        self.not_on_home = False

        #Create Server Dialog
        self.server_info_dialog = ft.AlertDialog(
            title=ft.Text("Server Information"),
            content=ft.Text(f"Server URL: {self.page.client_storage.get('server_url')}", selectable=True),
            alignment=ft.alignment.center,
            on_dismiss=lambda e: print("Dialog dismissed!"),
            title_padding=ft.padding.all(25)
        )  

        
        # Create the NavigationDrawer
        self.drawer = ft.NavigationDrawer(
            controls=[
                # Header
                ft.Container(
                    padding=ft.padding.all(16),
                    content=ft.Column(
                        [
                            ft.Text("OpenLingu", size=20, weight="bold"),
                            ft.Text("Language Learning", size=12, color="#757575"),
                        ],
                        spacing=4,
                        tight=True,
                    )
                ),
                ft.Divider(height=1),
                
                # Main Learning Sections
                ft.NavigationDrawerDestination(
                    label="Daily Tasks",
                    icon="check_circle_outline",
                    selected_icon="check_circle"
                ),
                ft.NavigationDrawerDestination(
                    label="Learning Page",
                    icon="menu_book_outlined",
                    selected_icon="menu_book"
                ),
                ft.NavigationDrawerDestination(
                    label="Vocabulary Trainer",
                    icon="psychology_outlined",
                    selected_icon="psychology"
                ),
                ft.NavigationDrawerDestination(
                    label="Dictionary",
                    icon="search_outlined",
                    selected_icon="search"
                ),
                
                # Divider before account section
                ft.Divider(height=20),
                
                # Account Section
                ft.NavigationDrawerDestination(
                    label="Account",
                    icon="person_outline",
                    selected_icon="person"
                ),
                ft.NavigationDrawerDestination(
                    label="Settings",
                    icon="settings_outlined",
                    selected_icon="settings"
                ),
                
                # Logout Button
                ft.Container(
                    margin=ft.margin.only(top=20, left=16, right=16, bottom=16),
                    content=ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Text("SIGN OUT", size=14, weight="bold"),
                                ft.Icon("logout", size=20),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        on_click=self.sign_out,
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="#f44336",
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=30, vertical=15),
                        ),
                        width=300,
                    ),
                ),
                
                # Version Info
                ft.Container(
                    padding=ft.padding.all(16),
                    content=ft.Row(
                        [
                            ft.Text("v1.0.0", size=10, color="#9e9e9e"),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )
            ],
        )
        
        # Set up drawer events
        self.drawer.on_dismiss = self.handle_dismissal
        self.drawer.on_change = self.handle_change
        
        # Initialize Pages
        self.learning_page = LearningPage(self.page)
        self.daily_tasks_page = DailyTasksPage(self.page)
        self.vocabs_page = VocabsPage(self.page)
        self.dictionary_page = DictionaryPage(self.page)
        self.account_page = AccountPage(self.page)
        self.settings_page = SettingsPage(self.page)
        self.spanish_main_tree = SpanishMainPage(self.page, self)
        self.english_main_tree = EnglishMainPage(self.page, self)

        self.current_shown_content = self.daily_tasks_page

        
        
        # Main content
        self.content = self.daily_tasks_page
        
    def handle_dismissal(self, e):
        # This is called when the drawer is dismissed (e.g., by tapping outside)
        pass
        
    def handle_change(self, e,):
        # Handle navigation when a drawer item is selected
        selected_index = e.control.selected_index
        print(f"Selected Index changed: {selected_index}")
        if selected_index == 0:
            self.content = self.daily_tasks_page
            self.not_on_home = False
            self.current_shown_content = self.daily_tasks_page
            self.appbar_title = "Daily Tasks"
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        elif selected_index == 1:
            self.not_on_home = False
            self.current_shown_content = self.learning_page
            self.content = self.learning_page
            self.appbar_title = "Learning Page"
            #Close drawer
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        elif selected_index == 2:
            self.not_on_home = False
            self.current_shown_content = self.vocabs_page
            self.content = self.vocabs_page
            self.appbar_title = "Vocabulary Trainer"
            #Close drawer
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        elif selected_index == 3:
            self.not_on_home = False
            self.current_shown_content = self.dictionary_page
            self.content = self.dictionary_page
            self.appbar_title = "Dictionary"
            #Close drawer
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        elif selected_index == 4:
            self.not_on_home = False
            self.current_shown_content = self.account_page
            self.content = self.account_page
            self.appbar_title = "Account"
            #Close drawer
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        elif selected_index == 5:
            self.not_on_home = False
            self.current_shown_content = self.settings_page
            self.content = self.settings_page
            self.appbar_title = "Settings"
            #Close drawer
            self.drawer.open = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()

    
    def toggle_drawer(self, e=None):
        # Toggle the drawer open/closed
        self.drawer.open = not self.drawer.open
        self.page.update()
        
    def show_server_info(self, e):
        self.page.open(self.server_info_dialog)
        self.page.update()
        
    def create_app_bar(self, appbar_title):
        # Get server URL or default text
        server_url = self.page.client_storage.get("server_url") or "No server"
        server_display = server_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Server info dialog is now created in show_server_info method
        if self.not_on_home:
            leading = ft.IconButton(
                icon="arrow_back",
                icon_color="white",
                tooltip="Go back",
                on_click=self.go_back_from_language_home
            )
        else:
            leading = ft.IconButton(
                icon="menu",
                icon_color="white",
                tooltip="Open menu",
                on_click=self.toggle_drawer
            )

        return ft.AppBar(
            leading=leading,
            title=ft.Text(f"{appbar_title}", color="white"),
            bgcolor="#1a73e8",
            center_title=False,
            actions=[
                # Learning language selection button (restored)
                self.language_btn,

                # Server Information Button
                ft.Container(
                    content=ft.IconButton(
                        icon="dns",
                        icon_color="white",
                        icon_size=22,
                        tooltip="Show server information",
                        on_click=self.show_server_info,
                    ),
                    padding=ft.padding.all(4),
                    on_click=self.show_server_info,
                ),
                
                # Native Language Selection Menu (Globe Icon)
                ft.PopupMenuButton(
                    icon="language",
                    icon_color="white",
                    tooltip="Change Native Language",
                    items=[
                        ft.PopupMenuItem(text="Select your native language"),  # Title
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(
                            text="English",
                            icon="check" if self.native_language_code == "en" else None,
                            on_click=lambda e: self.set_native_language("English", "en")
                        ),
                        ft.PopupMenuItem(
                            text="German",
                            icon="check" if self.native_language_code == "de" else None,
                            on_click=lambda e: self.set_native_language("German", "de")
                        ),
                        ft.PopupMenuItem(
                            text="Spanish",
                            icon="check" if self.native_language_code == "es" else None,
                            on_click=lambda e: self.set_native_language("Spanish", "es")
                        ),
                        ft.PopupMenuItem(
                            text="French",
                            icon="check" if self.native_language_code == "fr" else None,
                            on_click=lambda e: self.set_native_language("French", "fr")
                        ),
                        # Add more languages as needed
                    ],
                ),
                ft.IconButton(
                    icon="download",
                    icon_color="white",
                    tooltip="Download Lections from Server",
                    on_click=lambda e: self.page.go("/download-lection")
                ),
            ]
        )
    
    def _reset_sign_out_button(self):
        """Reset the sign-out button to its original state."""
        if hasattr(self, 'drawer') and len(self.drawer.controls) > 1:
            self.drawer.controls[-2].content.content = ft.Row(
                [
                    ft.Text("SIGN OUT", size=14, weight="bold"),
                    ft.Icon("logout", size=20),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
            self.drawer.controls[-2].content.disabled = False
            self.page.update()
    
    async def sign_out(self, e):
        try:
            # Set loading state
            if hasattr(self, 'drawer') and len(self.drawer.controls) > 1:
                self.drawer.controls[-2].content.disabled = True
                self.drawer.controls[-2].content.content = ft.Row(
                    [
                        ft.ProgressRing(width=20, height=20, stroke_width=2, color="white"),
                        ft.Text("Signing out...", size=14, weight="bold"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
                self.page.update()
            
            # Try to get and use the access token if available
            try:
                server_url = await self.page.client_storage.get_async("server_url")
                access_token = await self.page.client_storage.get_async("token")
                
                if server_url and access_token:
                    # Try to send logout request, but don't wait for it or handle errors
                    try:
                        requests.post(
                            f"{server_url}/logout",
                            params={"token": access_token},
                            timeout=2  # Short timeout to not block the UI
                        )
                    except:
                        pass  # Ignore any errors during logout
            except:
                pass  # Ignore any errors during token retrieval
            
            # Remove the token from client storage
            await self.page.client_storage.remove_async("token")
            
            # Navigate directly to the sign-in page
            self.page.go("/sign-in")
            
        except Exception as e:
            print(f"Error during sign out: {str(e)}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error during sign out: {str(e)}"),
                bgcolor="#f44336",
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=5000
            )
            self.page.snack_bar.open = True
            self._reset_sign_out_button()
    
    
    
    def go_back_from_language_home(self, e):
        if self.last_page:
            self.content = self.last_page.pop()
            self.current_shown_content = self.content
            self.on_language_home = False  # Or set based on the restored content
            self.set_appbar_title_by_content()
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()
        else:
            # If stack is empty, fallback to main page
            self.content = self.learning_page
            self.current_shown_content = self.learning_page
            self.appbar_title = "Learning Page"
            self.on_language_home = False
            self.page.views[-1].appbar = self.create_app_bar(self.appbar_title)
            self.page.update()

    def set_appbar_title_by_content(self):
        if self.current_shown_content == self.daily_tasks_page:
            self.appbar_title = "Daily Tasks"
            self.not_on_home = False
        elif self.current_shown_content == self.learning_page:
            self.appbar_title = "Learning Page"
            self.not_on_home = False
        elif self.current_shown_content == self.vocabs_page:
            self.appbar_title = "Vocabulary Trainer"
            self.not_on_home = False
        elif self.current_shown_content == self.dictionary_page:
            self.appbar_title = "Dictionary"
            self.not_on_home = False
        elif self.current_shown_content == self.account_page:
            self.appbar_title = "Account"
            self.not_on_home = False
        elif self.current_shown_content == self.settings_page:
            self.appbar_title = "Settings"
            self.not_on_home = False
        else:
            self.appbar_title = "OpenLingu"
            self.not_on_home = False
            
    async def _safe_save_language(self, language_name: str):
        """Safely save language to storage with proper error handling"""
        try:
            await self.page.client_storage.set_async("selected_language", language_name)
            print("[DEBUG] Language saved to client storage")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving language: {e}")
            return False

    def _run_async_save(self, language_name: str):
        """Run save operation in a new event loop if needed"""
        async def save():
            return await self._safe_save_language(language_name)
            
        try:
            # Try to run in the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                return asyncio.create_task(save())
            else:
                # If no loop is running, run it directly
                return loop.run_until_complete(save())
        except Exception as e:
            print(f"[WARNING] Couldn't save language: {e}")
            return None

    async def update_language(self, language_name: str):
        """
        Update the language button text with the provided language name.
        
        Args:
            language_name (str): The display name of the language (e.g., 'English', 'Deutsch')
        """
        if not language_name or not isinstance(language_name, str):
            print("[WARNING] Invalid language name provided")
            return
            
        print(f"[DEBUG] update_language called with: {language_name}")
        
        try:
            # Update the current language
            self.current_language = language_name
            
            # Update the UI
            if hasattr(self, 'language_btn') and self.language_btn is not None and self.page is not None:
                try:
                    self.language_btn.text = language_name
                    self.page.update()
                    print("[DEBUG] Language button updated")
                except Exception as e:
                    print(f"[ERROR] Failed to update language button: {e}")
            
            # Save to storage in the background
            if self.page is not None:
                # Run the save operation without awaiting it
                self._run_async_save(language_name)
                        
        except Exception as e:
            print(f"[ERROR] Error in update_language: {e}")
            import traceback
            traceback.print_exc()
