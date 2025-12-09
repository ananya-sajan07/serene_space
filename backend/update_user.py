import requests
import json

url = "http://127.0.0.1:8001/api/users/5/"
data = {
    "name": "a",
    "email": "a@gmail.com", 
    "password": "1",
    "is_admin": True
}

response = requests.put(url, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")