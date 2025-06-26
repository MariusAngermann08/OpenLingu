import flet as ft

# Handle import as module or directly
try:
    from Pages.lection_editor import MainEditor
    from Pages.authpage import LoginPage
    from Pages.Main_menu import MainMenu
except ImportError:
    from Pages.authpage import LoginPage
    from Pages.Main_menu import MainMenu
    from Pages.lection_editor import MainEditor

def route_change(e):
    page = e.page
    route = e.route
    
    # Don't clear views if it's just a route update
    if not page.views or page.views[-1].route != route:
        page.views.clear()
    
    if route == "/login":
        # Set window size for login
        page.window_width = 400
        page.window_height = 600
        page.window_resizable = False
        page.theme_mode = "light"
        
        # Create and add login view
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            controls=[
                LoginPage(page)
            ]
        )
        page.views.append(view)
    
    elif route == "/main":
        # Set window size for main app
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.theme_mode = "light"
        
        # Create and add main menu view
        main_menu = MainMenu(page)
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            appbar=main_menu.create_app_bar(),
            controls=[main_menu]
        )
        page.views.append(view)

    elif route == "/editor":
        # Set window size for editor
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.theme_mode = "light"
        main_editor = MainEditor(page)

        
        # Create and add editor view (placeholder)
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            controls=[
                main_editor
            ]
        )
        page.views.append(view)        
    
    page.update()

def view_pop(view):
    view.page.views.pop()
    top_view = view.page.views[-1]
    view.page.go(top_view.route)

def main(page: ft.Page):
    page.title = "Lection Creator"
    page.padding = 0
    
    # Set up routing
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Initial route
    page.go("/editor")
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)