#!/usr/bin/env python3
"""
Test script for improved FLAN-T5 implementation
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

def test_improved_flan():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test cases based on the chat conversation
    test_cases = [
        "I have a headache",
        "I have a cold", 
        "what can I do if I am having runny nose and sore throat",
        "My throat is sore and I have a fever",
        "I feel tired and have body aches"
    ]
    
    for message in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: '{message}'")
        print(f"{'='*60}")
        
        data = {
            "message": message,
            "model_choice": "flan-t5"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/ai/chat/", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response: {result['content']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_improved_flan() 