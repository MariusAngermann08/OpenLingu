import flet as ft
import sys
import os
from pathlib import Path

# Get the src directory (client/src)
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent  # Go up to client/src

# Add src directory to Python path
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now import the module
try:
    from pages.utils.lectionparser import LectionParser
except ImportError as e:
    print(f"Error importing LectionParser: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Source directory: {src_dir}")
    print(f"Current sys.path: {sys.path}")
    if (src_dir / 'pages' / 'utils').exists():
        print(f"Contents of pages/utils: {os.listdir(src_dir / 'pages' / 'utils')}")
    else:
        print(f"Utils directory not found at: {src_dir / 'pages' / 'utils'}")
    raise




class LectionViewer(ft.Container):
    def __init__(self, page: ft.Page = None, **kwargs):
        # Initialize container first to ensure it exists
        super().__init__(**kwargs)
        
        # Store page reference if provided
        self.page = page
        self.pages = []
        self.current_page = 0
        
        # Initialize UI components
        self.task_widgets = []  # Track task widgets for current page
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        # Create a simple container for content
        self.content_area = ft.Container(expand=True)
        
        # Create navigation controls
        self.prev_btn = ft.IconButton(
            icon="chevron_left",
            on_click=self.prev_page,
            disabled=True
        )
        self.next_btn = ft.IconButton(
            icon="chevron_right",
            on_click=self.next_page,
            disabled=True
        )
        self.page_number = ft.Text("Page: 0/0")
        
        # Create a styled warning for incomplete tasks
        self.incomplete_msg = ft.Container(
            content=ft.Row([
                ft.Icon("warning", color="#FFB300", size=24),
                ft.Text(
                    "Please complete all tasks before proceeding.",
                    color="#B71C1C",
                    size=18,
                    weight="bold",
                    text_align="center"
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor="#FFF3CD",  # Light yellow
            border_radius=8,
            padding=12,
            visible=False,
            alignment=ft.alignment.center,
            margin=ft.margin.symmetric(vertical=8, horizontal=0),
        )
        layout = ft.Column(
            [
                self.content_area,
                self.incomplete_msg,
                ft.Row(
                    [
                        self.prev_btn,
                        self.page_number,
                        self.next_btn
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            expand=True
        )
        # Set the layout as the container's content
        self.content = layout
        self.expand = True
    
    def prev_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_display()
    
    def next_page(self, e):
        if self.pages and self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_display()
    
    def update_display(self):
        if not self.pages or self.current_page >= len(self.pages):
            return
            
        current_page = self.pages[self.current_page]
        
        # Check if this is the LectionEndPage
        if hasattr(current_page, '__class__') and current_page.__class__.__name__ == 'LectionEndPage':
            # For the end page, hide the navigation and page number
            self.prev_btn.visible = False
            self.next_btn.visible = False
            self.page_number.visible = False
            self.incomplete_msg.visible = False
            
            # Set the end page as content
            self.content_area.content = current_page
            self.content_area.expand = True
            self.content_area.alignment = ft.alignment.center
        else:
            # For regular pages, show navigation and update task widgets
            self.prev_btn.visible = True
            self.next_btn.visible = True
            self.page_number.visible = True
            
            # Only update the content if it's different
            if self.content_area.content != current_page:
                self.content_area.content = current_page
            
            # Update task widgets and navigation state
            self.task_widgets = getattr(current_page, 'task_widgets', [])
            for widget in self.task_widgets:
                widget.page = self
            
            # Update navigation buttons
            self.prev_btn.disabled = self.current_page == 0
            self._update_next_btn_state()
        
        # Update the page number text (but keep it hidden for end page)
        self.page_number.value = f"Page: {self.current_page + 1}/{len(self.pages)}"
        
        # Update the page
        if self.page:
            self.page.update()

    # _find_task_widgets is no longer needed and can be removed.

    def _update_next_btn_state(self):
        all_solved = True
        for widget in self.task_widgets:
            if hasattr(widget, "is_fully_correct"):
                if not widget.is_fully_correct():
                    all_solved = False
                    break
            elif hasattr(widget, "check_all_solved"):
                if not widget.check_all_solved():
                    all_solved = False
                    break
            elif hasattr(widget, "is_correct"):
                if not widget.is_correct():
                    all_solved = False
                    break
        self.next_btn.disabled = not all_solved
        self.next_btn.update()  # Ensure button UI updates immediately
        if not all_solved:
            self.incomplete_msg.visible = True
        else:
            self.incomplete_msg.visible = False
        self.incomplete_msg.update()
        self.incomplete_msg.value = "Please complete all tasks before proceeding." if not all_solved else ""
        if self.page:
            self.page.update()

    def notify_task_update(self):
        # Call this from widgets when their state changes
        self._update_next_btn_state()

    def run_task(self, *args, **kwargs):
        # Proxy to the underlying Flet page's run_task
        return self.page.run_task(*args, **kwargs)

    def get_control(self, *args, **kwargs):
        # Proxy to the underlying Flet page's get_control
        return self.page.get_control(*args, **kwargs)

    
    def _get_page(self):
        """Helper method to safely get the page reference"""
        # Try to get page from self first
        page = getattr(self, 'page', None)
        # If not found, try to get it from the content
        if page is None and hasattr(self, 'content') and hasattr(self.content, 'page'):
            page = self.content.page
        return page

    def load_lection(self):
        print("\n=== Starting load_lection ===")
        try:
            page = self._get_page()
            if page is None:
                error_msg = "Error: Page reference is None in load_lection"
                print(error_msg)
                return
                
            print("1. Page reference obtained successfully")
            
            # Load lection from client storage
            print("2. Attempting to get lection from client storage...")
            lection = page.client_storage.get("lection")
            
            if not lection:
                error_msg = "No lection data found in client storage"
                print(error_msg)
                if page:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(error_msg),
                        bgcolor="#FF5252"
                    )
                    page.snack_bar.open = True
                    page.update()
                return
            
            #Print out the raw json content
            print("Raw lection content:", lection)
                
            print("3. Lection data retrieved from storage")
            print(f"   Lection type: {type(lection)}")
            
            # Debug: Print the type and keys of the lection data
            if hasattr(lection, 'keys'):
                print(f"   Lection keys: {list(lection.keys())}")
                if 'content' in lection and isinstance(lection['content'], str):
                    print(f"   Content type: {type(lection['content'])}")
                    print(f"   Content length: {len(lection['content'])}")
            
            # Check if we need to parse the content field
            if isinstance(lection, dict) and 'content' in lection and isinstance(lection['content'], str):
                print("4. Found string content, attempting to parse as JSON...")
                try:
                    import json
                    content_json = json.loads(lection['content'])
                    lection['content'] = content_json
                    print("   Successfully parsed content JSON")
                    if hasattr(content_json, 'keys'):
                        print(f"   Parsed content keys: {list(content_json.keys())}")
                except Exception as e:
                    print(f"   Error parsing content JSON: {e}")
                    import traceback
                    traceback.print_exc()
            
            print("5. Creating LectionParser instance...")
            try:
                lection_parser = LectionParser(lection)
                print("6. LectionParser created successfully")
                
                # Pass the page reference to the parser
                lection_parser.page = page
                print("7. Calling parse_lection...")
                lection_parser.parse_lection()
                
                print("8. Getting pages from parser...")
                self.pages = lection_parser.get_pages()
                print(f"9. Got {len(self.pages)} pages from parser")
                
                self.current_page = 0
                
                if self.pages:
                    print(f"10. First page type: {type(self.pages[0])}")
                    self.content_area.content = self.pages[0]
                    self.page_number.value = f"Page: 1/{len(self.pages)}"
                    self.prev_btn.disabled = True
                    self.next_btn.disabled = len(self.pages) <= 1
                    
                    print("11. Updating page content...")
                    page.update()
                    print("12. Page update complete")
                else:
                    print("10. No pages were generated by the parser")
                    
            except Exception as e:
                print(f"Error in LectionParser: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
                    
        except Exception as e:
            error_msg = f"Error in load_lection: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            
            page = self._get_page()
            if page:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error loading lection: {str(e)}"),
                    bgcolor="#FF5252"
                )
                page.snack_bar.open = True
                page.update()
        
        print("=== End of load_lection ===\n")
