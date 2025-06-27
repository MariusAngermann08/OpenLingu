import flet as ft
import os
import sys
from pathlib import Path
import json

# Versuche, die Widgets zu importieren, ansonsten hilfreiche Debug-Infos ausgeben
try:
    from Pages.Creator_widgets import MatchablePairs, MatchablePairsCreator, DraggableText, DraggableTextCreator
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
        self.pages_content = [[]]  # Each page is a list of widget configs
        self.page_count = len(self.pages_content)

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
            content=ft.Column(
                [],  # Start empty, will be filled in update_view
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
            ),
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
            self.update_view()

    def go_to_next_page(self, e=None):
        if self.page_index < self.page_count - 1:
            self.page_index += 1
            self.update_view()

    def add_new_page(self, e=None):
        # Neue leere Seite hinzufügen (kannst du später anpassen)
        self.pages_content.append([])  # New page is an empty list of widget configs
        self.page_count = len(self.pages_content)
        self.page_index = self.page_count - 1
        self.update_view()

    def update_view(self):
        self.navigator.content.controls[1].value = f"{self.page_index + 1} / {self.page_count}"
        self.editor_panel_label.value = f"Editor Panel - Seite {self.page_index + 1}"

        # Clear and rebuild all widgets for this page
        self.field.content.controls.clear()
        for i, widget_cfg in enumerate(self.pages_content[self.page_index]):
            if i > 0:
                self.field.content.controls.append(ft.Divider())
            widget = self.build_widget_from_config(widget_cfg)
            self.field.content.controls.append(widget)
        self.field.content.update()
        self.update()

    def set_editor_content(self, content: ft.Control, label: str = "Editor Panel", config=None):
        # Save config (type, data) instead of widget instance
        if config is None:
            config = {"type": "custom", "data": content}
        self.pages_content[self.page_index].append(config)
        self.update_view()
        self.editor_panel_label.value = label
        self.update()

    def build_widget_from_config(self, config):
        if config["type"] == "gap_text":
            # Always create a new DraggableText for unsolved state
            return DraggableText(self.page, config["data"]["text"], config["data"]["gaps"], config["data"]["options"]).build()
        elif config["type"] == "matchable_pairs":
            return MatchablePairs(self.page, config["data"]["left"], config["data"]["right"]).build()
        # Add more types as needed
        elif config["type"] == "custom":
            return config["data"]
        elif config["type"] == "plain_text":
            return ft.Text(config["data"]["text"], size=18)
        return ft.Text("Unbekannter Widget-Typ")


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

    def show_editor_ui(self, editor_ui):
        self.content.content = editor_ui
        self.content.update()

    def on_editor_selected(self, editor_type: str):
        editor_map = {
            "Matchable Pairs": self.build_matchable_pairs_editor,
            "Gap Text": self.build_gap_text_editor,
            "Plain Text": self.build_plain_text_editor,  # <-- add this line
            # Weitere Editoren können hier ergänzt werden
        }
        if editor_type in editor_map:
            editor_ui = editor_map[editor_type]()
            self.show_editor_ui(editor_ui)

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
                            self._build_button("Underlined Text"),
                            self._build_button("Plain Text")
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

    # — Matchable Pairs Editor, unverändert —
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
            self.on_select_editor_callback(
                None,
                "Matchable Pairs Aktivität",
                config={
                    "type": "matchable_pairs",
                    "data": {
                        "left": list(self.left_items),
                        "right": list(self.right_items)
                    }
                }
            )
            self.show_editor_ui(self._build_selection_options())

        return ft.Container(
            content=ft.Column(
                [
                    ft.ElevatedButton(
                        "Zurück",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",
                    ),
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
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
            ),
            expand=True,
            bgcolor="#fff",
            border_radius=12,
            padding=16,
        )

    # — NEUER GAP TEXT EDITOR (smooth, funktional, clean) —

    def build_gap_text_editor(self) -> ft.Control:
        self.text_field = ft.TextField(
            label="Text mit Lücken (Cursor an gewünschte Stelle setzen, dann Lücke einfügen)",
            multiline=True,
            filled=True,
            border_radius=8,
            min_lines=5,
            expand=True,
        )
        self.gaps_idx = []
        self.options = []
        self.options_container = ft.Column(spacing=10, expand=True)

        def update_gaps():
            text = self.text_field.value or ""
            words = text.split(" ")
            self.gaps_idx = [i for i, w in enumerate(words) if w == "_____"]
            update_option_dropdowns()

        def add_option(e):
            if not self.gaps_idx:
                self.page.snack_bar = ft.SnackBar(ft.Text("Bitte zuerst mindestens eine Lücke im Text einfügen!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            option = {"word": "", "gap_idx": 0}
            self.options.append(option)
            render_options()

        def insert_gap(e):
            text = self.text_field.value or ""
            gap_placeholder = "_____"
            new_text = text + " " + gap_placeholder
            self.text_field.value = new_text
            self.text_field.update()
            update_gaps()

        def update_option_dropdowns():
            # Optional: update dropdowns if gaps change
            pass

        def render_options():
            self.options_container.controls.clear()
            for i, option in enumerate(self.options):
                word_field = ft.TextField(
                    label="Option Wort",
                    value=option["word"],
                    width=220,
                    on_change=lambda e, opt=option: update_word(opt, e.control.value),
                    filled=True,
                    border_radius=8,
                )

                dropdown_options = [ft.dropdown.Option(str(idx)) for idx in range(len(self.gaps_idx))]
                dropdown_options.append(ft.dropdown.Option("99", "Incorrect Option"))

                gap_dropdown = ft.Dropdown(
                    label="Lücke auswählen",
                    width=140,
                    options=dropdown_options,
                    value=str(option["gap_idx"]),  # always string for dropdown
                    on_change=lambda e, opt=option: update_gap_idx(opt, e.control.value),
                )

                delete_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="red",
                    tooltip="Option löschen",
                    on_click=lambda e, idx=i: delete_option(idx),
                )

                option_row = ft.Row(
                    [
                        word_field,
                        gap_dropdown,
                        delete_button,
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                self.options_container.controls.append(option_row)
            self.options_container.update()

        def update_word(option, new_word):
            option["word"] = new_word

        def update_gap_idx(option, new_idx):
            try:
                idx = int(new_idx)
                if (0 <= idx < len(self.gaps_idx)) or idx == 99:
                    option["gap_idx"] = idx  # store as int!
            except Exception:
                pass

        def delete_option(index):
            self.options.pop(index)
            render_options()

        def finish_editor(e):
            # Validation
            if not self.gaps_idx:
                self.page.snack_bar = ft.SnackBar(ft.Text("Keine Lücken im Text gefunden!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not self.options:
                self.page.snack_bar = ft.SnackBar(ft.Text("Bitte mindestens eine Option hinzufügen!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            assigned_indices = {opt["gap_idx"] for opt in self.options if opt["gap_idx"] != 99}
            missing = [i for i in range(len(self.gaps_idx)) if i not in assigned_indices]
            if missing:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Lücke(n) {missing} ohne zugeordnete Option!"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            # Prepare data for DraggableText
            text = self.text_field.value
            options = {opt["word"]: opt["gap_idx"] for opt in self.options}
            gaps = self.gaps_idx

            # Add to page and reset editor UI
            self.on_select_editor_callback(
                None,
                "Gap Text Aktivität",
                config={"type": "gap_text", "data": {"text": text, "gaps": gaps, "options": options}}
            )
            self.show_editor_ui(self._build_selection_options())

        # --- Build the UI ---
        return ft.Container(
            content=ft.Column(
                [   ft.ElevatedButton(
                        "Zurück",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",),
                    ft.Text("Lückentext erstellen", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.text_field,
                            ft.Column(
                                [
                                    ft.ElevatedButton("Lücke einfügen", icon=ft.Icons.ADD, on_click=insert_gap),
                                    ft.ElevatedButton("Option hinzufügen", icon=ft.Icons.ADD, on_click=add_option),
                                    ft.ElevatedButton(
                                        "Fertig",
                                        icon=ft.Icons.CHECK,
                                        on_click=finish_editor,
                                        bgcolor="#4CAF50",
                                        color="white",
                                    ),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.START,
                            ),
                        ],
                        spacing=20,
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.Divider(),
                    self.options_container,
                ],
                spacing=15,
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,  # <-- PUT IT HERE!
            ),
            expand=True,
            bgcolor="#fff",
            border_radius=12,
            padding=16,
        )

    def build_plain_text_editor(self) -> ft.Control:
        self.plain_text_field = ft.TextField(
            label="Einfacher Text",
            multiline=True,
            filled=True,
            border_radius=8,
            min_lines=5,
            expand=True,
        )

        def finish_editor(e):
            text = self.plain_text_field.value.strip()
            if not text:
                self.page.snack_bar = ft.SnackBar(ft.Text("Bitte Text eingeben!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            self.on_select_editor_callback(
                None,
                "Plain Text",
                config={"type": "plain_text", "data": {"text": text}}
            )
            self.show_editor_ui(self._build_selection_options())

        return ft.Container(
            content=ft.Column(
                [
                    ft.ElevatedButton(
                        "Zurück",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",
                    ),
                    ft.Text("Einfachen Text hinzufügen", size=20, weight=ft.FontWeight.BOLD),
                    self.plain_text_field,
                    ft.ElevatedButton(
                        "Fertig",
                        icon=ft.Icons.CHECK,
                        on_click=finish_editor,
                        bgcolor="#4CAF50",
                        color="white",
                    ),
                ],
                spacing=15,
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
            ),
            expand=True,
            bgcolor="#fff",
            border_radius=12,
            padding=16,
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

    def show_editor_ui(self, editor_ui):
        self.content.content = editor_ui
        self.content.update()
        ft.ElevatedButton(
            "Zurück",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
            bgcolor="#bbbbbb",
            color="black",
        )
