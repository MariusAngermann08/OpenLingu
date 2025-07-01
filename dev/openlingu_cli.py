#!/usr/bin/env python3
"""
OpenLingu CLI Tool

A comprehensive command-line interface for managing OpenLingu content.
Handles both language and lection management with contributor authentication.
"""

import os
import sys
import json
import requests
from typing import Optional, Dict, Any, List

# Server configuration
BASE_URL = "http://zuhause.ipv64.de:8100/"

# Global variables for authentication
AUTH_TOKEN: Optional[str] = None
CURRENT_USER: Optional[str] = None

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str) -> None:
    """Print a formatted header."""
    clear_screen()
    print(f"\n=== {title} ===\n")

def get_input(prompt: str, default: Optional[str] = None, password: bool = False) -> str:
    """Get user input with an optional default value and password masking."""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt).strip()
    
    if not value and default is not None:
        return default
    return value

def get_json_file() -> Dict[str, Any]:
    """Prompt user for a JSON file path and return its content as a dict."""
    while True:
        try:
            file_path = get_input("Path to JSON file with content").strip('"')
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: File '{file_path}' not found. Please try again.")
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in file: {e}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

def get_auth_token(username: str, password: str) -> Optional[str]:
    """Authenticate and get JWT token for the contributor."""
    global AUTH_TOKEN, CURRENT_USER
    try:
        # Send as query parameters
        params = {
            "username": username,
            "password": password
        }
        url = f"{BASE_URL}/login_contributer"
        print(f"\n[DEBUG] Calling URL: {url}?username={username}&password=*****")
        response = requests.get(url, params=params)
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response content: {response.text}")
        response.raise_for_status()
        token_data = response.json()
        AUTH_TOKEN = token_data.get("access_token")
        CURRENT_USER = username
        return AUTH_TOKEN
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Authentication failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"[ERROR] {error_data}")
            except:
                print(f"Status code: {e.response.status_code}")
                if e.response.text:
                    print(f"Response: {e.response.text}")
        return None

def get_auth_headers() -> Dict[str, str]:
    """Generate authorization headers with the current token."""
    if not AUTH_TOKEN:
        raise ValueError("Not authenticated. Please log in first.")
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}

def require_auth() -> bool:
    """Ensure user is authenticated, prompt for login if not."""
    global AUTH_TOKEN, CURRENT_USER
    if AUTH_TOKEN:
        return True
    
    print("\n[INFO] Authentication required")
    username = get_input("Username")
    password = get_input("Password", password=True)
    
    return bool(get_auth_token(username, password))

def handle_api_error(e: Exception, operation: str) -> None:
    """Handle API errors consistently."""
    print(f"\n[ERROR] Error during {operation}:")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_data = e.response.json()
            print(f"[ERROR] {error_data.get('detail', 'Unknown error')}")
        except:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
    else:
        print(str(e))

# Language Management
def list_languages() -> None:
    """List all available languages."""
    print_header("Available Languages")
    
    try:
        response = requests.get(f"{BASE_URL}/languages")
        response.raise_for_status()
        languages = response.json()
        
        if not languages:
            print("No languages found.")
            return
            
        for i, lang in enumerate(languages, 1):
            if isinstance(lang, dict):
                # Handle case where lang is a dictionary
                print(f"{i}. {lang.get('name', 'Unnamed')} (ID: {lang.get('id', 'N/A')})")
                if 'description' in lang:
                    print(f"   {lang['description']}")
            else:
                # Handle case where lang is a string
                print(f"{i}. {lang}")
            print()
                
    except Exception as e:
        handle_api_error(e, "listing languages")

def add_language() -> None:
    """Add a new language."""
    global CURRENT_USER, AUTH_TOKEN
    if not require_auth():
        return
    
    print_header("Add New Language")
    language_name = get_input("Language name (e.g., 'german')")
    
    try:
        headers = get_auth_headers()
        # Include the username in the request body
        data = {"username": CURRENT_USER}
        print(f"[DEBUG] Sending request to {BASE_URL}/add_language/{language_name}")
        print(f"[DEBUG] Headers: {headers}")
        print(f"[DEBUG] Data: {data}")
        
        response = requests.post(
            f"{BASE_URL}/add_language/{language_name}",
            headers=headers,
            json=data
        )
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response content: {response.text}")
        
        response.raise_for_status()
        print("\n[SUCCESS] Language added successfully!")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        handle_api_error(e, "adding language")

