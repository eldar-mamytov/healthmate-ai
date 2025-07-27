import requests
import json

BASE_URL = "http://localhost:8000"

# Get a fresh token
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

# Get fresh token
access_token = get_token()

if access_token:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # --- Test the Chat Endpoint (OpenAI Model) ---
    print("\n--- Testing Chat (OpenAI) ---")
    chat_openai_url = f"{BASE_URL}/ai/chat/"
    chat_openai_data = {
        "message": "What is the capital of France?",
        "model_choice": "openai"
    }
    try:
        chat_openai_response = requests.post(chat_openai_url, headers=headers, json=chat_openai_data)
        chat_openai_response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        print("Chat (OpenAI) Status Code:", chat_openai_response.status_code)
        print("Chat (OpenAI) Response:", chat_openai_response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Chat (OpenAI) failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred during OpenAI chat: {e}")

    # --- Test the Chat Endpoint (FLAN-T5 Model) ---
    print("\n--- Testing Chat (FLAN-T5) ---")
    chat_flan_url = f"{BASE_URL}/ai/chat/"
    chat_flan_data = {
        "message": "I have a headache",
        "model_choice": "flan-t5"
    }
    try:
        chat_flan_response = requests.post(chat_flan_url, headers=headers, json=chat_flan_data)
        chat_flan_response.raise_for_status()
        print("Chat (FLAN-T5) Status Code:", chat_flan_response.status_code)
        print("Chat (FLAN-T5) Response:", chat_flan_response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Chat (FLAN-T5) failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred during FLAN-T5 chat: {e}")

    # --- Test the Chat Endpoint (Mistral Local Model) ---
    print("\n--- Testing Chat (Mistral) ---")
    chat_mistral_url = f"{BASE_URL}/ai/chat/"
    chat_mistral_data = {
        "message": "Tell me a short story about a brave knight.",
        "model_choice": "mistral"
    }
    try:
        chat_mistral_response = requests.post(chat_mistral_url, headers=headers, json=chat_mistral_data)
        chat_mistral_response.raise_for_status()
        print("Chat (Mistral) Status Code:", chat_mistral_response.status_code)
        print("Chat (Mistral) Response:", chat_mistral_response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Chat (Mistral) failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred during Mistral chat: {e}")

    # --- Test the Embedding Endpoint ---
    print("\n--- Testing Embedding ---")
    embed_url = f"{BASE_URL}/ai/embed/"
    embed_data = {
        "text": "This is a test sentence for embedding."
    }
    try:
        embed_response = requests.post(embed_url, headers=headers, json=embed_data)
        embed_response.raise_for_status()
        print("Embedding Status Code:", embed_response.status_code)
        print("Embedding Response:", embed_response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Embedding failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred during embedding: {e}")

    # --- Test Simple Authenticated Endpoint ---
    print("\n--- Testing Simple Authenticated Endpoint ---")
    test_auth_url = f"{BASE_URL}/auth/test-auth/"
    try:
        test_auth_response = requests.get(test_auth_url, headers=headers)
        test_auth_response.raise_for_status()
        print("Simple Auth Test Status Code:", test_auth_response.status_code)
        print("Simple Auth Test Response:", test_auth_response.json())
    except requests.exceptions.HTTPError as e:
        print(f"Simple Auth Test failed: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred during simple auth test: {e}")

else:
    print("\nAccess token is missing. Please ensure login was successful and token is correctly pasted.") 