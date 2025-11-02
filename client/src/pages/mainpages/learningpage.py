import flet as ft
from typing import Callable, List, Dict, Any
import asyncio
import requests
import random


class LearningPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.page = page
        self.page.on_resize = self.handle_resize
        
        # Layout constants
        self.CARD_WIDTH = 300
        self.CARD_HEIGHT = 180
        self.CARD_MARGIN = 15
        
        # Color schemes for light/dark mode
        self.light_colors = {
            "card_bg": "#ffffff",
            "card_border": "#e0e0e0",
            "text_primary": "#212121",
            "text_secondary": "#757575",
            "completed_bg": "#e8f5e9",
            "completed_text": "#2e7d32",
            "not_completed_bg": "#fff3e0",
            "not_completed_text": "#ef6c00",
            "difficulty_easy": "#4caf50",
            "difficulty_medium": "#ff9800",
            "difficulty_hard": "#f44336",
            "difficulty_text": "#ffffff"
        }
        
        self.dark_colors = {
            "card_bg": "#1e1e1e",
            "card_border": "#444444",
            "text_primary": "#f5f5f5",
            "text_secondary": "#b0b0b0",
            "completed_bg": "#1b5e20",
            "completed_text": "#a5d6a7",
            "not_completed_bg": "#e65100",
            "not_completed_text": "#ffcc80",
            "difficulty_easy": "#388e3c",
            "difficulty_medium": "#f57c00",
            "difficulty_hard": "#d32f2f",
            "difficulty_text": "#ffffff"
        }
        
        # Initialize UI components
        self.lessons: List[Dict[str, Any]] = []
        self.grid_view = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=350,
            child_aspect_ratio=1.5,
            spacing=20,
            run_spacing=20,
            padding=20,
        )
        
        # Add loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Loading lections...", size=16, weight="bold")
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=ft.alignment.center
        )
        
        # Set initial content to loading indicator
        self.content = self.loading_indicator
        
        # We'll use a timer to ensure the page is fully loaded before making async calls
        self.page.run_task(self._delayed_init)
    
    async def _delayed_init(self):
        """Delayed initialization to ensure page is fully loaded"""
        # Small delay to ensure the page is fully initialized
        await asyncio.sleep(0.5)
        # Now load the lections
        await self.load_lections()
    
    async def load_lections(self):
        """Load lections from the server asynchronously"""
        try:
            # Get server URL and selected language from client storage asynchronously
            try:
                server_url = await self.page.client_storage.get_async("server_url")
                if not server_url:
                    server_url = "http://localhost:8000"
                    
                selected_language = await self.page.client_storage.get_async("selected_language")
                if not selected_language:
                    selected_language = "default"
                
                # Make API request in a thread to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.get(
                        f"{server_url}/languages/{selected_language}/lections",
                        timeout=10
                    )
                )
                
                if response.status_code == 200:
                    lessons_data = response.json()
                    self.lessons = [
                        {
                            "id": lesson["id"],
                            "title": lesson["title"],
                            "description": lesson.get("description", "No description available"),
                            "difficulty": lesson.get("difficulty", "medium").lower(),
                            "is_completed": random.choice([True, False])  # Simulate completion status
                        }
                        for lesson in lessons_data
                    ]
                    await self.update_ui()
                else:
                    raise Exception(f"Failed to load lections: {response.status_code}")
                    
            except Exception as e:
                print(f"Error in load_lections: {e}")
                # Fallback to empty lessons if there's an error
                self.lessons = []
                await self.update_ui()
                raise
                
        except Exception as e:
            print(f"Error loading lections: {e}")
            self.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name="error_outline", size=48, color="#f44336"),
                        ft.Text("Failed to load lections", size=20, weight="bold"),
                        ft.Text("Please check your connection and try again.", size=14, color="#757575"),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda _: self.page.run_task(self.load_lections)
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.alignment.center,
                expand=True
            )
            self.page.update()
    
    async def update_ui(self):
        """Update the UI with the loaded lections"""
        if not self.lessons:
            self.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name="menu_book", size=48, color="#9e9e9e"),
                        ft.Text("No lections available", size=20, weight="bold"),
                        ft.Text("Check back later for new content!", size=14, color="#757575")
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        else:
            self.grid_view.controls = [
                self._create_lection_card(lesson) for lesson in self.lessons
            ]
            
            self.content = ft.Column(
                [
                    ft.Container(
                        content=ft.Text("Available Lections", size=28, weight="bold"),
                        padding=ft.padding.only(bottom=20)
                    ),
                    self.grid_view
                ],
                expand=True
            )
        
        self.page.update()
    
    def _get_colors(self):
        """Get color scheme based on current theme"""
        return self.dark_colors if self.page.theme_mode == ft.ThemeMode.DARK else self.light_colors

    def _get_difficulty_color(self, difficulty: str, colors: dict) -> str:
        """Get color for difficulty level"""
        difficulty = difficulty.lower()
        if difficulty == "easy":
            return colors["difficulty_easy"]
        elif difficulty == "hard":
            return colors["difficulty_hard"]
        else:  # medium or any other value
            return colors["difficulty_medium"]

    def _create_lection_card(self, lesson: Dict[str, Any]) -> ft.Container:
        """Create a card for a single lection"""
        colors = self._get_colors()
        is_completed = lesson.get("is_completed", False)
        difficulty = lesson.get("difficulty", "medium").lower()
        
        # Create difficulty badge
        difficulty_badge = ft.Container(
            content=ft.Text(
                difficulty.upper(),
                size=10,
                weight="bold",
                color=colors["difficulty_text"],
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=10,
            bgcolor=self._get_difficulty_color(difficulty, colors),
        )
        
        # Create the open button
        open_button = ft.ElevatedButton(
            text="Open",
            icon="open_in_new",
            on_click=lambda e, lid=lesson["id"]: self.page.run_task(self.load_lesson, lid),
            style=ft.ButtonStyle(
                color=colors["card_bg"],
                bgcolor=colors["text_primary"],
                padding=ft.padding.symmetric(horizontal=20, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=20)
            ),
            scale=0.9,
            animate_scale=ft.Animation(200, "ease_in_out"),
        )
        
        # Truncate description if too long
        description = lesson.get("description", "No description available")
        if len(description) > 100:
            description = description[:97] + "..."
        
        # Create the main card container with hover effects
        return ft.Container(
            content=ft.Column(
                [
                    # Header with title and difficulty
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(
                                    lesson["title"],
                                    size=18,
                                    weight="bold",
                                    color=colors["text_primary"],
                                    max_lines=1,
                                    overflow="ellipsis",
                                    expand=True
                                ),
                                difficulty_badge
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.only(left=20, right=20, top=15, bottom=5),
                        expand=True
                    ),
                    
                    # Description
                    ft.Container(
                        content=ft.Text(
                            description,
                            size=12,
                            color=colors["text_secondary"],
                            max_lines=3,
                            overflow="ellipsis"
                        ),
                        margin=ft.margin.only(left=20, right=20, bottom=10),
                        padding=ft.padding.only(right=5)
                    ),
                    
                    # Spacer to push content to top and bottom
                    ft.Container(expand=True),
                    
                    # Button and status row
                    ft.Container(
                        content=ft.Row(
                            [
                                # Status indicator
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                name="check_circle" if is_completed else "schedule",
                                                color=colors["completed_text"] if is_completed else colors["not_completed_text"],
                                                size=14
                                            ),
                                            ft.Text(
                                                "Completed" if is_completed else "In Progress",
                                                size=11,
                                                weight="w500",
                                                color=colors["completed_text"] if is_completed else colors["not_completed_text"]
                                            )
                                        ],
                                        spacing=5,
                                    ),
                                    padding=ft.padding.symmetric(vertical=6, horizontal=10),
                                    border_radius=15,
                                    bgcolor=colors["completed_bg"] if is_completed else colors["not_completed_bg"],
                                ),
                                
                                # Open button
                                open_button
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=ft.padding.symmetric(horizontal=15, vertical=10)
                    )
                ],
                spacing=0,
                expand=True
            ),
            border_radius=10,
            bgcolor=colors["card_bg"],
            border=ft.border.all(1, colors["card_border"]),
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color="#00000020",
                offset=ft.Offset(0, 5),
            ),
            animate=ft.Animation(200, "ease_in_out"),
            height=self.CARD_HEIGHT,
            on_hover=self._on_card_hover,
        )
    
    def _on_card_hover(self, e):
        """Handle card hover effect with scale animation"""
        card = e.control
        if e.data == "true":
            # Scale up slightly on hover
            card.scale = 1.02
            # Slightly increase shadow for depth
            card.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=20,
                color="#00000030",
                offset=ft.Offset(0, 8),
            )
        else:
            # Return to normal
            card.scale = 1.0
            card.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color="#00000020",
                offset=ft.Offset(0, 5),
            )
        self.page.update()
    
    async def handle_resize(self, e):
        """Handle window resize"""
        if self.page.width < 600:
            self.grid_view.max_extent = self.page.width - 40
        else:
            self.grid_view.max_extent = 350
        self.page.update()
    
    async def load_lesson(self, lection_id: str):
        """Load a specific lection"""
        try:
            # Get server URL and selected language from client storage asynchronously
            server_url = await self.page.client_storage.get_async("server_url")
            if not server_url:
                server_url = "http://localhost:8000"
                
            selected_language = await self.page.client_storage.get_async("selected_language")
            if not selected_language:
                selected_language = "default"
            
            # Make the API request in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"{server_url}/languages/{selected_language}/lections/{lection_id}",
                    timeout=10
                )
            )
            
            if response.status_code != 200:
                error_msg = "Error loading lection"
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_msg),
                    bgcolor="#FF5252"
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
                return
                
            # Response will be a dict with lection data
            lection_data = response.json()
            
            # Save lection to client storage asynchronously
            await self.page.client_storage.set_async("lection", lection_data)
            
            # Navigate to the lection viewer
            self.page.go("/lectionviewer")
            
            # Save lection to client storage asynchronously
            await self.page.client_storage.set_async("lection", lection_data)
            
            # Navigate to the lection viewer
            self.page.go("/lectionviewer")
            
        except Exception as e:
            # Show error message if something goes wrong
            if hasattr(self, 'page') and self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error loading lection: {str(e)}"),
                    bgcolor="#FF5252"
                )
                self.page.snack_bar.open = True
                self.page.update()
            print(f"Error in load_lesson: {e}")

    
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