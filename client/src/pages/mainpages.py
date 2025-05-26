import flet as ft
import requests

#Function to remove the access token from the client storage
def remove_access_token(page):
    page.client_storage.remove("access_token")

class MainPage(ft.Container):
    def __init__(self, page, route, drawer):
        super().__init__()
        self.page = page
        self.route = route
        self.drawer = drawer
        
        # Set up drawer events
        self.drawer.on_dismiss = self.handle_dismissal
        self.drawer.on_change = self.handle_change
        
        # Main content
        self.content = ft.Column(
            controls=[
                ft.Text("Welcome to OpenLingu Legacy!", size=24, weight="bold"),
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
    
    async def sign_out(self, e):
        try:
            # Get the server URL from client storage
            server_url = await self.page.client_storage.get_async("server_url")
            if not server_url:
                print("Server URL not found in client storage")
                return
                
            # Get the access token
            access_token = await self.page.client_storage.get_async("token")
            if not access_token:
                print("No access token found")
                return
                
            # Send logout request to the server
            response = requests.post(
                f"{server_url}/logout",
                params={"token": access_token},
                timeout=10
            )

            # Remove the token from client storage regardless of the response
            await self.page.client_storage.remove_async("token")
            
            # Navigate to the login page
            self.page.go("/")
            
        except Exception as e:
            print(f"Error during sign out: {str(e)}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error during sign out: {str(e)}"),
                bgcolor="red",
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=5000
            )
            self.page.snack_bar.open = True
            self.page.update()
