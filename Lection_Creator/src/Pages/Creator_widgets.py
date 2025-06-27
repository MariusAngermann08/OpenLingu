import flet as ft
import random
import asyncio 
import time

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
            if hasattr(self.page, "notify_task_update"):
                self.page.notify_task_update()
        else:
            for btn in [left_btn, right_btn]:
                btn.style = ft.ButtonStyle(bgcolor=ft.Colors.RED)
                btn.update()
            self.page.run_task(self.reset_incorrect_with_delay, left_btn, right_btn)

    async def set_random_color_after_delay(self, left_btn, right_btn):
        await asyncio.sleep(0.6)
        color = self.get_distinct_color()
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
            ft.Colors.LIGHT_GREEN,
            ft.Colors.LIGHT_BLUE,
        ]

        used_colors = set()
        for _, btn in self.buttons_left + self.buttons_right:
            if btn.disabled and hasattr(btn, "bgcolor") and btn.bgcolor is not None:
                used_colors.add(btn.bgcolor)

        available = [c for c in distinct_colors if c not in used_colors]

        if not available:
            available = distinct_colors  # Wenn alle vergeben, dann wieder freigeben

        color = random.choice(available)
        return color
    
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


class MatchablePairsCreator:
    def __init__(self, page):
        self.page = page
        self.left_inputs = []
        self.right_inputs = []

        self.pair_input_column = ft.Column()
        self.add_input_row()

    def add_input_row(self, left_text="", right_text=""):
        left_field = ft.TextField(label="Left", value=left_text)
        right_field = ft.TextField(label="Right", value=right_text)

        self.left_inputs.append(left_field)
        self.right_inputs.append(right_field)

        row = ft.Row([left_field, right_field])
        self.pair_input_column.controls.append(row)

    def build(self):
        add_pair_button = ft.ElevatedButton(
            text="+ Add Pair",
            on_click=lambda e: self.add_input_row()
        )

        start_button = ft.ElevatedButton(
            text="Start",
            on_click=self.start_game
        )

        return ft.Column([
            ft.Text("Enter your matching pairs:"),
            self.pair_input_column,
            ft.Row([add_pair_button, start_button], spacing=20)
        ])

    def start_game(self, e):
        left_items = [field.value.strip() for field in self.left_inputs if field.value.strip()]
        right_items = [field.value.strip() for field in self.right_inputs if field.value.strip()]

        if len(left_items) != len(right_items) or len(left_items) == 0:
            self.page.snack_bar = ft.SnackBar(ft.Text("Please enter the same number of left and right items."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        self.page.clean()
        game = MatchablePairs(self.page, left_items, right_items)
        self.page.add(game.build())
        self.page.update()