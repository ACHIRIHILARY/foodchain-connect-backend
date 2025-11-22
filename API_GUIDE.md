# Food Connect API Guide

Base URL: `http://localhost:8000/api`

## Authentication

The API uses JWT (JSON Web Token) for authentication.
- Include the access token in the `Authorization` header for protected endpoints.
- Format: `Authorization: Bearer <your_access_token>`

---

## Endpoints

### 1. User Registration & Profile

Create a new user account.

- **URL**: `/users/register/`
- **Method**: `POST`
- **Auth Required**: No

**Request Body (JSON):**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "SEEKER",  // Options: "SEEKER", "PROVIDER" (ADMIN is restricted)
  "phone_number": "1234567890", // Optional
  "address": "123 Green St, City", // Optional
  "organization_name": "Food Bank", // Optional (Provider/Seeker)
  "verification_document": "(file upload)" // Optional
}
```

- **URL**: `/users/me/`
- **Method**: `GET`, `PUT`, `PATCH`
- **Auth Required**: Yes

---

### 2. Food Listings

Manage food donations.

- **URL**: `/listings/`
- **Method**: `GET`
    - **Seekers**: View all `AVAILABLE` listings. Filter by `category`, `pickup_location`.
    - **Providers**: View their own listings.
    - **Admins**: View all listings.
- **Method**: `POST` (Providers only)

**Create Listing Payload:**

```json
{
  "title": "Fresh Bread",
  "description": "10 loaves of bread",
  "quantity": "10",
  "expiry_date": "2023-12-31T23:59:59Z",
  "category": "PACKAGED", // COOKED, PACKAGED, FRESH, OTHER
  "pickup_location": "123 Baker St",
  "pickup_time_window": "9AM - 5PM",
  "image": "(file upload)" // Optional
}
```

- **URL**: `/listings/{id}/`
- **Method**: `GET`, `PUT`, `PATCH`, `DELETE` (Provider/Admin)

- **URL**: `/listings/analytics/`
- **Method**: `GET` (Provider only)
    - Returns stats: `total_listings`, `active_listings`, `impact_score`.

---

### 3. Food Applications

Manage requests for food.

- **URL**: `/applications/`
- **Method**: `GET`
    - **Seekers**: View their applications.
    - **Providers**: View applications for their listings.
    - **Admins**: View all.
- **Method**: `POST` (Seekers only)

**Create Application Payload:**

```json
{
  "listing": 1, // ID of the listing
  "message": "We need this for our shelter.",
  "beneficiaries_count": 50,
  "preferred_pickup_time": "2023-12-30T10:00:00Z"
}
```

- **URL**: `/applications/{id}/update_status/`
- **Method**: `POST` (Provider/Admin)

**Update Status Payload:**

```json
{
  "status": "APPROVED" // Options: "APPROVED", "REJECTED"
}
```

- **URL**: `/applications/{id}/confirm_pickup/`
- **Method**: `POST` (Seeker only)
    - Confirms pickup for an `APPROVED` application. Sets status to `COLLECTED`.

---

### 4. Notifications

- **URL**: `/notifications/`
- **Method**: `GET` (List own notifications)

- **URL**: `/notifications/{id}/mark_read/`
- **Method**: `POST`

---

### 5. Support Tickets

- **URL**: `/support/`
- **Method**: `GET` (List own tickets)
- **Method**: `POST` (Create ticket)

**Create Ticket Payload:**

```json
{
  "subject": "Issue with pickup",
  "message": "The provider was not available."
}
```

---

### 6. Payments & Subscriptions

Manage plans and payments.

#### Subscription Plans
- **URL**: `/payments/plans/`
- **Method**: `GET` (Public)
- **Method**: `POST` (Admin Only)

#### Initiate Payment
- **URL**: `/payments/payments/initiate/`
- **Method**: `POST` (Authenticated)

**Payload:**

```json
{
  "plan_id": 1
}
```

#### Transaction History
- **URL**: `/payments/payments/history/`
- **Method**: `GET` (Authenticated)
