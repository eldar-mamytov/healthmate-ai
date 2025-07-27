#!/usr/bin/env python3
"""
Test script for FLAN-T5 improvements
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Get a fresh token first
def get_token():
    response = requests.post(
        f"{BASE_URL}/auth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=testuser@example.com&password=strongpassword123"
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

def test_flan_t5():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test cases
    test_cases = [
        "I have a headache",
        "I have a cold",
        "My throat is sore",
        "I feel tired and have a fever"
    ]
    
    for message in test_cases:
        print(f"\n--- Testing: '{message}' ---")
        
        data = {
            "message": message,
            "model_choice": "flan-t5"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/ai/chat/", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['content']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_flan_t5() 