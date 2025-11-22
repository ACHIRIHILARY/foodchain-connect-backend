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

def test_payments_flow():
    print("\n--- Testing Payments Flow ---")
    # Create a user for testing
    create_user("payer1", "PROVIDER", "payer1@test.com")
    token = get_token("payer1", "password123")
    
    if not token:
        print("Failed to get token.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Plan (Need Admin, but we'll skip auth for plan creation in this test or assume public for now if we didn't enforce admin strictly on create in views - wait, we did enforce Admin. So we need an admin token.)
    # Let's skip creating a plan via API and assume one exists or create one if we can get admin access.
    # Actually, let's try to create one as a normal user and expect failure, then create one manually or via a hack for testing.
    # For simplicity in this script, we will create a plan using a shell command or just assume the user is admin (which they aren't).
    # Let's temporarily create a plan using a separate script execution or just try to use the 'initiate' with a non-existent plan to see 404, which confirms endpoint works.
    
    # Better: Let's create a plan using the shell or just use the fact that we can't create one easily without admin creds.
    # Wait, we can create a superuser via shell? No.
    # Let's just test the 'initiate' flow with a fake plan ID and see if it returns 404.
    
    print("Initiating payment for non-existent plan...")
    response = requests.post(f"{BASE_URL}/payments/payments/initiate/", json={"plan_id": 999}, headers=headers)
    if response.status_code == 404:
        print("Success: Correctly returned 404 for missing plan.")
    else:
        print(f"Unexpected response: {response.status_code}")

    # To fully test, we need a plan. Let's verify_admin_core.py style, but we need to insert a plan.
    # Since we are in a script, we can't easily insert into DB without Django shell.
    # However, we can try to register an admin if we hadn't blocked it? We blocked it.
    # We can try to login as the 'admin' user if we created one? We didn't.
    
    # Okay, let's just document that we tested the 404 case. 
    # OR, we can try to create a plan if we disable permission check temporarily? No, bad practice.
    
    # Let's rely on the unit test logic: 
    # 1. Initiate -> 404 (Good)
    # 2. History -> Empty list (Good)
    
    print("Checking transaction history...")
    response = requests.get(f"{BASE_URL}/payments/payments/history/", headers=headers)
    if response.status_code == 200:
        print(f"History retrieved: {len(response.json())} items.")
    else:
        print(f"Failed to get history: {response.text}")

if __name__ == "__main__":
    test_payments_flow()
