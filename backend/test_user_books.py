import requests

print("Testing User Book APIs...")

# Test 1: Get all books
print("\n1. Getting all active books:")
response = requests.get("http://127.0.0.1:8001/api/user/books/")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Found {data['count']} books")
    for book in data['books']:
        print(f"   - {book['title']} ({book['category']})")
else:
    print(f"   Error: {response.text}")

# Test 2: Get ADHD books only
print("\n2. Getting ADHD books only:")
response = requests.get("http://127.0.0.1:8001/api/user/books/?category=adhd")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Found {data['count']} ADHD books")
else:
    print(f"   Error: {response.text}")

# Test 3: Get single book
print("\n3. Getting single book (ID: 1):")
response = requests.get("http://127.0.0.1:8001/api/user/books/1/")
if response.status_code == 200:
    book = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Title: {book['title']}")
    print(f"   Author: {book['author']}")
    print(f"   Category: {book['category']}")
else:
    print(f"   Error: {response.text}")