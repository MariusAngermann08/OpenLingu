import requests

username = "admin"
password = "admin"
email = "admin@admin.de"

response = requests.get("http://localhost:8000/")
print(response.json())

