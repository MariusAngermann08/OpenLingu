import flet as ft

# Handle import as module or directly
try:
    from Pages.lection_editor import MainEditor
    from Pages.authpage import LoginPage
    from Pages.Main_menu import MainMenu
    from Pages.serverpage import ServerPage
except ImportError:
    from Pages.authpage import LoginPage
    from Pages.Main_menu import MainMenu
    from Pages.lection_editor import MainEditor
    from Pages.serverpage import ServerPage

def route_change(e):
    page = e.page
    route = e.route
    
    # Don't clear views if it's just a route update
    if not page.views or page.views[-1].route != route:
        page.views.clear()
    
    if route == "/server":
        # Set window size for server
        page.window_width = 400
        page.window_height = 600
        page.window_resizable = False
        page.theme_mode = "light"
        
        # Create and add server view
        server_page = ServerPage(page)
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            controls=[server_page]
        )
        page.views.append(view)

    elif route == "/login":
        # Set window size for login
        page.window_width = 400
        page.window_height = 600
        page.window_resizable = False
        page.theme_mode = "light"
        
        # Create and add login view
        login_page = LoginPage(page)
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            appbar=login_page.app_bar,
            controls=[login_page]
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

    elif route.startswith("/editor"):
        # Parse query parameters
        from urllib.parse import parse_qs, urlparse
        
        # Default values
        is_new = True
        lection_name = ""
        
        # Parse query parameters from URL
        parsed_url = urlparse(route)
        params = parse_qs(parsed_url.query)
        
        # Get values from query parameters
        if 'new' in params:
            is_new = params['new'][0].lower() == 'true'
        if 'lection_name' in params:
            lection_name = params['lection_name'][0]
        if 'language' in params:
            language = params['language'][0]
        else:
            language = "en"  # Default to English if not specified
        
        # Set window size for editor
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.theme_mode = "light"
        
        # Create MainEditor with parameters
        main_editor = MainEditor(
            page=page, 
            new=is_new, 
            lection_name=lection_name,
            language=language
        )
        
        # Create and add editor view
        view = ft.View(
            route=route,
            padding=0,
            bgcolor="#f5f5f5",
            spacing=0,
            appbar=main_editor.create_app_bar(),
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
    page.go("/server")
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)