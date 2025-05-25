import flet as ft
import urllib.parse
import asyncio

class ConnectingPage(ft.Container):
    def __init__(self, page: ft.Page, route: str):
        # Store page reference
        self._page = page
        self.route = route
        self.server_url = self._get_server_url()
        self._connection_started = False
        self._from_server_page = 'from_server_page' in self.route
        
        # Create UI elements
        self.loading_indicator = ft.ProgressRing(
            width=50,
            height=50,
            stroke_width=3,
            value=None,  # Indeterminate mode
            color="blue700"
        )
        
        self.status_text = ft.Text(
            "Preparing to connect...",
            size=18,
            weight="w500",
            text_align=ft.TextAlign.CENTER
        )
        
        self.error_text = ft.Text(
            "",
            size=16,
            color="red",
            visible=False,
            text_align=ft.TextAlign.CENTER
        )
        
        self.retry_button = ft.ElevatedButton(
            "Retry",
            icon="refresh",
            on_click=self.retry_connection,
            visible=False,
            style=ft.ButtonStyle(
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        back_button = ft.TextButton(
            "Back to server selection",
            icon="arrow_back",
            on_click=self._go_back,
            style=ft.ButtonStyle(padding=20)
        )
        
        super().__init__(
            content=ft.Column(
                [
                    ft.Container(height=100),
                    ft.Icon(name="dns", size=60, color="blue700"),
                    ft.Container(height=30),
                    self.loading_indicator,
                    ft.Container(height=20),
                    self.status_text,
                    ft.Container(height=20),
                    self.error_text,
                    self.retry_button,
                    ft.Container(height=40),
                    back_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        # Schedule the connection to start after the page is fully initialized
        self._page.run_task(self._delayed_start_connection)
    
    async def _delayed_start_connection(self):
        # Small delay to ensure the page is fully initialized
        await asyncio.sleep(0.1)
        # Make sure loading indicator is visible
        self._update_ui(
            loading=True,
            status=f"Connecting to:\n{self.server_url}",
            error=None,
            show_retry=False
        )
        # Start connection attempt
        await self.connect_to_server()
    
    def _go_back(self, e=None):
        if self.page:
            self.page.go("/server")
    
    def _get_server_url(self):
        if '?' in self.route:
            params = dict(pair.split('=') for pair in self.route.split('?')[1].split('&'))
            return urllib.parse.unquote(params.get('url', ''))
        return ""
    
    async def connect_to_server(self):
        import requests
        
        if not self.server_url:
            self._update_ui(error="No server URL provided")
            return
        
        # Update UI to show connecting state
        self._update_ui(
            loading=True,
            status=f"Connecting to:\n{self.server_url}",
            error=None,
            show_retry=False
        )
        
        def _make_request():
            try:
                # Only check the base URL, no additional paths
                response = requests.get(self.server_url.rstrip('/'), timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and data.get('msg') == 'OpenLingu':
                        return True
                return False
            except Exception as e:
                return False
        
        try:
            # Run the request in a thread
            loop = asyncio.get_event_loop()
            is_valid = await loop.run_in_executor(None, _make_request)
            
            if is_valid:
                self._update_ui(status="Connected successfully!")
                await asyncio.sleep(1)
                if hasattr(self, '_page') and self._page:
                    self._page.go("/sign-in")
                return
            
            # If we get here, the server is either not online or not a valid OpenLingu server
            error_msg = f"Could not connect to {self.server_url}"
            
            # Show detailed error in the UI
            self._update_ui(
                error=f"{error_msg}\n\nThe server is either offline or not a valid OpenLingu server.",
                loading=False,
                show_retry=True
            )
            
            # Show error message on the current page without redirecting
            # The error is already displayed in the UI via self._update_ui()
            
        except Exception as e:
            error_msg = f"Failed to connect to {self.server_url}"
            
            # Show error in the UI
            self._update_ui(
                error=f"{error_msg}\n\nPlease check the server URL and try again.",
                loading=False,
                show_retry=True
            )
            
            # Show error message on the current page without redirecting
            # The error is already displayed in the UI via self._update_ui()
    
    def _update_ui(self, status=None, error=None, loading=None, show_retry=None):
        """Helper method to safely update the UI"""
        if status is not None:
            self.status_text.value = status
        
        if error is not None:
            self.error_text.value = str(error)
            self.error_text.visible = bool(error)
        
        if loading is not None:
            self.loading_indicator.visible = loading
            if loading:
                self.loading_indicator.value = None  # Start indeterminate animation
            else:
                self.loading_indicator.value = 0.5  # Show static state when not loading
        
        if show_retry is not None:
            self.retry_button.visible = show_retry
        
        # Only update if we have a page reference
        if hasattr(self, '_page') and self._page:
            try:
                self._page.update()
            except Exception as e:
                print(f"Error updating UI: {e}")
    
    def show_error(self, message):
        self.loading_indicator.visible = False
        self.error_text.value = message
        self.error_text.visible = True
        self.retry_button.visible = True
        self.update()
    
    async def retry_connection(self, e):
        """Handle retry button click"""
        if hasattr(self, 'page') and self.page:
            # Reset UI for retry
            self._update_ui(
                loading=True,
                status=f"Connecting to:\n{self.server_url}",
                error=None,
                show_retry=False
            )
            # Start connection attempt
            await self.connect_to_server()
