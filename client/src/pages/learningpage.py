import flet as ft
import requests

class LearningPage(ft.Container):
    def __init__(self, page, route):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.route = route
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to the Learningpage!", size=24, weight="bold"),
                ft.Text("Fresh Content to learn will be added soon", size=16, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        
        
        
        
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

    def handle_dismissal(self, e):
        pass
    
    def handle_change(self, e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            e.page.go("/main")
        elif selected_index == 1:
            e.page.go("/learning-page")
        
        self.page.update()
    
    def sign_out(self, e):
        pass

    def toggle_drawer(self, e=None):
        # Toggle the drawer open/closed
        self.drawer.open = not self.drawer.open
        self.page.update()
    
    def show_server_info(self, e):
        pass




    def create_app_bar(self):
        # Get server URL or default text
        server_url = self.page.client_storage.get("server_url") or "No server"
        server_display = server_url.replace("https://", "").replace("http://", "").split("/")[0]

        # Server info dialog is now created in show_server_info method

        return ft.AppBar(
            leading=ft.IconButton(
                icon="menu",
                icon_color="white",
                tooltip="Open menu",
                on_click=self.toggle_drawer
            ),
            title=ft.Text("OpenLingu", color="white"),
            bgcolor="#1a73e8",
            center_title=False,
            actions=[
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
                
                # Language Selection Button
                ft.IconButton(
                    icon="language",
                    icon_color="white",
                    tooltip="Change Language",
                    on_click=lambda _: None,  # Add language selection logic here
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=8,
                    ),
                ),
            ]
        )