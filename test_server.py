import requests

username = "admin"
password = "admin"
email = "admin@admin.de"

response = requests.get("http://localhost:8000/")
print(response.json())

response = requests.post("http://localhost:8000/register", json={"username": "admin", "password": "admin", "email": "admin@admin.de"})
print(response.json())