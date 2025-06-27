import flet as ft
import requests

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
        def __init__(self, page, lang_code, lang_name, lections):
            super().__init__()
            self.page = page
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
            is_localhost = "localhost" in server_url
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
                                on_click=None,
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
        return self.DownloadExpandableLanguage(self.page, lang_code, lang_name, lections)
