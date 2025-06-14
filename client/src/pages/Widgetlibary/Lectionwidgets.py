import flet as ft
import random
import asyncio
import time
import json


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

    def get_distinct_color(self):
        distinct_colors = [
            ft.Colors.ORANGE,
            ft.Colors.PURPLE,
            ft.Colors.BROWN,
            ft.Colors.YELLOW,
            ft.Colors.PINK,
            ft.Colors.AMBER,
            ft.Colors.LIME,
            ft.Colors.INDIGO,
            ft.Colors.GREY,
            ft.Colors.CYAN,
            ft.Colors.TEAL,
        ]
        # Bereits vergebene Farben sammeln
        used_colors = set(getattr(btn, "bgcolor", None) for _, btn in self.buttons_left + self.buttons_right if btn.disabled)
        # Nur erlaubte und noch nicht vergebene Farben nehmen
        available = [c for c in distinct_colors if c not in used_colors]
        if not available:
            # Falls alle Farben vergeben sind, nimm eine beliebige erlaubte
            available = [c for c in distinct_colors]
        return available
    
    async def set_random_color_after_delay(self, left_btn, right_btn):
        await asyncio.sleep(0.6)
        color = self.get_distinct_color()
        for btn in [left_btn, right_btn]:
            btn.style = ft.ButtonStyle(bgcolor=color)
            btn.update()

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
    
    def check_all_solved(self):
        # Returns True if all left and right buttons are disabled (i.e., all pairs solved)
        all_left_disabled = all(btn.disabled for _, btn in self.buttons_left)
        all_right_disabled = all(btn.disabled for _, btn in self.buttons_right)
        if all_left_disabled and all_right_disabled:
            return True
        else:
            return False  # Immer True oder False jenachdem ob alle Buttons disabled sind

class PictureDrag:
    def __init__(self, page: ft.Page, image_path: str, options: list[str], correct_option_index: int):
        self.page = page
        self.image_path = image_path
        self.options = list(enumerate(options))
        self.correct_option_index = correct_option_index

        self.drop_container = None
        self.buttons = []
        self.correct = False

    def drag_will_accept(self, e):
        idx = str(e.data)
        e.control.content.border = ft.border.all(
            2, ft.Colors.GREEN if idx == self.correct_option_index else ft.Colors.RED
        )
        e.control.update()

    def drag_leave(self, e):
        e.control.content.border = None
        e.control.update()

    def drag_accept(self, e: ft.DragTargetEvent):
        try:
            # falls Flet ein JSON liefert, extrahiere den src_id und hole darüber den Draggable
            dragged_idx = int(e.data)
        except ValueError:
            try:
                data_obj = json.loads(e.data)
                src_control = self.page.get_control(data_obj["src_id"])
                dragged_idx = int(src_control.data)  # <- hier liest du dann `data` korrekt aus
            except Exception as ex:
                print("FEHLER beim Parsen von Drag-Daten:", ex)
                return  # abbrechen

        self.correct = dragged_idx == self.correct_option_index
        color = ft.Colors.GREEN if self.correct else ft.Colors.RED

        # Drop-Ziel einfärben
        e.control.content.bgcolor = color
        e.control.content.border = None
        e.control.update()

        # gezogener Button einfärben
        for idx, container in self.buttons:
            if idx == dragged_idx:
                container.bgcolor = color
                container.update()
                break


        # Rücksetzen bei Fehler
        if not self.correct:
            async def reset_task():
                await asyncio.sleep(1)
                self.correct = False
                e.control.content.bgcolor = ft.Colors.BLUE_GREY_100
                e.control.update()
                for _, container in self.buttons:
                        container.bgcolor = ft.Colors.BLUE_GREY_100
                        container.update()
        else:
            print("task solved")


            self.page.run_task(reset_task)

    def build(self):
        image = ft.Image(src=self.image_path, width=200, height=200, fit=ft.ImageFit.CONTAIN)

        self.buttons.clear()
        drag_row = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        for idx, option in self.options:
            container = ft.Container(
                width=100,
                height=100,
                bgcolor=ft.Colors.BLUE_GREY_100,
                border_radius=5,
                alignment=ft.alignment.center,
                content=ft.Text(option, size=24, color=ft.Colors.WHITE),
            )
            drag = ft.Draggable(
                content=container,
                data=str(idx),
                group="answers"
            )
            self.buttons.append((idx, container))
            drag_row.controls.append(drag)

        drop_target = ft.DragTarget(
            group="answers",
            content=ft.Container(
                width=100,
                height=100,
                bgcolor=ft.Colors.BLUE_GREY_100,
                border_radius=5,
            ),
            on_will_accept=self.drag_will_accept,
            on_accept=self.drag_accept,
            on_leave=self.drag_leave,
        )

        return ft.Column(
            [image, drop_target, drag_row],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    def is_correct(self):
        return self.correct