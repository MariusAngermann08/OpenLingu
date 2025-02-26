import json
import requests

class Database:
    firebase_url = ""
    API_KEY = ""
    def __init__(self, database_url, apikey):
        self.firebase_url = database_url+".json"
        self.API_KEY = apikey
        self.users = {}

    def sign_in(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        data = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            user_data = response.json()
            print(user_data["localId"])
            return user_data["localId"]  # This is the user's unique ID
        else:
            print("Login failed:", response.text)
            return None
    def sign_up(self, email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=data)
        print(response.json())

    def create_user(self, name, pname, age, mlang):
        self.users[name] = {"name": pname, "age": age, "mlang": mlang}

    def update_user(self):
        pass

    def push_to_database(self):
        response = requests.patch(url=self.firebase_url, json=self.users)
        print(response)

if __name__ == "__main__":
    key = "AIzaSyDNFod33FXMK5IhBYi_d9RoxALn0LsqQo4"
    database = Database(database_url="https://openlingu-26798-default-rtdb.europe-west1.firebasedatabase.app/",apikey=key)
    id = database.sign_in(email="marius.angermann.2018@gmail.com", password="Paar3414")
    database.create_user(name=id, pname="Marius Angermann", age=16, mlang="german")
    database.push_to_database()

