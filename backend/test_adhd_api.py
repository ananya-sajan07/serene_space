import requests
import json

url = "http://127.0.0.1:8001/api/predict_adhd/"

# Test data (10 features from mentor's document)
test_data = {
    "gender": "Male",
    "easily_distracted": 2,
    "forgetful_daily_tasks": 1,
    "poor_organization": 2,
    "difficulty_sustaining_attention": 3,
    "restlessness": 2,
    "impulsivity_score": 1,
    "screen_time_daily": 7.8,
    "phone_unlocks_per_day": 120,
    "working_memory_score": 45
}

print("Testing ADHD Prediction API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(url, json=test_data)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nPrediction: {result.get('prediction')}")
        print(f"Message: {result.get('message')}")
    else:
        print(f"\nError: {response.text}")
        
except Exception as e:
    print(f"\nRequest failed: {e}")