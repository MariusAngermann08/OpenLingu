import flet as ft
import requests
import sys
import os
import pathlib
import json
import traceback
import uuid
import threading
import inspect as py_inspect
from datetime import datetime

class DownloadLectionPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        self.language_tiles = []
        self.list_view = ft.ListView([], expand=True, spacing=8, padding=8, auto_scroll=False, height=500)
        self.info_text = ft.Text("Select a language to expand and see available lections.")
        # Loading overlay (initial)
        self._loading_status_text = ft.Text("", size=16, color="#5f6368")
        self.loading_overlay = ft.Container(
            expand=True,
            bgcolor="#ffffff",
            alignment=ft.alignment.center,
            content=ft.Column([
                ft.Text("Loading languages and lections...", size=20, color="#1a73e8"),
                ft.ProgressBar(width=400, color="#1a73e8", bgcolor="#e0e0e0", value=0, ref=ft.Ref[ft.ProgressBar]()),
                self._loading_status_text
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
        )
        self._main_content = ft.Column([
            ft.Text("Download Lections from Server", size=22, weight="bold", color="#1a73e8"),
            self.info_text,
            self.list_view,
            ft.Row([
                ft.ElevatedButton("Back", icon="arrow_back", bgcolor="#1a73e8", color="white", on_click=self.go_back)
            ], alignment=ft.MainAxisAlignment.END)
        ], expand=True)
        self.content = self.loading_overlay
        import threading
        threading.Thread(target=self.fetch_languages_and_lections, daemon=True).start()

    def go_back(self, e=None):
        self.page.go("/main")

    def fetch_languages_and_lections(self):
        server_url = self.page.client_storage.get("server_url")
        progress_bar = self.loading_overlay.content.controls[1]
        self._loading_status_text.value = "Fetching languages from server..."
        self.page.update()
        if not server_url:
            self.info_text.value = "No server URL set in client storage."
            self.list_view.controls = [ft.Text("DEBUG: No language tiles generated")] 
            self.content = self._main_content
            self.page.update()
            return
        try:
            resp = requests.get(f"{server_url.rstrip('/')}/languages")
            resp.raise_for_status()
            print("/languages response:", resp.text)
            languages = resp.json() if isinstance(resp.json(), list) else resp.json().get("languages", [])
            print("Parsed languages:", languages)
        except Exception as ex:
            self.info_text.value = f"Failed to fetch languages: {ex}"
            self.list_view.controls.clear()
            self.content = self._main_content
            self.page.update()
            return
        if not languages:
            self.info_text.value = "No languages found on the server."
            self.list_view.controls = [ft.Text("DEBUG: No language tiles generated")] 
            self.content = self._main_content
            self.page.update()
            return
        # Start progress bar
        self.info_text.value = "Loading languages and lections..."
        progress_bar.value = 1/(len(languages)+1)
        self._loading_status_text.value = "Loaded language list."
        self.page.update()
        # Fetch lections for all languages
        all_tiles = []
        total = len(languages)
        for idx, lang in enumerate(languages):
            if isinstance(lang, dict):
                lang_code = lang.get("code", str(lang))
                lang_name = lang.get("name", lang_code)
            else:
                lang_code = str(lang)
                lang_name = lang_code.capitalize()
            # Update status text
            self._loading_status_text.value = f"Loading lections for {lang_name}..."
            self.page.update()
            # Fetch lections for this language
            try:
                lec_resp = requests.get(f"{server_url.rstrip('/')}/languages/{lang_code}/lections")
                lec_resp.raise_for_status()
                lections = lec_resp.json() if isinstance(lec_resp.json(), list) else lec_resp.json().get("lections", [])
            except Exception as ex:
                lections = [f"Failed to fetch lections: {ex}"]
            tile = self.make_expansion_tile(lang_code, lang_name, lections)
            all_tiles.append(tile)
            progress_bar.value = (idx + 2) / (total + 1)
            self.page.update()
        if not all_tiles:
            self.list_view.controls = [ft.Text("DEBUG: No tiles after loop")] 
        else:
            self.list_view.controls = all_tiles
        self.info_text.value = "Select a language to expand and see available lections."
        self.content = self._main_content
        self.page.update()


    class DownloadExpandableLanguage(ft.Container):
        def __init__(self, parent_page, lang_code, lang_name, lections):
            super().__init__()
            self.parent_page = parent_page  # Reference to parent DownloadLectionPage
            self.page = parent_page.page  # Get page from parent
            self.lang_code = lang_code
            self.lang_name = lang_name
            self.expanded = False
            self.lections_column = ft.Column(visible=False, spacing=8)
            self.expand_icon = ft.Icon("chevron_right", color="#5f6368")
            self.header = ft.Container(
                content=ft.Row([
                    ft.Text(f"{self.lang_name} ({self.lang_code})", size=18, weight=ft.FontWeight.BOLD, color="#202124"),
                    ft.Container(expand=True),
                    self.expand_icon
                ]),
                padding=ft.padding.symmetric(vertical=10, horizontal=16),
                border_radius=10,
                bgcolor="#fff",
                on_click=self.toggle_expand,
                border=ft.border.all(1, "#e0e0e0"),
                shadow=ft.BoxShadow(blur_radius=3, color="#00000010", offset=ft.Offset(0,1)),
            )
            # Determine if download buttons should be disabled
            server_url = self.page.client_storage.get("server_url") or ""
            is_localhost = "localhost" in server_url or "127.0.0.1" in server_url
            download_btn_color = "#bdbdbd" if is_localhost else "#1a73e8"
            download_btn_enabled = not is_localhost
            # Render lections immediately
            if isinstance(lections, list) and lections:
                for lec in lections:
                    lec_title = lec.get("title") if isinstance(lec, dict) else lec
                    self.lections_column.controls.append(
                        ft.Row([
                            ft.Text(lec_title),
                            ft.IconButton(
                                icon="download",
                                tooltip="Download",
                                on_click=lambda e, lc=lang_code, lt=lec_title, ld=lec: (
                                    print(f"[DEBUG] Download button clicked: {lt} ({lc})"),
                                    self.parent_page.download_lection(lc, lt, ld)
                                )[-1],
                                bgcolor=download_btn_color,
                                disabled=not download_btn_enabled
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
            else:
                self.lections_column.controls.append(ft.Text("No lections found."))
            self.content = ft.Column([
                self.header,
                self.lections_column
            ])

        def toggle_expand(self, e=None):
            self.expanded = not self.expanded
            self.lections_column.visible = self.expanded
            self.expand_icon.rotate = 1.57 if self.expanded else 0
            self.update()

    def make_expansion_tile(self, lang_code, lang_name, lections):
        # Create the expansion tile with a reference to this page instance
        tile = self.DownloadExpandableLanguage(self, lang_code, lang_name, lections)
        return tile
        
    def ensure_language_exists(self, session, lang_code, lang_name):
        """Ensure the language exists in the database, create it if not"""
        try:
            from models import Language as DBLanguage
            
            # Check if language exists
            lang = session.query(DBLanguage).filter_by(name=lang_code).first()
            if not lang:
                print(f"[DEBUG] Creating new language: {lang_code} ({lang_name})")
                # Create the language
                lang = DBLanguage(
                    name=lang_code,
                    created_by="downloaded"
                )
                session.add(lang)
                session.commit()
                print(f"[DEBUG] Created language: {lang_code}")
            return lang
        except Exception as e:
            print(f"[ERROR] Error in ensure_language_exists: {e}")
            print(traceback.format_exc())
            raise

    def download_lection(self, lang_code, lection_title, lection_data):
        """Download a lection from the server and save it to the local database.
        
        Args:
            lang_code (str): The language code of the lection
            lection_title (str): The title of the lection to download
            lection_data (dict): Additional lection data
        """
        print(f"[DEBUG] Starting download_lection for '{lection_title}' in language '{lang_code}'")
        
        # Get server URL with fallback to config file
        server_url = None
        try:
            # Try to get from client storage first
            server_url = self.page.client_storage.get("server_url")
            print(f"[DEBUG] Server URL from client storage: {server_url}")
            
            # Fall back to config file if not found
            if not server_url:
                try:
                    config_path = pathlib.Path(__file__).parent.parent.parent / 'config.json'
                    print(f"[DEBUG] Looking for config file at: {config_path}")
                    if config_path.exists():
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            server_url = config.get('server_url')
                            print(f"[DEBUG] Server URL from config file: {server_url}")
                except Exception as e:
                    print(f"[ERROR] Error reading config file: {e}")
                    print(traceback.format_exc())
            
            if not server_url:
                error_msg = "Server URL not configured. Please set it in the settings."
                print(f"[ERROR] {error_msg}")
                self.show_error(error_msg)
                return
            
            # Clean up server URL
            server_url = server_url.rstrip('/')
            print(f"[DEBUG] Using server URL: {server_url}")
            
            # Show loading overlay
            self.content = self.loading_overlay
            self._loading_status_text.value = f"Downloading lection: {lection_title}..."
            self.page.update()
            
            # Log environment info
            print("[DEBUG] Environment Info:")
            print(f"  Python: {sys.version.split()[0]}")
            print(f"  Flet: {getattr(ft, '__version__', 'unknown')}")
            print(f"  Requests: {requests.__version__}")
            
            # Prepare request
            lection_url = f"{server_url}/languages/{lang_code}/lections/by_title/{lection_title}"
            print(f"[DEBUG] Request URL: {lection_url}")
            
            headers = {
                'User-Agent': 'OpenLingu-Client/1.0',
                'Accept': 'application/json'
            }
            
            # Make the request
            print("[DEBUG] Sending request...")
            response = requests.get(
                lection_url,
                headers=headers,
                timeout=30,  # 30 second timeout
                allow_redirects=True
            )
            
            # Log response details
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Content-Type: {response.headers.get('content-type')}")
            print(f"[DEBUG] Content length: {len(response.content)} bytes")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                lection = response.json()
                if not isinstance(lection, dict):
                    raise ValueError(f"Expected dict response, got {type(lection).__name__}")
                
                print(f"[DEBUG] Successfully parsed lection: {lection.get('title', 'Untitled')}")
                print(f"[DEBUG] Lection ID: {lection.get('id', 'N/A')}")
                
                # Save to database
                self._save_lection_to_database(lang_code, lection_title, lection)
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response: {str(e)}"
                print(f"[ERROR] {error_msg}")
                print(f"[DEBUG] Response: {response.text[:500]}...")
                self.show_error("Invalid response from server")
                return
                
        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            print(f"[ERROR] Request failed: {error_type}")
            print(f"[ERROR] Details: {str(e)}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            
            if isinstance(e, requests.exceptions.Timeout):
                error_msg = "Request timed out. Please try again."
            elif isinstance(e, requests.exceptions.ConnectionError):
                error_msg = "Failed to connect to server. Check your connection and try again."
            elif isinstance(e, requests.exceptions.HTTPError):
                status_code = getattr(e.response, 'status_code', 'unknown')
                error_msg = f"Server error: {status_code}"
                print(f"[ERROR] Response content: {getattr(e.response, 'text', 'No response content')}")
            else:
                error_msg = f"Network error: {str(e)}"
            
            self.show_error(error_msg)
            return
        
        except Exception as e:
            print("[ERROR] Unexpected error in download_lection:")
            print(f"[ERROR] Type: {type(e).__name__}")
            print(f"[ERROR] Error: {str(e)}")
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            
            # Show user-friendly error
            error_msg = f"An error occurred: {str(e)}"
            if len(error_msg) > 100:  # Truncate long messages
                error_msg = error_msg[:100] + "..."
            
            self.show_error(error_msg)
        finally:
            # Always restore the main content view
            try:
                self.content = self._main_content
                self.page.update()
            except Exception as e:
                print(f"[WARNING] Error restoring UI: {e}")

    def _save_lection_to_database(self, lang_code, lection_title, lection_data):
        """Save the downloaded lection to the local database.
        
        Args:
            lang_code (str): The language code of the lection
            lection_title (str): The title of the lection
            lection_data (dict): The lection data to save
        """
        print(f"[DEBUG] Saving lection to database: {lection_title}")
        
        try:
            # Get database path
            project_root = pathlib.Path(__file__).parent.parent.parent.parent
            db_path = project_root / 'server' / 'db' / 'languages.db'
            print(f"[DEBUG] Database path: {db_path}")
            
            if not db_path.exists():
                error_msg = f"Database file not found at: {db_path}"
                print(f"[ERROR] {error_msg}")
                self.show_error("Local database not found. Please make sure the server is running locally.")
                return
            
            # Add server directory to Python path for imports
            server_path = str(project_root / 'server')
            if server_path not in sys.path:
                sys.path.insert(0, server_path)
            
            # Import SQLAlchemy components
            try:
                from sqlalchemy import create_engine, text
                from sqlalchemy.orm import sessionmaker, scoped_session
                from sqlalchemy.exc import SQLAlchemyError
                print("[DEBUG] Successfully imported SQLAlchemy")
                
                # Initialize database connection
                db_uri = f'sqlite:///{db_path}?check_same_thread=False'
                engine = create_engine(db_uri, echo=True)
                Session = scoped_session(sessionmaker(bind=engine))
                session = Session()
                
                try:
                    # Import models
                    from models import Language, Lection
                    
                    # Ensure language exists - note: Language model uses 'name' as primary key
                    # Get language from the lection data or use the provided lang_code as fallback
                    lang_name = lection_data.get('language', lang_code)
                    language = session.query(Language).filter_by(name=lang_name).first()
                    if not language:
                        # Create new language with name as primary key
                        language = Language(name=lang_name, created_by='downloaded')
                        session.add(language)
                        session.commit()
                        print(f"[DEBUG] Created new language: {lang_name}")
                    
                    # Create or update lection
                    lection_id = lection_data.get('id')
                    lection = session.query(Lection).filter_by(id=lection_id).first()
                    
                    # Get lection data from the API response
                    lection_title = lection_data.get('title', '')
                    lection_description = lection_data.get('description', '')
                    lection_difficulty = lection_data.get('difficulty', 'beginner')
                    lection_content = lection_data.get('content', {})
                    
                    if lection:
                        # Update existing lection
                        lection.title = lection_title
                        lection.description = lection_description
                        lection.language = lang_name  # Use the language name as stored in the database
                        lection.difficulty = lection_difficulty
                        lection.content = lection_content
                        lection_updated = True
                        print(f"[DEBUG] Updated existing lection: {lection_title} (ID: {lection_id})")
                    else:
                        # Create new lection
                        lection = Lection(
                            id=lection_id,
                            title=lection_title,
                            description=lection_description,
                            language=lang_name,  # Use the language name as stored in the database
                            difficulty=lection_difficulty,
                            content=lection_content,
                            created_by='downloaded'
                        )
                        session.add(lection)
                        lection_created = True
                        print(f"[DEBUG] Created new lection: {lection_title} (ID: {lection_id})")
                    
                    session.commit()
                    print(f"[SUCCESS] Successfully saved lection: {lection_title}")
                    self.show_success(f"Lection saved successfully!")
                    
                except SQLAlchemyError as e:
                    session.rollback()
                    print(f"[ERROR] Database error: {e}")
                    self.show_error("Error saving to database")
                    return
                finally:
                    session.close()
                    
            except ImportError as e:
                print(f"[ERROR] Failed to import database modules: {e}")
                self.show_error("Database error: Required modules not found")
                return
                
                # This block intentionally left blank - duplicate code removed
                
        except requests.exceptions.RequestException as e:
            self.show_error(f"Error downloading lection: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")
    
    def show_success(self, message):
        """Show a success message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor="#4CAF50"
        )
        self.page.snack_bar.open = True
        self.page.update()
        
    def show_error(self, message):
        """Show an error message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor="#F44336"
        )
        self.page.snack_bar.open = True
        self.page.update()
