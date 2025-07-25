import flet as ft
import random
import asyncio 
import time
import json


class UnderlinedText(ft.Container):
    def __init__(
        self,
        text: str,
        underlined: dict,
        font_size: float = 14,
        bgcolor: str = None,
        **kwargs
    ):
        words = text.split(" ")
        spans = []
        # Convert string keys to integers and adjust from 1-based to 0-based indexing
        underlined = {int(k)-1: v for k, v in underlined.items()}
        
        for i, word in enumerate(words):
            if i in underlined:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            decoration=ft.TextDecoration.UNDERLINE,
                            decoration_color=underlined[i],
                            size=font_size
                        )
                    )
                )
            else:
                spans.append(
                    ft.TextSpan(
                        text=word + " ",
                        style=ft.TextStyle(
                            size=font_size
                        )
                    )
                )

        super().__init__(
            content=ft.Text(spans=spans, selectable=True),
            bgcolor=bgcolor,
            padding=10,
            border_radius=5,
            **kwargs
        )


class DraggableText:

    def __init__(self, page: ft.Page, text: str, gaps_idx: list[int], options: dict[str, int]):
        self.page = page
        self.raw_text = text
        self.luecken_idx = gaps_idx
        self.options = list(options.items())  # [(word, idx)]
        self.correct_state = [False] * len(gaps_idx)
        self.drop_targets = []
        self.buttons = []

    def drag_will_accept(self, e: ft.DragTargetEvent):
        # e.data kommt als String, entweder JSON oder direkter Index
        try:
            print("DRAG WILL ACCEPT | e.data:", e.data)
            data = None
            # Versuch JSON zu parsen
            try:
                data = json.loads(e.data)
            except Exception:
                data = e.data  # fallback: roher String

            if isinstance(data, dict):
                dragged_idx = int(data.get("index", -1))
            elif isinstance(data, str) and data.isdigit():
                dragged_idx = int(data)
            else:
                dragged_idx = -1

            drop_idx = int(e.control.data)


            color = "#000000"
            e.control.content.border = ft.border.all(2, color)
        except Exception as ex:
            print("drag_will_accept Fehler:", ex)
        e.control.update()

    def drag_leave(self, e: ft.DragTargetEvent):
        e.control.content.border = None
        e.control.update()

    def drag_accept(self, e: ft.DragTargetEvent):
        try:
            print("DROP ACCEPTED | e.data:", e.data)

            data_obj = None
            # Versuche JSON parsen, fallback auf rohen String
            try:
                data_obj = json.loads(e.data)
            except Exception:
                data_obj = e.data

            # Falls data_obj ein dict mit src_id, holen wir Daten vom Draggable Control
            if isinstance(data_obj, dict) and "src_id" in data_obj:
                src_control = self.page.get_control(data_obj["src_id"])
                drag_data_raw = src_control.data
                if isinstance(drag_data_raw, str):
                    drag_data = json.loads(drag_data_raw)
                elif isinstance(drag_data_raw, dict):
                    drag_data = drag_data_raw
                else:
                    print("Unerwarteter Datentyp bei src_control.data:", type(drag_data_raw))
                    return
            elif isinstance(data_obj, dict) and "word" in data_obj and "index" in data_obj:
                drag_data = data_obj
            else:
                print("Unbekanntes Drag-Datenformat:", data_obj)
                return

            word = drag_data["word"]
            dragged_idx = int(drag_data["index"])
            drop_idx = int(e.control.data)

        except Exception as ex:
            print("Fehler bei drag_accept:", ex)
            return

        correct = dragged_idx == drop_idx
        self.correct_state[drop_idx] = correct

        container = e.control.content
        container.border = None
        container.bgcolor = ft.Colors.GREEN if correct else ft.Colors.RED
        container.content = ft.Text(word, size=16, color=ft.Colors.BLACK)
        e.control.update()

        if hasattr(self.page, "notify_task_update"):
            self.page.notify_task_update()

        if not correct:
            async def reset_task():
                await asyncio.sleep(1)
                self.correct_state[drop_idx] = False
                container.bgcolor = ft.Colors.BLUE_GREY_100
                container.content = ft.Text("______", size=16, color=ft.Colors.BLACK)
                e.control.update()

                if hasattr(self.page, "notify_task_update"):
                    self.page.notify_task_update()

            self.page.run_task(reset_task)

    def build(self):
        self.drop_targets.clear()
        self.buttons.clear()

        text_parts = self.raw_text.split(" ")
        row = ft.Row(wrap=True, spacing=5, alignment=ft.MainAxisAlignment.CENTER)

        luecke_counter = 0
        for i, word in enumerate(text_parts):
            if i in self.luecken_idx:
                drop = ft.DragTarget(
                    data=str(luecke_counter),
                    group="textdrop",
                    on_will_accept=self.drag_will_accept,
                    on_leave=self.drag_leave,
                    on_accept=self.drag_accept,
                    content=ft.Container(
                        padding=10,
                        width=100,
                        height=40,
                        bgcolor=ft.Colors.BLUE_GREY_100,
                        border_radius=8,
                        alignment=ft.alignment.center,
                        content=ft.Text("______", size=16, color=ft.Colors.BLACK),
                    ),
                )
                self.drop_targets.append(drop)
                row.controls.append(drop)
                luecke_counter += 1
            else:
                row.controls.append(ft.Text(word, size=16, color=ft.Colors.BLACK))

        drag_row = ft.Row(
            spacing=10,
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER
        )
        for word, idx in self.options:
            drag_data = json.dumps({"word": word, "index": idx})
            print("Draggable created:", drag_data)
            btn = ft.Draggable(
                group="textdrop",
                data=drag_data,
                content=ft.Container(
                    padding=10,
                    width=100,
                    height=40,
                    bgcolor=ft.Colors.BLUE_GREY_100,
                    border_radius=8,
                    alignment=ft.alignment.center,
                    content=ft.Text(word, size=16, color=ft.Colors.BLACK),
                ),
            )
            self.buttons.append(btn)
            drag_row.controls.append(btn)

        return ft.Column(
            [
                ft.Row([row], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20),
                drag_row,
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def is_fully_correct(self):
        return all(self.correct_state)



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

