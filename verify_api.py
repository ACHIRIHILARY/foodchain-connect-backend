import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/users"

def test_registration():
    print("Testing Registration...")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "SEEKER",
        "phone_number": "1234567890",
        "address": "123 Test St"
    }
    try:
        response = requests.post(f"{BASE_URL}/register/", json=data)
        if response.status_code == 201:
            print("Registration Successful")
            return True
        else:
            print(f"Registration Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Registration Error: {e}")
        return False

def test_login():
    print("\nTesting Login...")
    data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    try:
        response = requests.post(f"{BASE_URL}/login/", json=data)
        if response.status_code == 200:
            print("Login Successful")
            return response.json()
        else:
            print(f"Login Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def test_profile(access_token):
    print("\nTesting Profile Access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{BASE_URL}/me/", headers=headers)
        if response.status_code == 200:
            print("Profile Access Successful")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Profile Access Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Profile Error: {e}")
        return False

if __name__ == "__main__":
    if test_registration():
        tokens = test_login()
        if tokens:
            test_profile(tokens['access'])
