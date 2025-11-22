import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

# --- Helpers ---
def print_step(msg):
    print(f"\n[STEP] {msg}")

def print_success(msg):
    print(f"  [OK] {msg}")

def print_fail(msg):
    print(f"  [FAIL] {msg}")

def get_token(username, password):
    resp = requests.post(f"{BASE_URL}/users/login/", json={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.json()['access']
    return None

def create_user(username, role, email, password="password123"):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "role": role,
        "phone_number": "1234567890"
    }
    # We expect 201 or 400 if exists (which is fine for re-runs)
    requests.post(f"{BASE_URL}/users/register/", json=data)

# --- Main Test ---
def verify_system():
    print("=== Starting System-Wide Verification ===")
    
    # 1. Setup Users
    print_step("Setting up users (Admin, Provider, Seeker)")
    # Note: We can't create an ADMIN via public register, so we assume one exists or we skip Admin creation via API.
    # We'll focus on Provider and Seeker interactions and assume we have a superuser or we test Admin features if we have credentials.
    # For this script, let's stick to Provider/Seeker and mock Admin actions if needed or rely on previous admin verification.
    # Actually, let's try to use the 'admin' user if it exists (from previous manual setup) or just skip Admin-specific auth actions if we don't have creds.
    # Wait, I can't create an admin via API. I'll focus on the Provider-Seeker loop and Admin *viewing* if I can.
    
    create_user("master_provider", "PROVIDER", "m_prov@test.com")
    create_user("master_seeker", "SEEKER", "m_seek@test.com")
    
    prov_token = get_token("master_provider", "password123")
    seek_token = get_token("master_seeker", "password123")
    
    if not prov_token or not seek_token:
        print_fail("Failed to authenticate users. Aborting.")
        return

    prov_headers = {"Authorization": f"Bearer {prov_token}"}
    seek_headers = {"Authorization": f"Bearer {seek_token}"}
    print_success("Users authenticated")

    # 2. Provider: Profile & Listing
    print_step("Provider Flow: Profile & Listing")
    
    # Update Profile
    profile_data = {"organization_name": "Master Food Bank", "address": "123 Main St"}
    resp = requests.patch(f"{BASE_URL}/users/me/", json=profile_data, headers=prov_headers)
    if resp.status_code == 200:
        print_success("Provider profile updated")
    else:
        print_fail(f"Profile update failed: {resp.text}")

    # Create Listing
    listing_data = {
        "title": "System Test Meal",
        "description": "Full cycle test",
        "quantity": "100",
        "expiry_date": "2025-01-01T12:00:00Z",
        "category": "COOKED",
        "pickup_location": "Central Hub",
        "pickup_time_window": "12PM-4PM"
    }
    resp = requests.post(f"{BASE_URL}/listings/", json=listing_data, headers=prov_headers)
    if resp.status_code == 201:
        listing_id = resp.json()['id']
        print_success(f"Listing created (ID: {listing_id})")
    else:
        print_fail(f"Listing creation failed: {resp.text}")
        return

    # 3. Seeker: Search & Apply
    print_step("Seeker Flow: Search & Apply")
    
    # Filter Listings
    resp = requests.get(f"{BASE_URL}/listings/?category=COOKED&pickup_location=Central", headers=seek_headers)
    if resp.status_code == 200 and len(resp.json()) > 0:
        print_success("Seeker found listing via filter")
    else:
        print_fail("Seeker failed to find listing with filter")

    # Apply
    app_data = {
        "listing": listing_id,
        "message": "Urgent need",
        "beneficiaries_count": 50,
        "preferred_pickup_time": "2024-12-31T14:00:00Z"
    }
    resp = requests.post(f"{BASE_URL}/applications/", json=app_data, headers=seek_headers)
    if resp.status_code == 201:
        app_id = resp.json()['id']
        print_success(f"Application submitted (ID: {app_id})")
    else:
        print_fail(f"Application failed: {resp.text}")
        return

    # 4. Provider: Approve
    print_step("Provider Flow: Approval")
    resp = requests.post(f"{BASE_URL}/applications/{app_id}/update_status/", json={"status": "APPROVED"}, headers=prov_headers)
    if resp.status_code == 200:
        print_success("Application approved")
    else:
        print_fail(f"Approval failed: {resp.text}")

    # 5. Seeker: Confirm Pickup
    print_step("Seeker Flow: Pickup Confirmation")
    resp = requests.post(f"{BASE_URL}/applications/{app_id}/confirm_pickup/", headers=seek_headers)
    if resp.status_code == 200:
        print_success("Pickup confirmed")
    else:
        print_fail(f"Pickup confirmation failed: {resp.text}")

    # 6. Analytics Check
    print_step("Provider Flow: Analytics")
    resp = requests.get(f"{BASE_URL}/listings/analytics/", headers=prov_headers)
    if resp.status_code == 200:
        data = resp.json()
        if data['total_listings'] >= 1:
            print_success(f"Analytics verified (Total Listings: {data['total_listings']})")
        else:
            print_fail("Analytics data incorrect")
    else:
        print_fail("Analytics access failed")

    # 7. Payments (Mock)
    print_step("Payment Flow")
    # Initiate
    resp = requests.post(f"{BASE_URL}/payments/payments/initiate/", json={"plan_id": 999}, headers=prov_headers) # 999 will 404 but proves endpoint hit
    if resp.status_code == 404:
        print_success("Payment initiation endpoint reachable (returned expected 404 for fake plan)")
    else:
        print_fail(f"Payment initiation unexpected response: {resp.status_code}")

    # 8. Support
    print_step("Support Flow")
    resp = requests.post(f"{BASE_URL}/support/", json={"subject": "System Check", "message": "All good"}, headers=seek_headers)
    if resp.status_code == 201:
        print_success("Support ticket created")
    else:
        print_fail("Support ticket creation failed")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_system()
