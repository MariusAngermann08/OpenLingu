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
    def __init__(self, page: ft.Page, **kwargs):
        # Store page reference first
        self.page = page
        self.pages = []
        self.current_page = 0
        
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
        
        # Create the main layout
        layout = ft.Column(
            [
                self.content_area,
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
        
        # Initialize the container
        super().__init__(content=layout, **kwargs)
        
        # Ensure the container is properly sized
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
            
        # Only update the content if it's different
        if self.content_area.content != self.pages[self.current_page]:
            self.content_area.content = self.pages[self.current_page]
            
        self.page_number.value = f"Page: {self.current_page + 1}/{len(self.pages)}"
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == len(self.pages) - 1
        
        # Update the page instead of self
        if self.page:
            self.page.update()
    
    def load_lection(self, lection_json: str):
        try:
            lection = LectionParser(lection_json)
            # Pass the page reference to the parser
            lection.page = self.page
            lection.parse_lection()
            self.pages = lection.get_pages()
            self.current_page = 0
            
            if self.pages:
                self.content_area.content = self.pages[0]
                self.page_number.value = f"Page: 1/{len(self.pages)}"
                self.prev_btn.disabled = True
                self.next_btn.disabled = len(self.pages) <= 1
                
                # Update the page
                if self.page:
                    self.page.update()
                    
        except Exception as e:
            error_msg = f"Error loading lection: {str(e)}"
            print(error_msg)
            if self.page:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(error_msg),
                    bgcolor="#FF5252"
                )
                self.page.snack_bar.open = True
                self.page.update()
        