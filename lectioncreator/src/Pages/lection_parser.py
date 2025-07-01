import json
from typing import Dict, Any, List, Optional

class LectionParser:
    def __init__(self, lection_data: Dict[str, Any]):
        """Initialize the parser with lection data.
        
        Args:
            lection_data: The lection data as a dictionary
        """
        self.lection_data = lection_data
        self.pages = []
        
    def parse(self) -> Dict[str, Any]:
        """Parse the lection data into editor-compatible format.
        
        Returns:
            Dict containing parsed lection data
        """
        try:
            # Extract basic lection info
            result = {
                "id": self.lection_data.get("id", ""),
                "title": self.lection_data.get("title", ""),
                "description": self.lection_data.get("description", ""),
                "language": self.lection_data.get("language", "en"),
                "difficulty": self.lection_data.get("difficulty", "beginner"),
                "pages": []
            }
            
            # Get the content which contains the pages
            content = self.lection_data.get("content", {})
            if not content:
                return result
                
            # Handle nested content structure
            if "content" in content and isinstance(content["content"], dict):
                nested_content = content["content"]
                # Update metadata from nested content
                result["title"] = nested_content.get("title", result["title"])
                result["description"] = nested_content.get("description", result["description"])
                result["language"] = nested_content.get("language", result["language"])
                result["difficulty"] = nested_content.get("difficulty", result["difficulty"])
                content = nested_content
            else:
                # Update metadata from direct content
                result["title"] = content.get("title", result["title"])
                result["description"] = content.get("description", result["description"])
                result["language"] = content.get("language", result["language"])
                result["difficulty"] = content.get("difficulty", result["difficulty"])
            
            # Process pages
            if "pages" not in content or not content["pages"]:
                return result
                
            for page_data in content["pages"]:
                page = {
                    "title": page_data.get("title", ""),
                    "description": page_data.get("description", ""),
                    "widgets": []
                }
                
                # Process widgets
                if "widgets" in page_data and page_data["widgets"]:
                    for widget_data in page_data["widgets"]:
                        widget_type = widget_data.get("type")
                        if not widget_type:
                            continue
                            
                        # Create a clean widget dict with only necessary data
                        widget = {
                            "type": widget_type,
                            "data": widget_data.get("data", {})
                        }
                        
                        # Add widget to page
                        page["widgets"].append(widget)
                
                result["pages"].append(page)
                
            return result
            
        except Exception as e:
            print(f"Error parsing lection data: {e}")
            raise
    
    @staticmethod
    def to_editor_format(lection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert lection data to editor format.
        
        This is a convenience method that creates a parser instance and parses the data.
        """
        parser = LectionParser(lection_data)
        return parser.parse()

    @staticmethod
    def create_empty_lection(title: str = "New Lection", 
                           description: str = "", 
                           language: str = "en") -> Dict[str, Any]:
        """Create a new empty lection with default values."""
        return {
            "title": title,
            "description": description,
            "language": language,
            "difficulty": "beginner",
            "pages": [
                {
                    "title": "Page 1",
                    "description": "",
                    "widgets": []
                }
            ]
        }
