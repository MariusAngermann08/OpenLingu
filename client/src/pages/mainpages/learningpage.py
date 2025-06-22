import flet as ft
import requests
import os
from typing import Callable


class LearningPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page

        # Page layout
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Layout constants
        self.WIDTH = 500
        self.HEIGHT = 500
        self.OFFSET = 150
        self.center_index = 0
        self.lesson_widgets = []

        self.lessons = [
            {"title": "Lesson 1", "color": "#d65b09", "on_click": lambda e: print("Edit Lesson 1")},
            {"title": "Lesson 2", "color": "#098ad6", "on_click": lambda e: print("Edit Lesson 2")},
            {"title": "Lesson 3", "color": "#0acb6f", "on_click": lambda e: print("Edit Lesson 3")},
            {"title": "Lesson 4", "color": "#d65b09", "on_click": lambda e: print("Edit Lesson 4")},
            {"title": "Lesson 5", "color": "#098ad6", "on_click": lambda e: print("Edit Lesson 5")},
            {"title": "Lesson 6", "color": "#0acb6f", "on_click": lambda e: print("Edit Lesson 6")},
        ]

        for i, lesson in enumerate(self.lessons):
            container = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(lesson["title"], size=40, weight="bold", color="white"),
                        # Add subtext or icons here if needed
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                width=self.WIDTH,
                height=self.HEIGHT,
                bgcolor=lesson["color"],
                border_radius=15,
                ink=True,
                animate_position=ft.Animation(400, curve=ft.AnimationCurve.EASE_IN_OUT),
                animate_scale=ft.Animation(300, "ease_in_out"),
                animate_opacity=ft.Animation(300, "ease_in_out"),
                on_click=self.wrap_on_click(i, lesson["on_click"]),
                shadow=ft.BoxShadow(
                    blur_radius=25, spread_radius=1,
                    color="rgba(0,0,0,0.25)", offset=ft.Offset(4, 4)
                ),
            )
            self.lesson_widgets.append(container)

        # Stack for overlapping layout
        self.stack = ft.Stack(
            controls=self.lesson_widgets,
            width=page.width,
            height=self.HEIGHT + 40,
        )

        self.content = self.stack


        self.update_positions()

    def wrap_on_click(self, i: int, user_callback: Callable):
        def wrapped_click(e, self=self, i=i, user_callback=user_callback):
            if i != self.center_index:
                self.center_index = i
                self.update_positions()
                self.page.update()
            elif user_callback is not None:
                user_callback(e)
        return wrapped_click

    def navigate(self, direction: int):
        new_index = self.center_index + direction
        if 0 <= new_index < len(self.lesson_widgets):
            self.center_index = new_index
            self.update_positions()
            self.page.update()

    def update_positions(self):
        center_x = (self.page.width - self.WIDTH) // 2

        for i, container in enumerate(self.lesson_widgets):
            diff = i - self.center_index

            if diff == 0:
                container.left = center_x
                container.scale = 1.0
                container.opacity = 1.0
            elif diff == 1:
                container.left = self.page.width - self.OFFSET
                container.scale = 0.85
                container.opacity = 0.7
            elif diff == -1:
                container.left = -self.WIDTH + self.OFFSET
                container.scale = 0.85
                container.opacity = 0.7
            elif diff > 1:
                container.left = self.page.width + 1000
                container.scale = 0.7
                container.opacity = 0.0
            else:
                container.left = -self.WIDTH - 1000
                container.scale = 0.7
                container.opacity = 0.0