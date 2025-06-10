import flet as ft
import random
import asyncio
import time


# Unterstrichener Text, Underlined Text("Dies ist ein Beispieltext mit einigen unterstrichenen Wörtern",{3 : "red", 5: "blue"}, 32, "green")
class UnderlinedText:
    def __init__(
        self,
        text: str,
        underlined: dict[int, str],
        font_size: float = 14,
        bgcolor: str = None
    ):
        self.text = text
        self.underlined = underlined
        self.font_size = font_size
        self.bgcolor = bgcolor

    def render(self) -> ft.Container:
        words = self.text.split(" ")
        spans = []

        for i, word in enumerate(words):
            if i in self.underlined:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.UNDERLINE,
                            decoration_color=self.underlined[i],
                            size=self.font_size  # <-- Set font size here!
                        )
                    )
                )
            else:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            size=self.font_size  # <-- Set font size here!
                        )
                    )
                )

        return ft.Container(
            bgcolor=self.bgcolor,
            padding=10,
            border_radius=5,
            content=ft.Text(
                spans=spans,
                selectable=True
            )
        )

# Matchable Pairs Class
class MatchablePairs:
    def __init__(self, page, left_items: list[str], right_items: list[str]):
        super().__init__()
        assert len(left_items) == len(right_items)

        self.page = page

        self.original_pairs = list(zip(left_items, right_items))
        self.left_items = list(enumerate(left_items))
        self.right_items = list(enumerate(right_items))

        random.shuffle(self.left_items)
        random.shuffle(self.right_items)

        self.selected_left = None
        self.selected_right = None

        self.last_left_highlight = None
        self.last_right_highlight = None

        self.buttons_left = []
        self.buttons_right = []

    def build(self):
        self.left_column = ft.Column()
        self.right_column = ft.Column()

        for idx, word in self.left_items:
            btn = ft.ElevatedButton(
                text=word,
                width=150,
                on_click=lambda e, i=idx: self.left_click(i)
            )
            self.buttons_left.append((idx, btn))
            self.left_column.controls.append(btn)

        for idx, word in self.right_items:
            btn = ft.ElevatedButton(
                text=word,
                width=150,
                on_click=lambda e, i=idx: self.right_click(i)
            )
            self.buttons_right.append((idx, btn))
            self.right_column.controls.append(btn)

        return ft.Row([self.left_column, self.right_column],
                      alignment=ft.MainAxisAlignment.CENTER,
                      spacing=50)

    def get_button(self, idx, side):
        btn_list = self.buttons_left if side == "left" else self.buttons_right
        for i, btn in btn_list:
            if i == idx:
                return btn
        return None

    def highlight_selection(self, side, idx):
        # Alte Auswahl zurücksetzen
        if side == "left" and self.last_left_highlight is not None:
            old_btn = self.get_button(self.last_left_highlight, "left")
            if old_btn and not old_btn.disabled:
                old_btn.style = None
                old_btn.update()
        elif side == "right" and self.last_right_highlight is not None:
            old_btn = self.get_button(self.last_right_highlight, "right")
            if old_btn and not old_btn.disabled:
                old_btn.style = None
                old_btn.update()

        # Neue Auswahl blau markieren
        btn = self.get_button(idx, side)
        if btn and not btn.disabled:
            btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE)
            btn.update()

        # Speichern
        if side == "left":
            self.last_left_highlight = idx
        else:
            self.last_right_highlight = idx

    def left_click(self, idx):
        self.selected_left = idx
        self.highlight_selection("left", idx)
        if self.selected_right is not None:
            self.check_pair()

    def right_click(self, idx):
        self.selected_right = idx
        self.highlight_selection("right", idx)
        if self.selected_left is not None:
            self.check_pair()

    def check_pair(self):
        left_btn = self.get_button(self.selected_left, "left")
        right_btn = self.get_button(self.selected_right, "right")
        correct = self.selected_left == self.selected_right

        if correct:
            for btn in [left_btn, right_btn]:
                btn.disabled = True
                btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREEN)
                btn.update()
            # Nach kurzer Zeit beide Buttons auf gleiche Zufallsfarbe setzen
            self.page.run_task(self.set_random_color_after_delay, left_btn, right_btn)
            self.reset_selection()
        else:
            for btn in [left_btn, right_btn]:
                btn.style = ft.ButtonStyle(bgcolor=ft.Colors.RED)
                btn.update()
            self.page.run_task(self.reset_incorrect_with_delay, left_btn, right_btn)

    async def set_random_color_after_delay(self, left_btn, right_btn):
        await asyncio.sleep(0.6)
        color = self.get_random_color()
        for btn in [left_btn, right_btn]:
            btn.style = ft.ButtonStyle(bgcolor=color)
            btn.update()

    def get_random_color(self):
        # Liste von Farben, die NICHT blau, grün oder rot sind
        forbidden = {ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.RED}
        color_choices = [
            ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.BROWN, ft.Colors.YELLOW,
            ft.Colors.PINK, ft.Colors.CYAN, ft.Colors.LIME, ft.Colors.INDIGO,
            ft.Colors.AMBER, ft.Colors.DEEP_ORANGE, ft.Colors.DEEP_PURPLE,
            ft.Colors.LIGHT_GREEN, ft.Colors.LIGHT_BLUE, ft.Colors.TEAL,
            ft.Colors.GREY
        ]
        # Filtere verbotene Farben raus
        color_choices = [c for c in color_choices if c not in forbidden]
        return random.choice(color_choices)

    async def reset_incorrect_with_delay(self, left_btn, right_btn):
        time.sleep(0.6)
        self.reset_incorrect(left_btn, right_btn)

    def reset_selection(self):
        # Auswahl und Hervorhebung zurücksetzen
        if self.last_left_highlight is not None:
            btn = self.get_button(self.last_left_highlight, "left")
            if btn and not btn.disabled:
                btn.style = None
                btn.update()

        if self.last_right_highlight is not None:
            btn = self.get_button(self.last_right_highlight, "right")
            if btn and not btn.disabled:
                btn.style = None
                btn.update()

        self.selected_left = None
        self.selected_right = None
        self.last_left_highlight = None
        self.last_right_highlight = None

    def reset_incorrect(self, left_btn, right_btn):
        for btn in [left_btn, right_btn]:
            if btn and not btn.disabled:
                btn.style = None
                btn.update()
        self.reset_selection()
