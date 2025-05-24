import flet as ft

#Import App Pages
from pages.authpages import *
from pages.mainpages import *

def route_change(e):
    page = e.page
    page.views.clear()
    route = page.route

    if route == "/":
        page.go("/sign-in")
    
    elif route == "/sign-in":
        page.views.append(
            ft.View(
                route="/sign-in",
                controls=[SignInPage(page, route)]
            )
        )

    elif route == "/sign-up":
        page.views.append(
            ft.View(
                route="/sign-up",
                controls=[SignUpPage(page, route)]
            )
        )
    
    elif route == "/main":
        page.views.append(
            ft.View(
                route="/main",
                controls=[MainPage(page, route)]
            )
        )
    page.update()

def main(page: ft.Page):
    page.title = "OpenLingu Legacy"
    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, view=ft.AppView.FLET_APP)