def delete_language() -> None:
    """Delete a language."""
    if not require_auth():
        return
    
    print_header("Delete Language")
    language_name = get_input("Name of the language to delete")
    
    confirm = get_input(f"[WARNING]  Are you sure you want to delete '{language_name}'? This cannot be undone. (y/N)", "n")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    try:
        headers = get_auth_headers()
        response = requests.delete(
            f"{BASE_URL}/delete_language/{language_name}",
            headers=headers
        )
        response.raise_for_status()
        print("\n[SUCCESS] Language deleted successfully!")
    except Exception as e:
        handle_api_error(e, "deleting language")

# Lection Management
def list_lections() -> None:
    """List all lections for a language."""
    print_header("List Lections")
    language_name = get_input("Language name")
    
    try:
        response = requests.get(f"{BASE_URL}/languages/{language_name}/lections")
        response.raise_for_status()
        lections = response.json()
        
        if not lections:
            print(f"No lections found for language '{language_name}'.")
            return
            
        print(f"\nLections in {language_name}:")
        for i, lec in enumerate(lections, 1):
            print(f"{i}. {lec.get('title', 'Untitled')} (ID: {lec.get('id', 'N/A')})")
    except Exception as e:
        handle_api_error(e, "listing lections")

def add_lection() -> None:
    """Add a new lection."""
    if not require_auth():
        return
    
    print_header("Add New Lection")
    
    # Get basic info
    language_name = get_input("Language name")
    lection_name = get_input("Lection name")
    
    # Get content
    print("\n=== Lection Content ===")
    print("1. Enter JSON content directly")
    print("2. Load from a JSON file")
    choice = get_input("Choose an option (1-2)")
    
    if choice == "1":
        print("\nEnter the JSON content (press Ctrl+D on a new line to finish):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        try:
            content = json.loads('\n'.join(lines))
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return
    elif choice == "2":
        content = get_json_file()
    else:
        print("[ERROR] Invalid choice.")
        return
    
    # Prepare and send request
    try:
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "lection_name": lection_name,
            "content": content
        }
        
        response = requests.post(
            f"{BASE_URL}/add_lection/{language_name}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        print("\n[SUCCESS] Lection added successfully!")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        handle_api_error(e, "adding lection")

def edit_lection() -> None:
    """Edit an existing lection."""
    if not require_auth():
        return
    
    print_header("Edit Lection")
    
    # Get basic info
    language_name = get_input("Language name")
    lection_name = get_input("Name of the lection to edit")
    
    # Get new content
    print("\n=== New Lection Content ===")
    print("1. Enter new JSON content directly")
    print("2. Load new content from a JSON file")
    choice = get_input("Choose an option (1-2)")
    
    if choice == "1":
        print("\nEnter the new JSON content (press Ctrl+D on a new line to finish):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        try:
            content = json.loads('\n'.join(lines))
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return
    elif choice == "2":
        content = get_json_file()
    else:
        print("[ERROR] Invalid choice.")
        return
    
    # Prepare and send request
    try:
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "lection_name": lection_name,
            "content": content
        }
        
        response = requests.put(
            f"{BASE_URL}/edit_lection/{language_name}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        print("\n[SUCCESS] Lection updated successfully!")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        handle_api_error(e, "updating lection")

def delete_lection() -> None:
    """Delete a lection."""
    if not require_auth():
        return
    
    print_header("Delete Lection")
    
    language_name = get_input("Language name")
    lection_name = get_input("Name of the lection to delete")
    
    confirm = get_input(f"[WARNING]  Are you sure you want to delete '{lection_name}'? This cannot be undone. (y/N)", "n")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    try:
        headers = get_auth_headers()
        response = requests.delete(
            f"{BASE_URL}/delete_lection/{language_name}/{lection_name}",
            headers=headers
        )
        response.raise_for_status()
        print("\n[SUCCESS] Lection deleted successfully!")
    except Exception as e:
        handle_api_error(e, "deleting lection")

def view_lection() -> None:
    """View lection content by title."""
    print_header("View Lection")
    
    language_name = get_input("Language name")
    lection_title = get_input("Lection title")
    
    try:
        # Try to get lection by title
        response = requests.get(f"{BASE_URL}/languages/{language_name}/lections/by_title/{lection_title}")
        response.raise_for_status()
        lection = response.json()
        
        print("\n" + "="*50)
        print(f"Title: {lection.get('title', 'Untitled')}")
        print(f"Language: {language_name}")
        print(f"ID: {lection.get('id', 'N/A')}")
        print("\nContent:")
        print(json.dumps(lection.get('content', {}), indent=2))
        print("="*50 + "\n")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"[ERROR] Lection with title '{lection_title}' not found in language '{language_name}'")
        else:
            handle_api_error(e, "fetching lection")
    except Exception as e:
        handle_api_error(e, "fetching lection")

def register() -> None:
    """Register a new user."""
    print_header("Register New User")
    
    username = get_input("Username")
    email = get_input("Email")
    password = get_input("Password", password=True)
    confirm_password = get_input("Confirm Password", password=True)
    
    if password != confirm_password:
        print("\n[ERROR] Passwords do not match!")
        input("\nPress Enter to continue...")
        return
    
    try:
        # Prepare the request data as JSON
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        # Make the request with JSON body
        response = requests.post(
            f"{BASE_URL}/register",
            json=data
        )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n[SUCCESS] Registration successful!")
        print(f"You can now log in with your username and password.")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            print("\n[ERROR] Username or email already exists.")
        elif e.response.status_code == 400:
            try:
                error_data = e.response.json()
                print(f"\n[ERROR] {error_data.get('detail', 'Invalid input data')}")
            except:
                print(f"\n[ERROR] {e.response.text}")
        else:
            print(f"\n[ERROR] Registration failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
    
    input("\nPress Enter to continue...")

def login(username: str = None, password: str = None) -> bool:
    """Handle contributor login."""
    global AUTH_TOKEN, CURRENT_USER
    
    print("\n=== Contributor Login ===\n")
    
    # If username and password are not provided, prompt for them
    if username is None:
        username = get_input("Username")
    if password is None:
        password = get_input("Password", password=True)
    
    token = get_auth_token(username, password)
    if token:
        print(f"[SUCCESS] Successfully logged in as {username}")
        return True
    else:
        print("[ERROR] Login failed. Please check your credentials.")
        return False

def main_menu() -> None:
    """Display the main menu and handle user choices."""
    global AUTH_TOKEN, CURRENT_USER
    
    while True:
        print_header("OpenLingu CLI Tool")
        if CURRENT_USER:
            print(f"[USER] Logged in as: {CURRENT_USER}")
        else:
            print("[AUTH] Not authenticated")
        
        print("\nMain Menu:")
        print("1. Login")
        print("2. Register")
        print("3. Language Management")
        print("4. Lection Management")
        print("0. Exit")
        
        choice = get_input("\nEnter your choice (0-4)")
        
        if choice == "1":
            if login():
                input("\nPress Enter to continue...")
            else:
                input("\nPress Enter to try again...")
        elif choice == "2":
            register()
        elif choice == "3":
            language_menu()
        elif choice == "4":
            lection_menu()
        elif choice == "0":
            print("\n[INFO] Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            input("\nPress Enter to continue...")

def language_menu() -> None:
    """Display the language management menu."""
    while True:
        print_header("Language Management")
        print("1. List all languages")
        print("2. Add a new language")
        print("3. Delete a language")
        print("0. Back to main menu")
        
        choice = get_input("\nEnter your choice (0-3)")
        
        if choice == "1":
            list_languages()
            input("\nPress Enter to continue...")
        elif choice == "2":
            add_language()
            input("\nPress Enter to continue...")
        elif choice == "3":
            delete_language()
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            print("\n❌ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def lection_menu() -> None:
    """Display the lection management menu."""
    while True:
        print_header("Lection Management")
        print("1. List all lections in a language")
        print("2. View a lection")
        print("3. Add a new lection")
        print("4. Edit a lection")
        print("5. Delete a lection")
        print("0. Back to main menu")
        
        choice = get_input("\nEnter your choice (0-5)")
        
        if choice == "1":
            list_lections()
            input("\nPress Enter to continue...")
        elif choice == "2":
            view_lection()
            input("\nPress Enter to continue...")
        elif choice == "3":
            add_lection()
            input("\nPress Enter to continue...")
        elif choice == "4":
            edit_lection()
            input("\nPress Enter to continue...")
        elif choice == "5":
            delete_lection()
            input("\nPress Enter to continue...")
        elif choice == "0":
            break
        else:
            print("\n Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

def main():
    try:
        # Check for command line arguments for direct login
        if len(sys.argv) == 3:
            username = sys.argv[1]
            password = sys.argv[2]
            print(f"[INFO] Attempting to login as {username}...")
            if login(username, password):
                print("[SUCCESS] Login successful!")
                return
            else:
                print("[ERROR] Login failed!")
                sys.exit(1)

        main_menu()
    except KeyboardInterrupt:
        print("\n\n[INFO] Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
