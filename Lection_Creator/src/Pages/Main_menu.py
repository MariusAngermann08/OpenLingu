import flet as ft
from math import pi

class LectionButton(ft.ElevatedButton):
    def __init__(self, page, language: str, lection: str, index: int, on_select):
        super().__init__()
        self.page = page
        self.language = language
        self.lection = lection
        self.index = index
        self.on_select_callback = on_select
        self.selected = False

        self.text = f"Lektion {index + 1}: {lection}"
        self.width = 300
        self.height = 50
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            bgcolor="#ffffff",
            color="#1a1a1a",
            overlay_color="#e3f2fd",
            shadow_color="#dadce0",
            elevation=1,
            animation_duration=200,
        )
        self.on_click = self.handle_click

    def handle_click(self, e):
        self.selected = not self.selected
        self.update_style()
        self.on_select_callback(self, self.language, self.lection, self.selected)

    def update_style(self):
        if self.selected:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                bgcolor="#e8f0fe",
                color="#1a73e8",
                overlay_color="#d2e3fc",
                side=ft.border.BorderSide(2, "#1a73e8"),
                shadow_color="#c6dafc",
                elevation=2,
                animation_duration=200,
            )
        else:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                bgcolor="#ffffff",
                color="#1a1a1a",
                overlay_color="#e3f2fd",
                shadow_color="#dadce0",
                elevation=1,
                animation_duration=200,
            )
        self.update()

class ExpandableLanguage(ft.Container):
    def __init__(self, page: ft.Page, language: str, lections: list, on_lection_select):
        super().__init__(animate_rotation=True)
        self.page = page
        self.expanded = False
        self.language = language
        self.lections = lections
        self.on_lection_select = on_lection_select
        self.lection_buttons = {}

        self.expand_icon = ft.Icon(
            "chevron_right",
            animate_rotation=ft.Animation(300, curve="ease"),
            color="#5f6368"
        )


        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(language, size=20, weight=ft.FontWeight.BOLD, color="#202124"),
                    ft.Container(expand=True),
                    self.expand_icon
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=14, horizontal=20),
            border_radius=12,
            bgcolor="#ffffff",
            on_click=self.toggle_expand,
            border=ft.border.all(1, "#e0e0e0"),
            shadow=ft.BoxShadow(
                blur_radius=4,
                spread_radius=1,
                color="#00000012",
                offset=ft.Offset(0, 1),
            )
        )

        self.lection_buttons_container = ft.Column(
            spacing=8,
            visible=False,
            animate_opacity=ft.Animation(200, "easeInOut"),
        )

        for i, lection in enumerate(lections):
            btn = LectionButton(
                page=page,
                language=language,
                lection=lection,
                index=i,
                on_select=self.on_lection_select
            )
            self.lection_buttons[lection] = btn
            self.lection_buttons_container.controls.append(btn)

        self.content = ft.Column(
            [
                self.header,
                ft.Container(
                    content=self.lection_buttons_container,
                    padding=ft.padding.only(left=20, top=8, bottom=8, right=0),
                )
            ],
            spacing=0,
        )
    def toggle_expand(self, e):
        self.expanded = not self.expanded
        self.lection_buttons_container.visible = self.expanded
        self.expand_icon.rotate = pi / 2 if self.expanded else 0
        self.update()
    
    def select_lection(self, lection_name, selected):
        if lection_name in self.lection_buttons:
            self.lection_buttons[lection_name].selected = selected
            self.lection_buttons[lection_name].update_style()
