import flet as ft
import os
import sys
import time
from pathlib import Path
import json
import requests

# Try to import widgets, otherwise print helpful debug information
try:
    from Pages.Creator_widgets import MatchablePairs, DraggableText, UnderlinedText
except ImportError as e:
    print(f"Error importing widgets: {e}")
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
                        tooltip="Previous page",
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
                        tooltip="Next page",
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
                        tooltip="Add new page",
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

        # Create loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(width=50, height=50, stroke_width=4, color="#1565C0"),
                    ft.Text("Loading lection...", size=16, weight=ft.FontWeight.W_500, color="#555555")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            visible=False,
            bgcolor="#fefefeee",  # Slightly transparent white
            border_radius=16,
            expand=True,
        )
        
        # Create the main content container
        self.field_content = ft.Column(
            [],  # Start empty, will be filled in update_view
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
        )
        
        # Stack the loading indicator on top of the content
        self.field = ft.Container(
            expand=True,
            bgcolor="#fefefe",
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=14, color="#00000033", offset=ft.Offset(3, 3)),
            padding=30,
            content=ft.Stack(
                [
                    self.field_content,
                    self.loading_indicator
                ],
                expand=True,
            ),
        )    

        self.editor_panel_label = ft.Text("Editor Panel - Page 1", size=18, weight=ft.FontWeight.W_600)

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

    def show_loading(self, show: bool = True):
        """Show or hide the loading indicator"""
        self.loading_indicator.visible = show
        self.field_content.visible = not show
        self.update()

    def update_view(self):
        """Update the view to show the current page's widgets"""
        # Show loading indicator while updating
        self.show_loading(True)
        
        try:
            # Clear existing content
            self.field_content.controls.clear()
            
            # Add all widgets from the current page
            if self.pages_content and self.page_index < len(self.pages_content):
                for widget_config in self.pages_content[self.page_index]:
                    widget = self.build_widget_from_config(widget_config)
                    if widget:
                        self.field_content.controls.append(widget)
            
            # Update the page counter
            self.navigator.content.controls[1].value = f"{self.page_index + 1} / {self.page_count}"
            self.editor_panel_label.value = f"Editor Panel - Page {self.page_index + 1}"
            
            # Update the UI
            self.update()
        finally:
            # Hide loading indicator when done
            self.show_loading(False)

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
        elif config["type"] == "underlined_text":
            return UnderlinedText(
                config["data"]["text"],
                config["data"]["underlined"],
                font_size=18,
                bgcolor="#f5f5f5"
            )
        return ft.Text("Unknown widget type")


