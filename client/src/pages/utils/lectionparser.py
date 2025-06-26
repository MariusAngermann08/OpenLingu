import flet as ft
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Get the src directory (client/src)
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent  # Go up to client/src

# Add src directory to Python path
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now import the modules
try:
    from pages.Widgetlibary.Lectionwidgets import (
        UnderlinedText,
        MatchablePairs,
        DraggableText,
        PictureDrag
    )
except ImportError as e:
    print(f"Error importing widgets: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Source directory: {src_dir}")
    print(f"Current sys.path: {sys.path}")
    if (src_dir / 'pages').exists():
        print(f"Contents of pages: {os.listdir(src_dir / 'pages')}")
    else:
        print(f"Pages directory not found at: {src_dir / 'pages'}")
    raise


class Page(ft.Container):
    def __init__(self):
        super().__init__()



class LectionParser:
    def __init__(self, lection_data):
        print(f"Initializing LectionParser with data type: {type(lection_data)}")
        
        # Check if lection_data is a string (file path) or a dict (already parsed JSON)
        if isinstance(lection_data, str):
            # Handle file path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # If path is relative, resolve it relative to the current file's directory
            if not os.path.isabs(lection_data):
                # First try relative to the current working directory
                cwd_path = os.path.abspath(lection_data)
                if os.path.exists(cwd_path):
                    lection_path = cwd_path
                else:
                    # If not found, try relative to the script directory
                    script_path = os.path.join(script_dir, lection_data)
                    if os.path.exists(script_path):
                        lection_path = script_path
                    else:
                        # If still not found, try one level up (in case we're running from src/)
                        parent_dir = os.path.dirname(script_dir)
                        parent_path = os.path.join(parent_dir, lection_data)
                        if os.path.exists(parent_path):
                            lection_path = parent_path
                        else:
                            # If still not found, use the original path (will raise error)
                            lection_path = lection_data
            else:
                lection_path = lection_data
                
            print(f"Loading lection from file: {lection_path}")
            
            # Load json from file
            try:
                with open(lection_path, "r", encoding='utf-8') as f:
                    self.lection = json.load(f)
                    print(f"Successfully loaded lection from file")
            except FileNotFoundError as e:
                error_msg = f"Error: Could not find lection file at {lection_path}"
                print(error_msg)
                print(f"Current working directory: {os.getcwd()}")
                print(f"Script directory: {script_dir}")
                raise ValueError(error_msg) from e
            except json.JSONDecodeError as e:
                error_msg = f"Error parsing JSON from file {lection_path}: {str(e)}"
                print(error_msg)
                raise ValueError(error_msg) from e
        elif isinstance(lection_data, dict):
            # Already parsed JSON
            print("Using provided dictionary as lection data")
            self.lection = lection_data
        else:
            error_msg = f"Expected string (file path) or dict, got {type(lection_data).__name__}"
            print(error_msg)
            raise ValueError(error_msg)
            
        print(f"Lection data keys: {list(self.lection.keys())}")
    


    def _create_widget(self, widget_data: Dict[str, Any]) -> ft.Control:
        widget_type = widget_data["type"]
        data = widget_data["data"]
        
        if widget_type == "underlined_text":
            widget =UnderlinedText(
                text=data["text"],
                underlined=data["underlined"],
                font_size=data.get("font_size", 14),
                bgcolor=data.get("bgcolor")
            )
            return widget.render()
            
        elif widget_type == "matchable_pairs":
            widget = MatchablePairs(
                page=self.page,
                left_items=data["left_items"],
                right_items=data["right_items"]
            )
            return widget.build()
            
        elif widget_type == "draggable_text":
            widget = DraggableText(
                page=self.page,
                text=data["text"],
                gaps_idx=data["gaps_idx"],
                options=data["options"]
            )
            return widget.build()
            
        elif widget_type == "text":
            return ft.Text(
                value=data["text"],
                size=data.get("size", 14),
                weight=data.get("weight", "normal"),
                color=data.get("color", "black")
            )
            
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
    
    def parse_lection(self):
        print("Starting to parse lection data...")
        
        try:
            # Extract basic lection info
            self.id = self.lection.get("id", "unknown_id")
            self.title = self.lection.get("title", "Untitled Lection")
            self.description = self.lection.get("description", "No description provided")
            self.language = self.lection.get("language", "unknown")
            self.difficulty = self.lection.get("difficulty", "beginner")
            self.created_at = self.lection.get("created_at", "")
            self.updated_at = self.lection.get("updated_at", "")
            
            print(f"Parsing lection: {self.title} (ID: {self.id})")
            print(f"Language: {self.language}, Difficulty: {self.difficulty}")
            
            # Get the content which contains the pages
            content = self.lection.get("content", {})
            if not content:
                print("Warning: No content found in lection data")
                self.pages = []
                return
                
            # Update metadata from content if not already set
            self.title = content.get("title", self.title)
            self.description = content.get("description", self.description)
            self.language = content.get("language", self.language)
            self.difficulty = content.get("difficulty", self.difficulty)
            
            # Check if pages exist in content
            if "pages" not in content or not content["pages"]:
                print("Warning: No pages found in lection content")
                self.pages = []
                return
                
            print(f"Found {len(content['pages'])} pages in lection")
            
            self.pages = []
            total_pages = len(content["pages"])
            for i, page_data in enumerate(content["pages"], 1):
                print(f"\nProcessing page {i}/{total_pages}")
                current_page = Page()
                widgets = []
                current_page.task_widgets = []  # Store interactive widgets here
                
                # Add title if exists
                if "title" in page_data:
                    print(f"  - Page title: {page_data['title']}")
                    widgets.append(ft.Text(
                        page_data["title"],
                        size=24,
                        weight="bold",
                        text_align=ft.TextAlign.CENTER,
                        width=float("inf"),
                    ))
                
                # Add description if exists
                if "description" in page_data:
                    print(f"  - Page description: {page_data['description']}")
                    widgets.append(ft.Text(
                        page_data["description"],
                        size=16,
                        italic=True,
                        text_align=ft.TextAlign.CENTER
                    ))
                
                # Add widgets
                if "widgets" not in page_data or not page_data["widgets"]:
                    print("  - No widgets found on this page")
                else:
                    print(f"  - Found {len(page_data['widgets'])} widgets on this page")
                    for j, widget_data in enumerate(page_data["widgets"], 1):
                        try:
                            widget_type = widget_data.get("type", "unknown")
                            print(f"    - Processing widget {j}: {widget_type}")
                            
                            # --- Store the actual widget instance for task widgets ---
                            widget_type = widget_data.get("type", "unknown")
                            if widget_type == "matchable_pairs":
                                task_widget = MatchablePairs(
                                    page=self.page,
                                    left_items=widget_data["data"]["left_items"],
                                    right_items=widget_data["data"]["right_items"]
                                )
                                widgets.append(task_widget.build())
                                current_page.task_widgets.append(task_widget)
                                print(f"      ✓ Successfully created widget: {widget_type}")
                            elif widget_type == "draggable_text":
                                task_widget = DraggableText(
                                    page=self.page,
                                    text=widget_data["data"]["text"],
                                    gaps_idx=widget_data["data"]["gaps_idx"],
                                    options=widget_data["data"]["options"]
                                )
                                widgets.append(task_widget.build())
                                current_page.task_widgets.append(task_widget)
                                print(f"      ✓ Successfully created widget: {widget_type}")
                            elif widget_type == "picture_drag":
                                task_widget = PictureDrag(
                                    page=self.page,
                                    image_path=widget_data["data"]["image_path"],
                                    options=widget_data["data"]["options"],
                                    correct_option_index=widget_data["data"]["correct_option_index"]
                                )
                                widgets.append(task_widget.build())
                                current_page.task_widgets.append(task_widget)
                                print(f"      ✓ Successfully created widget: {widget_type}")
                            else:
                                widget = self._create_widget(widget_data)
                                if widget:
                                    widgets.append(widget)
                                    print(f"      ✓ Successfully created widget: {widget_type}")
                                else:
                                    print(f"      ✗ Failed to create widget: {widget_type} (returned None)")
                        except Exception as e:
                            print(f"      ✗ Error creating widget {j}: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            continue
                
                # Add some spacing between widgets
                if widgets:
                    for i in range(1, len(widgets) * 2 - 1, 2):
                        widgets.insert(i, ft.Divider())
                
                current_page.content = ft.Column(widgets, alignment=ft.MainAxisAlignment.CENTER)
                self.pages.append(current_page)
                print(f"  Successfully created page {i} with {len(widgets)} widgets")
                
            # --- Add the ending page ---
            from pages.Widgetlibary.Lectionwidgets import LectionEndPage
            end_page = LectionEndPage(page=self.page)
            self.pages.append(end_page)

            print(f"\nAll {len(self.pages)} pages processed (including ending page).")
            
        except Exception as e:
            print(f"Error in parse_lection: {str(e)}")
            import traceback
            traceback.print_exc()
            self.pages = []
        
    def get_pages(self):
        return self.pages

if __name__ == "__main__":
    lection = LectionParser("lection_example.json")
    lection.parse_lection()
    #Print pages and their content
    for page in lection.pages:
        print(page.content)