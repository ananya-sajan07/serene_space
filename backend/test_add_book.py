import requests
import json

url = "http://127.0.0.1:8001/api/books/"

# Test book data
book_data = {
    "title": "Coping with Depression",
    "author": "Dr. Sarah Johnson",
    "category": "depression",
    "description": "A guide to understanding and managing depression symptoms.",
    "is_active": True
}

print("Testing Add Book API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(book_data, indent=2)}")

try:
    response = requests.post(url, json=book_data)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n Book added successfully!")
        print(f" Title: {result['book']['title']}")
        print(f" Author: {result['book']['author']}")
        print(f" Category: {result['book']['category']}")
    else:
        print(f"\nError: {response.text}")
        
except Exception as e:
    print(f"\nRequest failed: {e}")