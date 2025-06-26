import flet as ft


class EditorField(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )

        self.field = ft.Container(
            content=[],
            expand=True,
            bgcolor="#d86e6e",
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.field,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
        )

class EditorSelection(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )

        self.selection_options = ft.GridView(
                controls=[
                    ft.ElevatedButton(
                        text="Matchable Pairs",
                        on_click= lambda e: page.go("/editor/text"),
                        width=150,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding(10, 5, 10, 5),
                            bgcolor="#2196f3",
                            color="white",
                            overlay_color="#1976d2",
                        ),
                    ),
                    ft.ElevatedButton(
                        text="Gap Text",
                        on_click=lambda e: page.go("/editor/text"),
                        width=150,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding(10, 5, 10, 5),
                            bgcolor="#2196f3",
                            color="white",
                            overlay_color="#1976d2",
                        ),
                    ),
                    ft.ElevatedButton(
                        text="Picture Match",
                        on_click=lambda e: page.go("/editor/text"),
                        width=150,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding(10, 5, 10, 5),
                            bgcolor="#2196f3",
                            color="white",
                            overlay_color="#1976d2",
                        ),
                    ),
                    ft.ElevatedButton(
                        text="Underlined Text",
                        on_click=lambda e: page.go("/editor/text"),
                        width=150,
                        height=50,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.Padding(10, 5, 10, 5),
                            bgcolor="#2196f3",
                            color="white",
                            overlay_color="#1976d2",
                        ),
                    ),
                ],
                expand=1,
                runs_count=3,
                max_extent=150,
                child_aspect_ratio=1.0,
                spacing=5,
                run_spacing=5,
            )

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.selection_options,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
            ),
        )


    
