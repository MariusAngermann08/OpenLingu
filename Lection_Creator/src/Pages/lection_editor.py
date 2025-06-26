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


    