class MainMenu(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor="#f5f5f5"
        )
        self.page = page
        self.selected_lections = set()  # Store (language, lection) tuples
        self.app_bar_actions = []
        self.app_bar = None
        
        # Sample data - in a real app, this would come from a database
        self.languages = {
            "Deutsch": ["Grundlagen", "Einführung", "Grammatik"],
            "English": ["Basics", "Introduction", "Grammar"],
            "Español": ["Básico", "Introducción", "Gramática"]
        }
        
        # Create language sections
        self.language_sections = {}
        language_sections = []
        for language, lections in self.languages.items():
            language_section = ExpandableLanguage(
                page=page,
                language=language,
                lections=lections,
                on_lection_select=self.handle_lection_select
            )
            self.language_sections[language] = language_section
            language_sections.append(language_section)
        
        # Create create button
        create_button = ft.FloatingActionButton(
            icon="add",
            text="Create",
            on_click=self.on_create_click,
            bgcolor="#1a73e8",
            width=140,
            height=48,
            shape=ft.RoundedRectangleBorder(radius=24),
        )
        
        # Main content
        self.content = ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Meine Lektionen", size=28, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=24, color="transparent"),
                            *language_sections,
                            ft.Divider(height=16, color="transparent"),
                        ],
                        spacing=16,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=create_button,
                    alignment=ft.alignment.bottom_right,
                    padding=ft.padding.all(20),
                )
            ],
            expand=True,
        )
    
    def on_lesson_click(self, e):
        # Handle lesson button click
        pass
    
    def on_create_click(self, e):
        # Handle create button click
        pass
    
    def create_app_bar(self):
        # Create action buttons (initially hidden)
        self.edit_button = ft.IconButton(
            "edit",
            tooltip="Edit Lection",
            icon_color="white",
            on_click=self.on_edit_lection,
            visible=False
        )
        
        self.delete_button = ft.IconButton(
            "delete",
            tooltip="Delete Lection",
            icon_color="white",
            on_click=self.on_delete_lection,
            visible=False
        )
        
        self.cancel_button = ft.IconButton(
            "close",
            tooltip="Cancel",
            icon_color="white",
            on_click=self.on_cancel_selection,
            visible=False
        )
        
        self.app_bar_actions = [
            self.edit_button,
            self.delete_button,
            self.cancel_button,
            ft.IconButton("account_circle", tooltip="Profile"),
        ]
        
        self.app_bar = ft.AppBar(
            title=ft.Text("Lection Creator", color="white"),
            center_title=False,
            bgcolor="#1a73e8",
            actions=self.app_bar_actions
        )
        return self.app_bar
    
    def handle_lection_select(self, button, language, lection, selected):
        lection_key = (language, lection)
        
        if selected:
            self.selected_lections.add(lection_key)
            # Deselect all other lections
            for lang, sect in self.language_sections.items():
                for lec in self.languages[lang]:
                    if (lang, lec) != lection_key:
                        sect.select_lection(lec, False)
                        self.selected_lections.discard((lang, lec))
        else:
            self.selected_lections.discard(lection_key)
        
        # Update app bar actions visibility
        has_selection = len(self.selected_lections) > 0
        self.edit_button.visible = len(self.selected_lections) == 1
        self.delete_button.visible = has_selection
        self.cancel_button.visible = has_selection
        
        if self.app_bar:
            self.app_bar.update()
    
    def on_edit_lection(self, e):
        if self.selected_lections:
            language, lection = next(iter(self.selected_lections))
            print(f"Editing {language} - {lection}")
            # TODO: Implement edit functionality
    
    def on_delete_lection(self, e):
        if self.selected_lections:
            language, lection = next(iter(self.selected_lections))
            print(f"Deleting {language} - {lection}")
            # TODO: Implement delete functionality
            # After deletion, clear selection
            self.clear_selection()
    
    def on_cancel_selection(self, e):
        self.clear_selection()
    
    def clear_selection(self):
        self.selected_lections.clear()
        for language, section in self.language_sections.items():
            for lection in self.languages[language]:
                section.select_lection(lection, False)
        
        # Hide action buttons
        self.edit_button.visible = False
        self.delete_button.visible = False
        self.cancel_button.visible = False
        
        if self.app_bar:
            self.app_bar.update()