class EditorSelection(ft.Container):
    def __init__(self, page: ft.Page, on_select_editor_callback, new: bool = False, lection_name: str = "", language: str = "en"):
        super().__init__(
            expand=True,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor="#f5f5f5"
        )
        self.page = page
        self.new = new
        self.lection_name = lection_name
        self.language = language  # Store the selected language
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
            "Plain Text": self.build_plain_text_editor,
            "Underlined Text": self.build_underlined_text_editor,  # <-- add this line
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
                    ft.Text("Select Activity Type", size=18, weight=ft.FontWeight.W_600, color="white"),
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
        self.left_input = ft.TextField(label="Left item", filled=True, border_radius=8)
        self.right_input = ft.TextField(label="Right item", filled=True, border_radius=8)
        self.pairs_display = ft.Column()
        self.left_items = []
        self.right_items = []

        def refresh_pairs_display():
            self.pairs_display.controls.clear()
            for i, (left, right) in enumerate(zip(self.left_items, self.right_items)):
                pair_text = ft.Text(f"{left} ↔ {right}", expand=True)
                edit_button = ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="Edit",
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
                    ft.Text("Invalid pairs! Please add at least one valid pair.")
                )
                self.page.snack_bar.open = True
                self.page.update()
                return
            self.on_select_editor_callback(
                None,
                "Matchable Pairs Activity",
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
                        "Back",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",
                    ),
                    ft.Text("Create Matchable Pairs", size=20, weight=ft.FontWeight.BOLD),
                    self.left_input,
                    self.right_input,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Add pair", icon=ft.Icons.ADD, on_click=add_pair),
                            ft.ElevatedButton(
                                text="Done",
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
            label="Text with gaps (place cursor and click 'Insert Gap' to add a gap)",
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
                self.page.snack_bar = ft.SnackBar(ft.Text("Please add at least one gap in the text first!"))
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
                    label="Option word",
                    value=option["word"],
                    width=220,
                    on_change=lambda e, opt=option: update_word(opt, e.control.value),
                    filled=True,
                    border_radius=8,
                )

                dropdown_options = [ft.dropdown.Option(str(idx)) for idx in range(len(self.gaps_idx))]
                dropdown_options.append(ft.dropdown.Option("99", "Incorrect Option"))

                gap_dropdown = ft.Dropdown(
                    label="Select gap",
                    width=140,
                    options=dropdown_options,
                    value=str(option["gap_idx"]),  # always string for dropdown
                    on_change=lambda e, opt=option: update_gap_idx(opt, e.control.value),
                )

                delete_button = ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color="red",
                    tooltip="Delete option",
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
                self.page.snack_bar = ft.SnackBar(ft.Text("No gaps found in the text!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not self.options:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please add at least one option!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            assigned_indices = {opt["gap_idx"] for opt in self.options if opt["gap_idx"] != 99}
            missing = [i for i in range(len(self.gaps_idx)) if i not in assigned_indices]
            if missing:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Gap(s) {missing} without assigned option!"))
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
                "Gap Text Activity",
                config={"type": "gap_text", "data": {"text": text, "gaps": gaps, "options": options}}
            )
            self.show_editor_ui(self._build_selection_options())

        # --- Build the UI ---
        return ft.Container(
            content=ft.Column(
                [   ft.ElevatedButton(
                        "Back",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",),
                    ft.Text("Create Gap Text", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            self.text_field,
                            ft.Column(
                                [
                                    ft.ElevatedButton("Insert Gap", icon=ft.Icons.ADD, on_click=insert_gap),
                                    ft.ElevatedButton("Add Option", icon=ft.Icons.ADD, on_click=add_option),
                                    ft.ElevatedButton(
                                        "Done",
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
            label="Simple Text",
            multiline=True,
            filled=True,
            border_radius=8,
            min_lines=5,
            expand=True,
        )

        def finish_editor(e):
            text = self.plain_text_field.value.strip()
            if not text:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please enter text!"))
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
                        "Back",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",
                    ),
                    ft.Text("Add Simple Text", size=20, weight=ft.FontWeight.BOLD),
                    self.plain_text_field,
                    ft.ElevatedButton(
                        "Done",
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

    def build_underlined_text_editor(self) -> ft.Control:
        self.underlined_text_field = ft.TextField(
            label="Text with underlines (select text and click 'Underline Selected' to underline)",
            multiline=True,
            filled=True,
            border_radius=8,
            min_lines=3,
            expand=True,
        )
        self.underlined_words = {}  # {word_index: color}
        self.selected_word = None
        self.selected_color = "#1976D2"
        self.words_dropdown = ft.Dropdown(
            label="Select word",
            width=200,
            options=[],
            on_change=lambda e: setattr(self, "selected_word", e.control.value),
        )
        self.color_dropdown = ft.Dropdown(
            label="Select color",
            width=160,
            options=[
                ft.dropdown.Option("#1976D2", "Blue"),
                ft.dropdown.Option("#E53935", "Red"),
                ft.dropdown.Option("#43A047", "Green"),
                ft.dropdown.Option("#FBC02D", "Yellow"),
                ft.dropdown.Option("#8E24AA", "Purple"),
                ft.dropdown.Option("#000000", "Black"),
            ],
            value="#1976D2",
            on_change=lambda e: setattr(self, "selected_color", e.control.value),
        )
        self.underlined_display = ft.Container()
        self.words_row = ft.Row([self.words_dropdown, self.color_dropdown], spacing=12)

        def update_words_dropdown(e=None):
            text = self.underlined_text_field.value or ""
            words = text.split()
            self.words_dropdown.options = [
                ft.dropdown.Option(f"{i}:{w}", w) for i, w in enumerate(words)
            ]
            self.words_dropdown.value = None
            self.words_dropdown.update()

        def add_underlined_word(e):
            if not self.words_dropdown.value:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please select a word!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            idx = int(self.words_dropdown.value.split(":")[0])
            self.underlined_words[idx + 1] = self.selected_color  # <-- Use 1-based index!
            render_underlined_preview()

        def remove_underlined_word(idx1):
            if idx1 in self.underlined_words:
                del self.underlined_words[idx1]
                render_underlined_preview()

        def render_underlined_preview():
            text = self.underlined_text_field.value or ""
            preview = UnderlinedText(text, self.underlined_words, font_size=18, bgcolor="#f5f5f5")
            # Show removable chips for each underlined word
            chips = []
            words = text.split()
            for idx1, color in self.underlined_words.items():
                idx = idx1 - 1  # idx1 is 1-based
                if 0 <= idx < len(words):
                    chips.append(
                        ft.Chip(
                            label=ft.Text(f"{words[idx]}"),
                            bgcolor=color,
                            on_delete=lambda e, i=idx1: remove_underlined_word(i),
                            color="white" if color != "#FBC02D" else "black",
                        )
                    )
            self.underlined_display.content = ft.Column(
                [
                    ft.Text("Preview:", size=16, weight=ft.FontWeight.W_600),
                    preview,
                    ft.Row(chips, spacing=8) if chips else ft.Text("No underlined words."),
                ],
                spacing=8,
            )
            self.underlined_display.update()

        def finish_editor(e):
            text = self.underlined_text_field.value.strip()
            if not text:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please enter text!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not self.underlined_words:
                self.page.snack_bar = ft.SnackBar(ft.Text("Please underline at least one word!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            # Store as string keys (1-based) for config
            config = {
                "type": "underlined_text",
                "data": {
                    "text": text,
                    "underlined": {str(idx): color for idx, color in self.underlined_words.items()}
                }
            }
            print("Saving underlined config:", config)  # DEBUG
            self.on_select_editor_callback(None, "Underlined Text", config=config)
            self.show_editor_ui(self._build_selection_options())

        # Update dropdown when text changes
        self.underlined_text_field.on_change = update_words_dropdown

        return ft.Container(
            content=ft.Column(
                [
                    ft.ElevatedButton(
                        "Back",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
                        bgcolor="#bbbbbb",
                        color="black",
                    ),
                    ft.Text("Underline Selected Words", size=20, weight=ft.FontWeight.BOLD),
                    self.underlined_text_field,
                    self.words_row,
                    ft.ElevatedButton(
                        "Underline Word",
                        icon=ft.Icons.ADD,
                        on_click=add_underlined_word,
                        bgcolor="#1976D2",
                        color="white",
                    ),
                    ft.Divider(),
                    self.underlined_display,
                    ft.ElevatedButton(
                        "Fertig",
                        icon=ft.Icons.CHECK,
                        on_click=finish_editor,
                        bgcolor="#4CAF50",
                        color="white",
                    ),
                ],
                spacing=12,
                expand=True,
                scroll=ft.ScrollMode.ALWAYS,
            ),
            expand=True,
            bgcolor="#fff",
            border_radius=12,
            padding=16,
        )


class MainEditor(ft.Container):
    def __init__(self, page: ft.Page, new: bool, lection_name: str, language: str = "en"):
        self.page = page

        self.new = new
        self.lection_name = lection_name
        self.language = language
        self.lection_data = None

        self.editor_field = EditorField(page)
        self.editor_selection = EditorSelection(
            page=page, 
            on_select_editor_callback=self.editor_field.set_editor_content,
            new=new,
            lection_name=lection_name,
            language=language
        )

        self.lection_name_field = ft.TextField(
            label="Lection Name",
            hint_text="Enter lesson name",
            expand=True,
            value=self.lection_name if not self.new else "New Lection",
            border_radius=8,
            filled=True,
            bgcolor="#ffffff",
        )
        
        self.lection_description_field = ft.TextField(
            label="Description",
            hint_text="Enter lesson description",
            expand=True,
            border_radius=8,
            filled=True,
            bgcolor="#ffffff",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )

        super().__init__(
            expand=True,
            padding=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Lesson Name:", size=20, weight=ft.FontWeight.W_600),
                                        self.lection_name_field,
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Row(
                                    [
                                        ft.Text("Description:", size=16, weight=ft.FontWeight.W_500),
                                        self.lection_description_field,
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                ),
                            ],
                            spacing=10,
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
        
    def did_mount(self):
        # Load existing lection if not creating a new one
        # This runs after the component is mounted and has access to page context
        if not self.new and self.lection_name:
            self._load_existing_lection()

    def _load_existing_lection(self):
        """Load an existing lection from the server and update the editor"""
        # Show loading state
        self.editor_field.show_loading(True)
        self.page.update()
        
        try:
            # Get server URL from client storage
            server_url = self.page.client_storage.get("server_url")
            if not server_url:
                print("Server URL not set")
                self._show_error("Server URL not configured")
                return
                
            # Make the API request to get the lection
            url = f"{server_url.rstrip('/')}/languages/{self.language}/lections/by_title/{self.lection_name}"
            print(f"Fetching lection from: {url}")
            
            # Show loading message
            self.editor_field.loading_indicator.content.controls[1].value = "Fetching lection data..."
            self.editor_field.update()
            
            response = requests.get(url)
            response.raise_for_status()
            
            # Store the raw lection data
            self.lection_data = response.json()
            print("Raw lection data received:", json.dumps(self.lection_data, indent=2))
            
            # Parse the lection data into editor format
            self.editor_field.loading_indicator.content.controls[1].value = "Parsing lection content..."
            self.editor_field.update()
            
            from .lection_parser import LectionParser
            parsed_data = LectionParser.to_editor_format(self.lection_data)
            print("Parsed lection data:", json.dumps(parsed_data, indent=2))
            
            # Update the UI with the parsed data
            self._update_editor_with_lection(parsed_data)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error loading lection: {e}"
            print(error_msg)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error details: {error_data}")
                    error_msg += f"\n{json.dumps(error_data, indent=2)}"
                except:
                    status = getattr(e.response, 'status_code', 'Unknown')
                    text = getattr(e.response, 'text', 'No details')
                    print(f"Status code: {status}")
                    print(f"Response: {text}")
                    error_msg += f"\nStatus: {status}\n{text}"
            self._show_error(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error loading lection: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self._show_error(error_msg)
    
    def _update_editor_with_lection(self, lection_data: dict):
        """Update the editor UI with the loaded lection data"""
        # Update loading message
        self.editor_field.loading_indicator.content.controls[1].value = "Building editor..."
        self.editor_field.update()
        try:
            # Update basic lection info
            self.lection_name_field.value = lection_data.get("title", "")
            self.lection_description_field.value = lection_data.get("description", "")
            
            # Clear existing pages
            self.editor_field.pages_content = []
            
            # Add pages from the lection data
            for page_data in lection_data.get("pages", []):
                self._add_page_from_data(page_data)
            
            # Update the UI
            self.lection_name_field.update()
            self.lection_description_field.update()
            self.editor_field.update_view()
            
            print("Editor updated with lection data")
            
        except Exception as e:
            error_msg = f"Error updating editor with lection data: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self._show_error(error_msg)
    
    def _add_page_from_data(self, page_data: dict):
        """Add a page to the editor from page data"""
        try:
            # Create a new page in the editor
            self.editor_field.add_new_page()
            current_page_idx = len(self.editor_field.pages_content) - 1
            
            # Add widgets to the page
            for widget_data in page_data.get("widgets", []):
                self._add_widget_from_data(current_page_idx, widget_data)
                
        except Exception as e:
            print(f"Error adding page from data: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_widget_from_data(self, page_idx: int, widget_data: dict):
        """Add a widget to a page from widget data"""
        try:
            widget_type = widget_data.get("type")
            data = widget_data.get("data", {})
            
            if widget_type == "text":
                # For plain text, we can directly add it without going through the editor
                config = {
                    "type": "plain_text",
                    "data": {
                        "text": data.get("text", ""),
                        "size": data.get("size", 16),
                        "weight": data.get("weight", "normal")
                    }
                }
                self.editor_field.set_editor_content(None, "Plain Text", config)
                
            elif widget_type == "matchable_pairs":
                # For matchable pairs, we need to set up the editor first
                self.editor_selection.on_editor_selected("Matchable Pairs")
                # Wait for the editor to be ready
                time.sleep(0.1)
                # Create the config for matchable pairs
                config = {
                    "type": "matchable_pairs",
                    "data": {
                        "left": data.get("left_items", []),
                        "right": data.get("right_items", [])
                    }
                }
                # Add the widget with config
                self.editor_field.set_editor_content(None, "Matchable Pairs", config)
                
            elif widget_type == "draggable_text":
                # For gap text, we need to set up the editor first
                self.editor_selection.on_editor_selected("Gap Text")
                # Wait for the editor to be ready
                time.sleep(0.1)
                # Create the config for gap text
                config = {
                    "type": "gap_text",
                    "data": {
                        "text": data.get("text", ""),
                        "gaps": data.get("gaps_idx", []),
                        "options": data.get("options", {})
                    }
                }
                # Add the widget with config
                self.editor_field.set_editor_content(None, "Gap Text Activity", config)
                
            elif widget_type == "underlined_text":
                # For underlined text, we can directly add it without going through the editor
                config = {
                    "type": "underlined_text",
                    "data": {
                        "text": data.get("text", ""),
                        "underlined": data.get("underlined", {})
                    }
                }
                # Add the widget with config
                self.editor_field.set_editor_content(None, "Underlined Text", config)
                
            # Update the view after adding the widget
            self.editor_field.update_view()
            
        except Exception as e:
            print(f"Error adding widget from data: {e}")
            import traceback
            traceback.print_exc()
    
    def close_editor(self, e=None):
        """Close the editor and return to main menu"""
        self.page.go("/main")
        self.page.update()

    def create_app_bar(self):
        # Create save button
        self.save_button = ft.IconButton(
            icon="save",
            tooltip="Save Lection",
            icon_color="#FFFFFF",
            on_click=self.save_lection,
            visible=True,
        )
        
        # Create close button
        self.close_button = ft.IconButton(
            icon="close",
            tooltip="Close Editor",
            icon_color="#FFFFFF",
            on_click=self.close_editor,
        )
        
        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white", weight=ft.FontWeight.BOLD),
            bgcolor="#1565C0",
            elevation=4,
            actions=[
                self.save_button,
                self.close_button,
            ],
        )
        return self.app_bar

    def save_lection(self, e):
        # Show loading indicator
        self.save_button.disabled = True
        self.save_button.text = "Saving..."
        self.page.update()
        
        try:
            # Get server URL and auth token
            server_url = self.page.client_storage.get("server_url")
            auth_token = self.page.client_storage.get("auth_token")
            
            if not server_url or not auth_token:
                self._show_error("Not authenticated. Please log in first.")
                return
                
            # Generate lection data
            lection_data = self.export_lection()
            
            # Prepare headers with auth token
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Get the language name from the URL or use the one from lection_data
            language_name = self.language  # This comes from the URL parameter
            
            if self.new:
                # For new lections
                request_data = {
                    "lection_name": lection_data["title"],
                    "content": lection_data
                }
                endpoint = f"{server_url.rstrip('/')}/add_lection/{language_name}"
                method = requests.post
            else:
                # For existing lections
                request_data = {
                    "lection_name": self.lection_name,  # Original name for identification
                    "content": lection_data
                }
                endpoint = f"{server_url.rstrip('/')}/edit_lection/{language_name}"
                method = requests.put
            
            # Make the request
            response = method(
                endpoint,
                headers=headers,
                json=request_data
            )
            response.raise_for_status()  # Will raise an exception for 4XX/5XX responses
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Lection saved successfully!", color="white"),
                bgcolor="#43a047"
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Navigate back to main menu after a short delay
            def navigate_back():
                # Reset the view to the main menu
                self.page.go("/main")
                # Force a page update to ensure the navigation happens
                self.page.update()
                
            # Use the page's timer to navigate after a delay
            self.page.run_thread(lambda: (time.sleep(1.5), navigate_back()))
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('detail', str(error_data))
                except:
                    error_msg = e.response.text or str(e)
            self._show_error(f"Failed to save lection: {error_msg}")
        except Exception as e:
            self._show_error(f"An error occurred: {str(e)}")
        finally:
            # Re-enable save button
            self.save_button.disabled = False
            self.save_button.text = "Save"
            self.page.update()
            
    def _show_error(self, message):
        """Display an error message to the user"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor="#f44336"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_editor_ui(self, editor_ui):
        self.content.content = editor_ui
        self.content.update()
        ft.ElevatedButton(
            "Back",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self.show_editor_ui(self._build_selection_options()),
            bgcolor="#bbbbbb",
            color="black",
        )

    def export_lection(self, e=None):
        """Export the current lection to JSON format and return as a dictionary"""
        import uuid
        from datetime import datetime
        
        # Basic lection info
        lection_data = {
            "id": f"lection_{uuid.uuid4().hex[:8]}",
            "title": self.lection_name_field.value or "Untitled Lection",
            "description": self.lection_description_field.value or "",
            "language": self.language,  # Use the selected language
            "difficulty": "beginner",  # Default difficulty
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "pages": []
        }
        
        # Convert each page's widgets to the required format
        for page_idx, page_widgets in enumerate(self.editor_field.pages_content):
            if not page_widgets:
                continue
                
            page_data = {
                "title": f"Page {page_idx + 1}",
                "description": f"Description for page {page_idx + 1}",
                "widgets": []
            }
            
            # Use a set to track unique widget indices we've already processed
            processed_indices = set()
            
            for widget in page_widgets:
                # Skip if we've already processed this widget
                widget_id = id(widget)
                if widget_id in processed_indices:
                    continue
                processed_indices.add(widget_id)
                
                widget_type = widget.get("type")
                widget_data = widget.get("data", {})
                
                if not all([widget_type, widget_data]):
                    continue
                
                widget_export = None
                
                if widget_type == "plain_text":
                    widget_export = {
                        "type": "text",
                        "data": {
                            "text": widget_data.get("text", ""),
                            "size": 16,
                            "weight": "normal"
                        }
                    }
                    
                elif widget_type == "underlined_text":
                    widget_export = {
                        "type": "underlined_text",
                        "data": {
                            "text": widget_data.get("text", ""),
                            "underlined": widget_data.get("underlined", {}),
                            "font_size": 16,
                            "bgcolor": "#F0F8FF"
                        }
                    }
                    
                elif widget_type == "matchable_pairs":
                    widget_export = {
                        "type": "matchable_pairs",
                        "data": {
                            "left_items": list(widget_data.get("left", [])),
                            "right_items": list(widget_data.get("right", []))
                        }
                    }
                    
                elif widget_type == "gap_text":
                    widget_export = {
                        "type": "draggable_text",
                        "data": {
                            "text": widget_data.get("text", ""),
                            "gaps_idx": list(widget_data.get("gaps", [])),
                            "options": dict(widget_data.get("options", {}))
                        }
                    }
                
                if widget_export:
                    page_data["widgets"].append(widget_export)
            
            if page_data["widgets"]:  # Only add page if it has widgets
                lection_data["pages"].append(page_data)
        
        return lection_data
        return lection_data
