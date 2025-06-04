import flet as ft
import requests
import os
from typing import Callable


class LearningPage(ft.Container):
    def __init__(self, page, mainpage, lessons: list[dict]):
        """
        `lessons`: List of dictionaries with:
            - 'title': str
            - 'color': str (hex color)
            - 'on_click': Callable
        """
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        self.main_page = mainpage

        # Page layout settings
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Layout constants
        self.WIDTH = 500
        self.HEIGHT = 500
        self.OFFSET = 150  # Side peek space

        # Track currently centered lesson
        self.center_index = 0

        self.lesson_widgets = []

        # List to hold all Flet containers
        self.lessons = [
            {
                "title": "Lesson 1",
                "color": "#d65b09",
                "on_click": None
            },
            {
                "title": "Lesson 2",
                "color": "#098ad6",
                "on_click": None
            },
            {
                "title": "Lesson 3",
                "color": "#0acb6f",
                "on_click": None
            },
            {
                "title": "Lesson 4",
                "color": "#d65b09",
                "on_click": None
            },
            {
                "title": "Lesson 5",
                "color": "#098ad6",
                "on_click": None
            },
            {
                "title": "Lesson 6",
                "color": "#0acb6f",
                "on_click": None
            },
        ]


        # Dynamically create containers from passed data
        for i, lesson in enumerate(self.lessons):
            container = ft.Container(
                content=ft.Row(
                    controls=[ft.Text(lesson["title"], size=70, weight="w600")],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=self.WIDTH,
                height=self.HEIGHT,
                bgcolor=lesson["color"],
                border_radius=10,
                ink=True,
                animate_position=ft.Animation(400, curve=ft.AnimationCurve.EASE_IN_OUT),
                on_click=self.wrap_on_click(i, lesson["on_click"]),
            )
            self.lesson_widgets.append(container)

        # Stack them for animated layout
        self.stack = ft.Stack(
            controls=self.lesson_widgets,
            width=page.width,
            height=self.HEIGHT,
        )

        self.content = self.stack
        self.update_positions()

    def wrap_on_click(self, i: int, user_callback: Callable):
        def wrapped_click(e, self=self, i=i, user_callback=user_callback):
            if i != self.center_index:
                self.center_index = i
                self.update_positions()
                self.page.update()
                #user_callback()   @Jonas what is this for? No such function exists
        return wrapped_click

    def update_positions(self):
        """
        Repositions lesson containers based on which is centered.
        Only current, previous, and next are visibly placed.
        """
        center_x = (self.page.width - self.WIDTH) // 2

        for i, container in enumerate(self.lesson_widgets):
            diff = i - self.center_index

            if diff == 0:
                container.left = center_x
            elif diff == 1:
                container.left = self.page.width - self.OFFSET
            elif diff == -1:
                container.left = -self.WIDTH + self.OFFSET
            elif diff > 1:
                container.left = self.page.width + 1000
            else:
                container.left = -self.WIDTH - 1000