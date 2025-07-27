#!/usr/bin/env python3
"""
Test database connection and check if tables exist
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        else:
            print(f"Health error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")

def test_auth():
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=testuser@example.com&password=strongpassword123"
        )
        print(f"Auth status: {response.status_code}")
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"Got token: {token[:20]}...")
            return token
        else:
            print(f"Auth error: {response.text}")
            return None
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def test_embedding_with_token(token):
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "message": "I have a headache",
        "model_choice": "embedding"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat/", headers=headers, json=data)
        print(f"Embedding test status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Embedding success: {result['content']}")
        else:
            print(f"❌ Embedding failed: {response.text}")
    except Exception as e:
        print(f"❌ Embedding error: {e}")

if __name__ == "__main__":
    print("Testing database connection...")
    test_health()
    
    print("\nTesting authentication...")
    token = test_auth()
    
    print("\nTesting embedding model...")
    test_embedding_with_token(token) 