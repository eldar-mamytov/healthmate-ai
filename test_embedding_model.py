#!/usr/bin/env python3
"""
Test script for embedding model to identify issues
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

def test_embedding_model():
    token = get_token()
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test cases for embedding model
    test_cases = [
        "I have a headache",
        "My throat is sore",
        "I have a cold with runny nose",
        "I feel tired and have body aches"
    ]
    
    for message in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing Embedding Model: '{message}'")
        print(f"{'='*60}")
        
        data = {
            "message": message,
            "model_choice": "embedding"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/ai/chat/", headers=headers, json=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['content']}")
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_embedding_endpoint():
    """Test the /ai/embed/ endpoint directly"""
    token = get_token()
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print(f"\n{'='*60}")
    print("Testing /ai/embed/ endpoint directly")
    print(f"{'='*60}")
    
    data = {
        "text": "I have a headache"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/embed/", headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding endpoint works: {len(result['embedding'])} dimensions")
        else:
            print(f"❌ Embedding endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Embedding Model...")
    test_embedding_model()
    
    print("\n" + "="*60)
    print("Testing Embedding Endpoint...")
    test_embedding_endpoint() 