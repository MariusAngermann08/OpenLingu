import flet as ft
import os
import sys
from pathlib import Path

# Versuche, die Widgets zu importieren, ansonsten hilfreiche Debug-Infos ausgeben
try:
    from Pages.Creator_widgets import MatchablePairs, MatchablePairsCreator
except ImportError as e:
    print(f"Fehler beim Importieren der Widgets: {e}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    raise


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
                        tooltip="Vorherige Seite",
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
                        weight=ft.FontWeight.W_600,
                        color="#000000",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_RIGHT,
                        tooltip="Nächste Seite",
                        on_click=on_next,
                        icon_color="#1565C0",
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            overlay_color="#e0e0e0",
                        )
                    ),
                    ft.Container(width=20),  # Abstand
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        tooltip="Neue Seite hinzufügen",
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
        self.page_count = 5

        self.navigator = PageNavigator(
            page_index=self.page_index,
            page_count=self.page_count,
            on_back=self.go_to_previous_page,
            on_next=self.go_to_next_page,
            on_add=self.add_new_page,
        )

        self.field = ft.Container(
            expand=True,
            bgcolor="#fefefe",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(3, 3)),
            padding=30,
            content=None,
        )

        self.editor_panel_label = ft.Text("Editor Panel", size=18, weight=ft.FontWeight.W_600)

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    self.navigator,
                    self.field,
                    self.editor_panel_label,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                expand=True,
            )
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
        # Aktualisiere die Seitennummer im Navigator
        self.navigator.content.controls[1].value = f"{self.page_index + 1} / {self.page_count}"
        self.navigator.update()

    def set_editor_content(self, content: ft.Control, label: str = "Editor Panel"):
        self.field.content = content
        self.editor_panel_label.value = label
        self.update()


class EditorSelection(ft.Container):
    def __init__(self, page: ft.Page, on_select_editor_callback):
        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
        )
        self.page = page
        self.on_select_editor_callback = on_select_editor_callback

        self.content = ft.Container(
            content=ft.Column(
                [
                    self._build_selection_options()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True,
            )
        )

    def _build_selection_options(self) -> ft.Container:
        return ft.Container(
            padding=20,
            bgcolor="#1976D2",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(3, 3)),
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Text("Aktivitätstyp auswählen", size=18, weight=ft.FontWeight.W_600, color="white"),
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
                    ),
                ],
                spacing=20,
            )
        )

    def _build_button(self, text: str) -> ft.ElevatedButton:
        return ft.ElevatedButton(
            text=text,
            on_click=lambda e: self.on_editor_selected(text),
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

    def on_editor_selected(self, editor_type: str):
        editor_map = {
            "Matchable Pairs": self.build_matchable_pairs_editor,
            # Weitere Editoren können hier ergänzt werden
        }
        if editor_type in editor_map:
            editor_ui = editor_map[editor_type]()
            self.on_select_editor_callback(editor_ui, f"{editor_type} Editor")

    def build_matchable_pairs_editor(self) -> ft.Control:
        self.left_input = ft.TextField(label="Linker Eintrag", filled=True, border_radius=8)
        self.right_input = ft.TextField(label="Rechter Eintrag", filled=True, border_radius=8)
        self.pairs_display = ft.Column()
        self.left_items = []
        self.right_items = []

        def refresh_pairs_display():
            self.pairs_display.controls.clear()
            for i, (left, right) in enumerate(zip(self.left_items, self.right_items)):
                pair_text = ft.Text(f"{left} ↔ {right}", expand=True)
                edit_button = ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="Bearbeiten",
                    on_click=lambda e, index=i: edit_pair(index),
                )
                self.pairs_display.controls.append(
                    ft.Row(
                        [pair_text, edit_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )
            self.page.update()

        def add_pair(e):
            left = self.left_input.value.strip()
            right = self.right_input.value.strip()
            if left and right:
                self.left_items.append(left)
                self.right_items.append(right)
                self.left_input.value = ""
                self.right_input.value = ""
                refresh_pairs_display()

        def edit_pair(index: int):
            self.left_input.value = self.left_items[index]
            self.right_input.value = self.right_items[index]
            del self.left_items[index]
            del self.right_items[index]
            refresh_pairs_display()

        def finish_editor(e):
            if len(self.left_items) != len(self.right_items) or not self.left_items:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Ungültige Paare! Bitte mindestens ein gültiges Paar hinzufügen.")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            matchable = MatchablePairs(self.page, self.left_items, self.right_items)
            self.on_select_editor_callback(matchable.build(), "Matchable Pairs Aktivität")

        return ft.Column(
            [
                ft.Text("Matchbare Paare erstellen", size=20, weight=ft.FontWeight.BOLD),
                self.left_input,
                self.right_input,
                ft.Row(
                    [
                        ft.ElevatedButton(text="Paar hinzufügen", icon=ft.Icons.ADD, on_click=add_pair),
                        ft.ElevatedButton(
                            text="Fertig",
                            icon=ft.Icons.CHECK,
                            on_click=finish_editor,
                            bgcolor="#4CAF50",
                            color="white",
                        ),
                    ],
                    spacing=12,
                ),
                ft.Divider(),
                self.pairs_display,
            ],
            spacing=10,
        )


class MainEditor(ft.Container):
    def __init__(self, page: ft.Page):
        self.page = page

        self.editor_field = EditorField(page)
        self.editor_selection = EditorSelection(page, self.editor_field.set_editor_content)

        self.lection_name_field = ft.TextField(
            label="Lection Name",
            hint_text="Name der Lektion eingeben",
            expand=True,
            border_radius=8,
            filled=True,
            bgcolor="#ffffff",
        )

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Lection Name:", size=20, weight=ft.FontWeight.W_600),
                                self.lection_name_field,
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
                        spacing=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            ),
        )

    def create_app_bar(self):
        self.save_button = ft.IconButton(
            icon=ft.Icons.SAVE,
            tooltip="Lection speichern",
            icon_color="white",
            on_click=self.save_lection,
            visible=True,
        )
        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white", weight=ft.FontWeight.BOLD),
            bgcolor="#1565C0",
            elevation=4,
            actions=[
                self.save_button,
                ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, tooltip="Profil", icon_color="white"),
            ],
        )
        return self.app_bar

    def save_lection(self, e):
        # TODO: Implementiere das Speichern
        self.page.snack_bar = ft.SnackBar(ft.Text("Speichern-Funktion noch nicht implementiert."))
        self.page.snack_bar.open = True
        self.page.update()
