import flet as ft
from typing import Callable
import asyncio
import requests
import random


class LearningPage(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True, alignment=ft.alignment.center)
        self.page = page
        
        # Layout constants
        self.WIDTH = 500
        self.HEIGHT = 500
        self.OFFSET = 150
        self.center_index = 0
        self.lesson_widgets = []
        self._auto_resize_running = False
        self._initialized = False
        
        # Initialize UI components
        self.lessons_list = []

        #Get server url from client storage
        self.server_url = self.page.client_storage.get("server_url")
        if not self.server_url:
            self.server_url = "http://localhost:8000"
        
        #Get current selected language from client storage
        self.selected_language = self.page.client_storage.get("selected_language")
        if not self.selected_language:
            self.selected_language = "default"
        
        #/languages/{language_name}/lections
        response = requests.get(f"{self.server_url}/languages/{self.selected_language}/lections", timeout=5)
        if not response.status_code == 200:
            self.lessons = [
                {"title": "Error Loading Lections", "color": "#d65b09", "on_click": lambda e: None},
            ]
        else:
            # Response is a list of lection objects with id and title
            self.lessons_list = response.json()
            # Add loaded lections from lessons list to self.lessons
            self.lessons = []
            for lesson in self.lessons_list:
                self.lessons.append({
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "color": random.choice(["#1a73e8", "#d65b09"]), 
                    "on_click": lambda e, lid=lesson["id"]: self.load_lesson(lid)
                })

        


        # Create lesson widgets
        for i, lesson in enumerate(self.lessons):
            container = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(lesson["title"], size=40, weight="bold", color="white"),
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
                    blur_radius=25, 
                    spread_radius=1,
                    color="rgba(0,0,0,0.25)", 
                    offset=ft.Offset(4, 4)
                ),
            )
            self.lesson_widgets.append(container)

        # Initialize stack
        self._init_stack()
        
        # Mark as initialized and start auto-resize
        self._initialized = True
        self.start_auto_resize()
    
    def load_lesson(self, lection_id: str):
        # Load lection by ID instead of title
        response = requests.get(f"{self.server_url}/languages/{self.selected_language}/lections/{lection_id}", timeout=5)
        if not response.status_code == 200:
            error_msg = "Error loading lection"
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(error_msg),
                bgcolor="#FF5252"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        # Response will be a dict with lection data
        self.lection = response.json()
        # Save lection to client storage
        self.page.client_storage.set("lection", self.lection)
        # Navigate to the lection viewer
        self.page.go("/lectionviewer")

    
    def _init_stack(self):
        """Initialize the stack with the current page width"""
        if not hasattr(self, 'page') or self.page is None:
            return
            
        # Stack for overlapping layout
        self.stack = ft.Stack(
            controls=self.lesson_widgets,
            width=self.page.width,
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
        try:
            if not hasattr(self, 'page') or self.page is None or not hasattr(self, 'stack') or self.stack is None:
                return
                
            if not hasattr(self.page, 'width') or not self.page.width:
                return
                
            page_width = self.page.width
            width = self.WIDTH
            height = self.HEIGHT
            offset = self.OFFSET
            center_x = (page_width - width) // 2

            for i, container in enumerate(self.lesson_widgets):
                if not container:
                    continue
                    
                diff = i - self.center_index

                if diff == 0:
                    container.left = center_x
                    container.scale = 1.0
                    container.opacity = 1.0
                elif diff == 1:
                    container.left = page_width - offset
                    container.scale = 0.85
                    container.opacity = 0.7
                elif diff == -1:
                    container.left = -width + offset
                    container.scale = 0.85
                    container.opacity = 0.7
                elif diff > 1:
                    container.left = page_width + 1000
                    container.scale = 0.7
                    container.opacity = 0.0
                else:
                    container.left = -width - 1000
                    container.scale = 0.7
                    container.opacity = 0.0

            if hasattr(self, 'stack') and self.stack is not None:
                self.stack.width = page_width
                self.stack.height = height + 50
        except Exception as e:
            print(f"[ERROR] in update_positions: {e}")

    def _safe_create_task(self, coro):
        """Safely create a task, handling the case where no event loop is running"""
        try:
            # Try to get the running loop
            loop = asyncio.get_running_loop()
            return loop.create_task(coro)
        except RuntimeError as e:
            if "no running event loop" in str(e):
                # If no loop is running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                task = loop.create_task(coro)
                # Start the loop in a separate thread
                import threading
                def run_loop():
                    asyncio.set_event_loop(loop)
                    loop.run_forever()
                threading.Thread(target=run_loop, daemon=True).start()
                return task
            raise

    def start_auto_resize(self):
        if not self._auto_resize_running:
            self._auto_resize_running = True
            try:
                self._auto_resize_task = self._safe_create_task(self._auto_resize_loop())
            except Exception as e:
                print(f"[ERROR] Failed to start auto-resize: {e}")
                self._auto_resize_running = False

    def stop_auto_resize(self):
        self._auto_resize_running = False
        if hasattr(self, '_auto_resize_task'):
            try:
                if not self._auto_resize_task.done():
                    self._auto_resize_task.cancel()
            except Exception as e:
                print(f"[ERROR] Error stopping auto-resize: {e}")

    async def _auto_resize_loop(self):
        while self._auto_resize_running:
            try:
                if not hasattr(self, 'page') or self.page is None:
                    await asyncio.sleep(0.5)  # Wait longer if page isn't ready
                    continue
                    
                # Check if stack is initialized
                if not hasattr(self, 'stack') or self.stack is None:
                    self._init_stack()  # Try to reinitialize stack
                    await asyncio.sleep(0.5)
                    continue
                    
                # Update positions and refresh UI
                self.update_positions()
                try:
                    self.page.update()
                except Exception as e:
                    print(f"[WARNING] Failed to update page: {e}")
                
                await asyncio.sleep(0.1)  # Reduced update frequency
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[ERROR] in _auto_resize_loop: {e}")
                await asyncio.sleep(1)  # Prevent tight error loop

    def __del__(self):
        # Clean up resources when the object is destroyed
        self.stop_auto_resize()