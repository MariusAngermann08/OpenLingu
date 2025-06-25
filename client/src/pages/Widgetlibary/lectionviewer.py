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
            
        # Only update the content if it's different
        if self.content_area.content != self.pages[self.current_page]:
            self.content_area.content = self.pages[self.current_page]
            
        self.page_number.value = f"Page: {self.current_page + 1}/{len(self.pages)}"
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = self.current_page == len(self.pages) - 1
        
        # Update the page instead of self
        if self.page:
            self.page.update()
    
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
