import flet as ft

# Function for saving the server URL to client storage
async def save_server_url(page, url):
    await page.client_storage.set_async("server_url", url)

class ServerPage(ft.Container):
    def __init__(self, page: ft.Page, route: str):
        super().__init__()
        self.page = page
        self.route = route
        self.selected_server = None
        self.url_input = ft.TextField(
            label="Server URL",
            border=ft.InputBorder.UNDERLINE,
            prefix_icon="link",
            hint_text="Enter the URL of the server",
            focused_border_color="#1565C0",
            focused_color="#1565C0",
            visible=False,
            on_change=self.on_url_change
        )
        
        # Server options
        self.server_options = {
            "OpenLingu-Main": "https://openlingu-main.example.com",
            "EierLingu": "https://eierlingu.example.com"
        }
        self.selected_server_name = "OpenLingu-Main"
        self.selected_server = self.server_options[self.selected_server_name]
        
        # Server selection radio buttons
        self.official_radio = ft.Radio("Choose from list", value="official")
        self.localhost_radio = ft.Radio("Use Localhost", value="localhost")
        self.custom_radio = ft.Radio("Custom URL", value="custom")
        
        # Server list radio buttons group
        self.server_radio_group = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(
                        name,
                        value=url
                    ) for name, url in self.server_options.items()
                ],
                spacing=5
            ),
            value=next(iter(self.server_options.values())),  # First URL as default
            on_change=lambda e: self.on_server_select(e.control.value)
        )
        self.server_radios = ft.Container(
            content=self.server_radio_group,
            visible=True
        )
        
        # Selected server URL display
        self.server_url_display = ft.TextField(
            value=self.selected_server,
            read_only=True,
            border=ft.InputBorder.UNDERLINE,
            color="#757575",  # Grey 600
            bgcolor="#F5F5F5",  # Grey 100
            text_size=12,
            height=40,
            expand=True
        )
        
        self.radio_group = ft.RadioGroup(
            content=ft.Column([
                self.official_radio,
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=self.server_radios,
                            padding=ft.padding.only(left=30, top=5, bottom=5)
                        ),
                        ft.Container(
                            content=ft.Row([
                                #ft.Text("Selected URL:", size=12, color="#757575"),   Grey 600
                                self.server_url_display
                            ], spacing=10),
                            padding=ft.padding.only(left=30, top=5, bottom=5)
                        )
                    ], spacing=0)
                ),
                self.localhost_radio,
                self.custom_radio,
            ], spacing=5),
            value="official",
            on_change=self.on_server_change
        )
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Select a OpenLingu server", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        ft.Divider(height=10, color="transparent"),
                        self.radio_group,
                        ft.Divider(height=10, color="transparent"),
                        self.url_input,
                        ft.Divider(height=25, color="transparent"),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Text("NEXT", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Icon("arrow_forward"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#1565C0",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                            ),
                            on_click=self.next,
                            width=320,
                        ),
                    ]
                ),
                padding=30,
                width=320,
            ),
            elevation=5,
        )

        self.content = ft.Container(
            margin=ft.margin.only(top=50),
            content=card,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=["#E3F2FD", "white"],
            ),
            expand=True,
        )
    
    def on_server_change(self, e):
        # Update UI based on selection
        if self.radio_group.value == "custom":
            self.url_input.visible = True
            self.server_radios.visible = False
            self.server_url_display.visible = False
            self.url_input.value = "http://"
            self.selected_server = None
        elif self.radio_group.value == "localhost":
            self.url_input.visible = False
            self.server_radios.visible = False
            self.server_url_display.visible = False
            self.selected_server = "http://localhost:8000"
            self.update_url_display()
        else:  # official
            self.url_input.visible = False
            self.server_radios.visible = True
            self.server_url_display.visible = True
            self.update_url_display()
        
        if hasattr(self, 'page') and self.page is not None:
            self.page.update()
    
    def on_server_select(self, url):
        # Update selected server when radio changes
        if self.radio_group.value == "official":
            self.selected_server = url
            self.update_url_display()
            if hasattr(self, 'page') and self.page is not None:
                self.page.update()
    
    def update_url_display(self):
        # Update the URL display field
        self.server_url_display.value = self.selected_server
    
    def on_url_change(self, e):
        # Update selected server when URL changes
        if self.radio_group.value == "custom":
            self.selected_server = e.control.value
            self.update_url_display()
    
    def show_error(self, message):
        """Helper to show error messages in a snackbar"""
        if hasattr(self, 'page') and self.page is not None:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message),
                bgcolor="red",
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=5000
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def next(self, e):
        async def _next():
            if not self.selected_server and self.radio_group.value == "custom":
                self.show_error("Please enter a valid server URL")
                return
                
            print(f"Selected server: {self.selected_server}")
            # Save the selected server URL
            server_url = "http://localhost:8000"  # For now using localhost
            # Uncomment to use selected server: server_url = self.selected_server
            await save_server_url(self.page, server_url)
            # Navigate to connecting page with the server URL as a parameter
            self.page.go(f"/connecting?url={server_url}&from_server_page=True")
        
        self.page.run_task(_next)