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

        self.content = ft.Column(
            [
                ft.Text("This is the main page of the app a users encounters after login", size=28, weight=ft.FontWeight.BOLD, color="#1565C0"),
                ft.ElevatedButton(
                    "Sign Out",
                    on_click=self.sign_out,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    
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
