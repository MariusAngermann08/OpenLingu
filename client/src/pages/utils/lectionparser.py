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
    def __init__(self, lection_json: str):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If path is relative, resolve it relative to the current file's directory
        if not os.path.isabs(lection_json):
            # First try relative to the current working directory
            cwd_path = os.path.abspath(lection_json)
            if os.path.exists(cwd_path):
                self.lection_json = cwd_path
            else:
                # If not found, try relative to the script directory
                script_path = os.path.join(script_dir, lection_json)
                if os.path.exists(script_path):
                    self.lection_json = script_path
                else:
                    # If still not found, try one level up (in case we're running from src/)
                    parent_dir = os.path.dirname(script_dir)
                    parent_path = os.path.join(parent_dir, lection_json)
                    if os.path.exists(parent_path):
                        self.lection_json = parent_path
                    else:
                        # If still not found, use the original path (will raise error)
                        self.lection_json = lection_json
        else:
            self.lection_json = lection_json
            
        print(f"Loading lection from: {self.lection_json}")
        
        # Load json from file
        try:
            with open(self.lection_json, "r", encoding='utf-8') as f:
                self.lection = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: Could not find lection file at {self.lection_json}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Script directory: {script_dir}")
            raise
    


    def _create_widget(self, widget_data: Dict[str, Any]) -> ft.Control:
        widget_type = widget_data["type"]
        data = widget_data["data"]
        
        if widget_type == "underlined_text":
            return UnderlinedText(
                text=data["text"],
                underlined=data["underlined"],
                font_size=data.get("font_size", 14),
                bgcolor=data.get("bgcolor")
            )
            
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
        self.id = self.lection["id"]
        self.title = self.lection["title"]
        self.description = self.lection["description"]
        self.language = self.lection["language"]
        self.difficulty = self.lection["difficulty"]
        self.created_at = self.lection["created_at"]
        self.updated_at = self.lection["updated_at"]
        
        self.pages = []
        for page_data in self.lection["pages"]:
            current_page = Page()
            widgets = []
            
            # Add title if exists
            if "title" in page_data:
                widgets.append(ft.Text(
                    page_data["title"],
                    size=24,
                    weight="bold",
                    text_align=ft.TextAlign.CENTER,
                    width=float("inf"),
                ))
            
            # Add description if exists
            if "description" in page_data:
                widgets.append(ft.Text(
                    page_data["description"],
                    size=16,
                    italic=True,
                    text_align=ft.TextAlign.CENTER
                ))
            
            # Add widgets
            for widget_data in page_data["widgets"]:
                try:
                    widget = self._create_widget(widget_data)
                    widgets.append(widget)
                except Exception as e:
                    print(f"Error creating widget: {e}")
                    continue
            
            # Add some spacing between widgets
            for i in range(1, len(widgets) * 2 - 1, 2):
                widgets.insert(i, ft.Divider())
            
            current_page.content = ft.ListView(
                controls=widgets,
                expand=True,
                spacing=10,
                padding=20
            )
            self.pages.append(current_page)
        
    def get_pages(self):
        return self.pages

if __name__ == "__main__":
    lection = LectionParser("lection_example.json")
    lection.parse_lection()
    #Print pages and their content
    for page in lection.pages:
        print(page.content)