import flet as ft


class PageNavigator(ft.Container):
    def __init__(self, page_index: int, page_count: int, on_back, on_next, on_add):
        super().__init__(
            padding=10,
            border_radius=12,
            bgcolor="#f5f5f5",
            shadow=ft.BoxShadow(blur_radius=6, color="#00000011", offset=ft.Offset(2, 2)),
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_LEFT,
                        tooltip="Previous Page",
                        on_click=on_back,
                        icon_color="#1565C0",
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            overlay_color="#e0e0e0",
                        )
                    ),
                    ft.Text(
                        f"{page_index + 1} / {page_count}",
                        size=16,
                        weight=ft.FontWeight.W_500,
                        color="#333333"
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_RIGHT,
                        tooltip="Next Page",
                        on_click=on_next,
                        icon_color="#1565C0",
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            overlay_color="#e0e0e0",
                        )
                    ),
                    ft.Container(width=20),  # spacing
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        tooltip="Add New Page",
                        bgcolor="#1976D2",
                        mini=True,
                        on_click=on_add,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            )
        )






class EditorField(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page
        self.page_index = 0
        self.page_count = 5  # or dynamically set this

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )

        self.navigator = PageNavigator(
            page_index=self.page_index,
            page_count=self.page_count,
            on_back=self.go_to_previous_page,
            on_next=self.go_to_next_page,
            on_add=self.add_new_page
        )

        self.field = ft.Container(
            content=None,
            expand=True,
            bgcolor="#4CAF50",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(3, 3)),
            padding=30,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.navigator,
                    self.field,
                    ft.Text("Editor Panel", size=18, weight=ft.FontWeight.W_600)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
            ),
        )

    def go_to_previous_page(self, e=None):
        if self.page_index > 0:
            self.page_index -= 1
            self.update_navigator()

    def go_to_next_page(self, e=None):
        if self.page_index < self.page_count - 1:
            self.page_index += 1
            self.update_navigator()

    def add_new_page(self, e=None):
        self.page_count += 1
        self.page_index = self.page_count - 1
        self.update_navigator()

    def update_navigator(self):
        # Re-create the navigator with updated values
        self.navigator.content.controls[1].value = f"{self.page_index + 1} / {self.page_count}"
        self.navigator.update()



class EditorSelection(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )

        self.selection_options = ft.Container(
            content=ft.Column([
                ft.Text("Select Activity Type", size=18, weight=ft.FontWeight.W_600, color="white"),
                ft.GridView(
                    controls=[
                        self._build_button("Matchable Pairs"),
                        self._build_button("Gap Text"),
                        self._build_button("Picture Match"),
                        self._build_button("Underlined Text"),
                    ],
                    expand=True,
                    runs_count=2,
                    max_extent=300,
                    child_aspect_ratio=3.0,
                    spacing=12,
                    run_spacing=12,
                )
            ]),
            padding=20,
            bgcolor="#1976D2",  # deeper blue
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(3, 3)),
            alignment=ft.alignment.center,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.selection_options
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
            ),
        )

    def _build_button(self, text: str) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            text=text,
            on_click=lambda e: self.page.go("/editor/text"),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(10, 5, 10, 5),
                bgcolor="#64B5F6",
                color="white",
                overlay_color="#42A5F5",
                elevation=2,
            ),
            height=50,
        )


class MainEditor(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )

        self.editor_field = EditorField(page)
        self.editor_selection = EditorSelection(page)

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Lection Name:", size=20, weight=ft.FontWeight.W_600),
                                ft.TextField(
                                    label="Enter lection name",
                                    expand=True,
                                    border_radius=8,
                                    filled=True,
                                    bgcolor="#ffffff",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(16, 10, 16, 10),
                        bgcolor="#eeeeee",
                        border_radius=16,
                        shadow=ft.BoxShadow(blur_radius=8, color="#00000010", offset=ft.Offset(2, 2)),
                    ),
                    ft.Row(
                        [
                            self.editor_field,
                            self.editor_selection,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        expand=True,
                    )
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            ),
            padding=20,
        )

    def create_app_bar(self):
        self.save_button = ft.IconButton(
            icon="save",
            tooltip="Save Lection",
            icon_color="white",
            on_click=self.save_lection,
            visible=True
        )

        self.app_bar_actions = [
            self.save_button,
            ft.IconButton(icon="account_circle", tooltip="Profile", icon_color="white"),
        ]

        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white", weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor="#1565C0",
            elevation=4,
            actions=self.app_bar_actions
        )
        return self.app_bar

    def save_lection():
        pass
