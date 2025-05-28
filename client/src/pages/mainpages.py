import flet as ft
import requests

#Function to remove the access token from the client storage
def remove_access_token(page):
    page.client_storage.remove("access_token")

class MainPage(ft.Container):
    def __init__(self, page, route):
        super().__init__()
        self.page = page
        self.route = route
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # Default language (can be loaded from user preferences later)
        self.current_language = "English"
        
        # Create language button reference for hover effect
        self.language_btn = ft.Ref[ft.Container]()
        # Create server button reference for hover effect
        self.server_btn = ft.Ref[ft.Container]()
        
        # Server info dialog will be created when needed
        
        # Sign out button state and reference
        self.sign_out_button = None
        self.is_signing_out = False
        
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
        
        # Main content
        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to OpenLingu!", size=24, weight="bold"),
                ft.Text("Select an option from the menu to get started.", size=16, color="grey"),
            ],
            alignment="center",
            horizontal_alignment="center",
            expand=True
        )
        
    def handle_dismissal(self, e):
        # This is called when the drawer is dismissed (e.g., by tapping outside)
        pass
        
    def handle_change(self, e):
        # Handle navigation when a drawer item is selected
        selected_index = e.control.selected_index
        print(f"Selected Index changed: {selected_index}")
        
        # Close the drawer after selection
        self.drawer.open = False
        self.page.update()
        
    def toggle_drawer(self, e=None):
        # Toggle the drawer open/closed
        self.drawer.open = not self.drawer.open
        self.page.update()
        
    def show_server_info(self, e):
        print("Server info button clicked")  # Debug print
        try:
            server_url = self.page.client_storage.get("server_url") or "No server configured"
            print(f"Server URL: {server_url}")  # Debug print
            
            # Create a simple dialog
            dlg = ft.AlertDialog(
                title=ft.Text("Server Information"),
                content=ft.Text(server_url, selectable=True),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.close_dialog(dlg))
                ],
            )
            
            # Show the dialog
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
            print("Dialog should be visible now")  # Debug print
            
        except Exception as ex:
            print(f"Error showing server info: {ex}")
    
    def close_dialog(self, dlg):
        dlg.open = False
        self.page.update()
        
    def close_server_info(self, e):
        self.server_info_dialog.open = False
        self.page.update()
        
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
