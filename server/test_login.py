import requests
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.append(str(Path(__file__).parent))

def test_login():
    print("Testing login endpoint...")
    
    # Replace with your actual test credentials
    test_username = "Marius"
    test_password = "Marius"  # Make sure this is the correct password
    
    try:
        # Test login with correct credentials
        print(f"\n[TEST] Logging in with username: {test_username}")
        form_data = {
            "username": test_username,
            "password": test_password
        }
        print(f"[DEBUG] Sending form data: {form_data}")
        
        response = requests.post(
            "http://localhost:8000/login",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Login successful!")
            print(f"Access token: {data.get('access_token')}")
            print(f"Token type: {data.get('token_type')}")
            return data.get('access_token')
        else:
            print(f"[ERROR] Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_login()
