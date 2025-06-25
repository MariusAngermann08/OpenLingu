#!/usr/bin/env python3
"""
Script to add a new lection to the OpenLingu server through the console.
"""

import json
import requests
import os
from typing import Optional, Dict, Any

# Server configuration
BASE_URL = "http://localhost:8000"

def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Helper function to get user input with an optional default value."""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    if not value and default is not None:
        return default
    return value

def get_json_file() -> dict:
    """Prompt user for a JSON file path and return its content as a dict."""
    while True:
        try:
            file_path = input("Path to JSON file with lection content: ").strip('"')
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found. Please try again.")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file: {e}. Please try again.")
        except Exception as e:
            print(f"Error reading file: {e}. Please try again.")

def add_lection() -> None:
    """Add a new lection by collecting input and sending to the server."""
    print("\n=== Add New Lection ===\n")
    
    # Collect input
    language_name = get_input("Language name (e.g., 'german')")
    lection_name = get_input("Lection name")
    username = get_input("Your username")
    token = get_input("Your authentication token")
    
    print("\n=== Lection Content ===")
    print("1. Enter JSON content directly")
    print("2. Load from a JSON file")
    choice = input("Choose an option (1-2): ").strip()
    
    if choice == "1":
        print("\nEnter the JSON content (press Ctrl+D on a new line to finish):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        content = '\n'.join(lines)
        # Validate and parse JSON
        try:
            content = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON content: {e}")
            return
    elif choice == "2":
        content = get_json_file()
    else:
        print("Invalid choice. Operation cancelled.")
        return
    
    # Prepare the request
    url = f"{BASE_URL}/languages/{language_name}/lections/add"
    headers = {"Content-Type": "application/json"}
    data = {
        "lection_name": lection_name,
        "username": username,
        "token": token,
        "content": content
    }
    
    print("\nSending request to server...")
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print("\n✅ Success! Lection added.")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                print(f"Response: {e.response.text}")
            except:
                pass

def edit_lection() -> None:
    print("\n=== Edit Existing Lection ===\n")
    language_name = get_input("Language name (e.g., 'german')")
    lection_name = get_input("Lection name")
    username = get_input("Your username")
    token = get_input("Your authentication token")
    print("\n=== New Lection Content ===")
    print("1. Enter JSON content directly")
    print("2. Load from a JSON file")
    choice = input("Choose an option (1-2): ").strip()
    if choice == "1":
        print("\nEnter the JSON content (press Ctrl+D on a new line to finish):")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        content = '\n'.join(lines)
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON content: {e}")
            return
    elif choice == "2":
        content = get_json_file()
    else:
        print("Invalid choice. Operation cancelled.")
        return
    url = f"{BASE_URL}/languages/{language_name}/lections/edit"
    headers = {"Content-Type": "application/json"}
    data = {
        "lection_name": lection_name,
        "username": username,
        "token": token,
        "content": content
    }
    print("\nSending edit request to server...")
    try:
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        print("\n✅ Success! Lection edited.")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                print(f"Response: {e.response.text}")
            except:
                pass

def remove_lection() -> None:
    print("\n=== Remove Lection ===\n")
    language_name = get_input("Language name (e.g., 'german')")
    lection_name = get_input("Lection name")
    username = get_input("Your username")
    token = get_input("Your authentication token")
    url = f"{BASE_URL}/languages/{language_name}/lections/{lection_name}/delete"
    headers = {"Content-Type": "application/json"}
    data = {
        "username": username,
        "token": token
    }
    print("\nSending delete request to server...")
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print("\n✅ Success! Lection removed.")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                print(f"Response: {e.response.text}")
            except:
                pass

def main() -> None:
    """Main function to run the script."""
    print("OpenLingu Lection Manager")
    print("=======================")
    while True:
        print("\nOptions:")
        print("1. Add a new lection")
        print("2. Edit an existing lection")
        print("3. Remove a lection")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            add_lection()
        elif choice == "2":
            edit_lection()
        elif choice == "3":
            remove_lection()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
