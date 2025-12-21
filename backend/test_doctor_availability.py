import requests
import json

#Test changing Doctor availability
doctor_id = 2 #doc d2
url = f"http://127.0.0.1:8001/api/doctors/{doctor_id}/availability/"

print(f"Testing Doctor Availability API...")
print(f"URL: {url}")

#Test 1: Make Doctor Available
print("\n1. Setting Doctor to Available (True):")
data = {"available": True}
response = requests.put(url, json = data)
print(f" Status: {response.status_code}")
print(f" Response: {response.json()}")

#Test 2: Make Doctor Unavailable
print("\n1. Setting Doctor to Unavailable (False):")
data = {"available": False}
response = requests.put(url, json = data)
print(f" Status: {response.status_code}")
print(f" Response: {response.json()}")

#Test 3: Check current Status
print("\n3. Checking all doctors: ")
response = requests.get("http://127.0.0.1:8001/api/doctors/")
doctors = response.json()
for doctor in doctors:
    print(f"Doctor {doctor['id']}: {doctor['name']} - Available: {doctor['available']}")