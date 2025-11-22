import requests
import json
import datetime

BASE_URL = "http://127.0.0.1:8000/api"

def get_token(username, password):
    response = requests.post(f"{BASE_URL}/users/login/", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()['access']
    return None

def create_user(username, role, email):
    data = {
        "username": username,
        "email": email,
        "password": "password123",
        "role": role,
        "phone_number": "1234567890"
    }
    requests.post(f"{BASE_URL}/users/register/", json=data)

def test_admin_flow():
    print("\n--- Testing Admin Flow ---")
    # Assuming a superuser exists or we can't test this fully without one.
    # For now, we'll skip creating a superuser via script as it requires shell access.
    # We will test if normal user can register as admin (should fail)
    
    print("Attempting to register as ADMIN (should fail)...")
    data = {
        "username": "fakeadmin",
        "email": "fake@admin.com",
        "password": "password123",
        "role": "ADMIN"
    }
    response = requests.post(f"{BASE_URL}/users/register/", json=data)
    if response.status_code == 400:
        print("Success: Public Admin registration blocked.")
    else:
        print(f"Failure: Public Admin registration allowed! {response.status_code}")

def test_core_flow():
    print("\n--- Testing Core Flow ---")
    # Create Provider and Seeker
    create_user("provider1", "PROVIDER", "provider1@test.com")
    create_user("seeker1", "SEEKER", "seeker1@test.com")
    
    provider_token = get_token("provider1", "password123")
    seeker_token = get_token("seeker1", "password123")
    
    if not provider_token or not seeker_token:
        print("Failed to get tokens.")
        return

    # 1. Provider creates listing
    print("Provider creating listing...")
    listing_data = {
        "title": "Fresh Bread",
        "description": "Leftover bread from bakery",
        "quantity": "10 loaves",
        "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
    }
    headers = {"Authorization": f"Bearer {provider_token}"}
    response = requests.post(f"{BASE_URL}/listings/", json=listing_data, headers=headers)
    if response.status_code == 201:
        listing_id = response.json()['id']
        print(f"Listing created: ID {listing_id}")
    else:
        print(f"Failed to create listing: {response.text}")
        return

    # 2. Seeker views listings
    print("Seeker viewing listings...")
    headers = {"Authorization": f"Bearer {seeker_token}"}
    response = requests.get(f"{BASE_URL}/listings/", headers=headers)
    if response.status_code == 200:
        print(f"Seeker sees {len(response.json())} listings.")
    else:
        print(f"Seeker failed to view listings: {response.text}")

    # 3. Seeker applies for listing
    print("Seeker applying for listing...")
    app_data = {"listing": listing_id, "message": "I need this for my shelter."}
    response = requests.post(f"{BASE_URL}/applications/", json=app_data, headers=headers)
    if response.status_code == 201:
        app_id = response.json()['id']
        print(f"Application created: ID {app_id}")
    else:
        print(f"Failed to apply: {response.text}")
        return

    # 4. Provider approves application
    print("Provider approving application...")
    headers = {"Authorization": f"Bearer {provider_token}"}
    status_data = {"status": "APPROVED"}
    response = requests.post(f"{BASE_URL}/applications/{app_id}/update_status/", json=status_data, headers=headers)
    if response.status_code == 200:
        print("Application approved.")
    else:
        print(f"Failed to approve: {response.text}")

if __name__ == "__main__":
    test_admin_flow()
    test_core_flow()
