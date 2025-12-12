import requests
import json

def test_login(email, password):
    url = "http://127.0.0.1:8001/api/login/"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Email: {email}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:200]}")  # First 200 chars
    print("-" * 50)

# Test pending doctor with correct password

#Test 1: User Login (Success)
test_login("d@gmail.com", "123456")

# Test 2 Update test_login_api.py
# test_login("d3@gmail.com", "123456")  # Approved doctor

#Test 3: Pending Doctor Login (Should show "not approved" message)
# test_login("d2@gmail.com", "123456")

#Test 4: Rejected Doctor Login (Should show "not approved" message)
#test_login("d1@gmail.com", "123456")  # Rejected doctor

#Test 5: Invalid Credentials
# test_login("wrong@example.com", "wrong")