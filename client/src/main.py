import flet as ft
import requests

#Import App Pages
from pages.authpages import *
from pages.mainpage import *
from pages.serverpage import *
from pages.connectingpage import *





def route_change(e):
    page = e.page
    page.views.clear()
    route = page.route

    if route == "/":
        page.go("/main")
        # Check if server url is saved
        #server_url = page.client_storage.get("server_url")
        #if server_url:
            # Go to connecting page to validate the server
            #page.go(f"/connecting?url={server_url}")
        #else:
            #page.go("/server")
    
    
    def create_server_appbar(page):
        server_url = page.client_storage.get("server_url") or "No server selected"
        # Extract domain from URL
        server_display = server_url.replace("https://", "").replace("http://", "").split("/")[0]
        # Create a container reference for the animation
        server_btn = ft.Ref[ft.Container]()
        
        return ft.AppBar(
            leading=ft.Icon("dns", color="white"),
            title=ft.Text("Server", color="white"),
            center_title=False,
            bgcolor="#1a73e8",
            elevation=1,
            actions=[
                ft.Container(
                    ref=server_btn,
                    content=ft.Row([
                        ft.Icon("public", color="white", size=18, opacity=0.9),
                        ft.Container(
                            content=ft.Text(
                                server_display,
                                color="white",
                                size=13,
                                weight="w500",
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            padding=ft.padding.only(right=4)
                        ),
                        ft.Icon("chevron_right", color="white", size=16, opacity=0.8),
                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=16,
                    bgcolor="#1557b0",
                    animate=300,  # Animation duration in milliseconds
                    on_hover=lambda e: (
                        setattr(server_btn.current, "bgcolor", "#1a4d8c" if e.data == "true" else "#1557b0"),
                        server_btn.current.update()
                    ),
                    on_click=lambda _: page.go("/server"),
                    tooltip="Change server",
                )
            ]
        )

    if route == "/server":
        page.views.append(
            ft.View(
                route="/server",
                controls=[ServerPage(page, route)]
            )
        )
    elif route.startswith("/connecting"):
        page.views.append(
            ft.View(
                route=route,
                controls=[ConnectingPage(page, route)]
            )
        )
    elif route == "/sign-in":
        page.views.append(
            ft.View(
                route="/sign-in",
                appbar=create_server_appbar(page),
                controls=[SignInPage(page, route)]
            )
        )

    elif route == "/sign-up":
        page.views.append(
            ft.View(
                route="/sign-up",
                appbar=create_server_appbar(page),
                controls=[SignUpPage(page, route)]
            )
        )
    elif route == "/main":
        # Create main page instance with integrated NavigationDrawer and app bar
        mainpage = MainPage(page, route)
        
        # Create view with drawer and app bar
        view = ft.View(
            route="/main",
            appbar=mainpage.create_app_bar(),
            drawer=mainpage.drawer,
            controls=[mainpage]
        )

        page.views.append(view)

    
    page.update()

def main(page: ft.Page):
    page.title = "OpenLingu Legacy"
    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, view=ft.AppView.FLET_APP)

