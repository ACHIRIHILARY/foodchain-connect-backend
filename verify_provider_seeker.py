import requests
import json

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

def test_features():
    print("\n--- Testing Provider & Seeker Features ---")
    
    # Setup Users
    create_user("provider_feat", "PROVIDER", "prov_feat@test.com")
    create_user("seeker_feat", "SEEKER", "seek_feat@test.com")
    
    prov_token = get_token("provider_feat", "password123")
    seek_token = get_token("seeker_feat", "password123")
    
    prov_headers = {"Authorization": f"Bearer {prov_token}"}
    seek_headers = {"Authorization": f"Bearer {seek_token}"}

    # 1. Provider: Create Listing with new fields
    print("Provider creating listing...")
    listing_data = {
        "title": "Detailed Listing",
        "description": "With category and pickup",
        "quantity": "50",
        "expiry_date": "2024-12-31T12:00:00Z",
        "category": "COOKED",
        "pickup_location": "Main St",
        "pickup_time_window": "10AM-2PM"
    }
    resp = requests.post(f"{BASE_URL}/listings/", json=listing_data, headers=prov_headers)
    if resp.status_code == 201:
        listing_id = resp.json()['id']
        print(f"Listing created: ID {listing_id}")
    else:
        print(f"Failed to create listing: {resp.text}")
        return

    # 2. Provider: Analytics
    print("Provider checking analytics...")
    resp = requests.get(f"{BASE_URL}/listings/analytics/", headers=prov_headers)
    if resp.status_code == 200:
        print(f"Analytics: {resp.json()}")
    else:
        print(f"Failed to get analytics: {resp.text}")

    # 3. Seeker: Apply with details
    print("Seeker applying...")
    app_data = {
        "listing": listing_id,
        "message": "Need for 10 people",
        "beneficiaries_count": 10,
        "preferred_pickup_time": "2024-12-30T10:00:00Z"
    }
    resp = requests.post(f"{BASE_URL}/applications/", json=app_data, headers=seek_headers)
    if resp.status_code == 201:
        app_id = resp.json()['id']
        print(f"Application created: ID {app_id}")
    else:
        print(f"Failed to apply: {resp.text}")
        return

    # 4. Provider: Approve Application
    print("Provider approving...")
    resp = requests.post(f"{BASE_URL}/applications/{app_id}/update_status/", json={"status": "APPROVED"}, headers=prov_headers)
    if resp.status_code == 200:
        print("Application approved.")
    else:
        print(f"Failed to approve: {resp.text}")

    # 5. Seeker: Confirm Pickup
    print("Seeker confirming pickup...")
    resp = requests.post(f"{BASE_URL}/applications/{app_id}/confirm_pickup/", headers=seek_headers)
    if resp.status_code == 200:
        print("Pickup confirmed.")
    else:
        print(f"Failed to confirm pickup: {resp.text}")

    # 6. Support Ticket
    print("Creating support ticket...")
    resp = requests.post(f"{BASE_URL}/support/", json={"subject": "Test", "message": "Help"}, headers=seek_headers)
    if resp.status_code == 201:
        print("Support ticket created.")

if __name__ == "__main__":
    test_features()
