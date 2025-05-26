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
        self.drawer = ft.NavigationDrawer(
            on_dismiss=self.handle_dismissal,
            on_change=self.handle_change,
            controls=[
                ft.Container(height=12),
                ft.NavigationDrawerDestination(
                    label="Item 1",
                    icon=ft.Icons.DOOR_BACK_DOOR_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.DOOR_BACK_DOOR),
                ),
                ft.Divider(thickness=2),
                ft.NavigationDrawerDestination(
                    icon=ft.Icon(ft.Icons.MAIL_OUTLINED),
                    label="Item 2",
                    selected_icon=ft.Icons.MAIL,
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icon(ft.Icons.PHONE_OUTLINED),
                    label="Item 3",
                    selected_icon=ft.Icons.PHONE,
                ),
            ],
        )
    def handle_dismissal(self, e):
        print("Drawer dismissed!")

    def handle_change(self, e):
        print(f"Selected Index changed: {e.control.selected_index}")
        self.page.close(self.drawer)
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
