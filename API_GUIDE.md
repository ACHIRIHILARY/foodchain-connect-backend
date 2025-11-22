# Food Connect API Guide

Base URL: `http://localhost:8000/api`

## Authentication

The API uses JWT (JSON Web Token) for authentication.
- Include the access token in the `Authorization` header for protected endpoints.
- Format: `Authorization: Bearer <your_access_token>`

---

## Endpoints

### 1. User Registration

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
  "address": "123 Green St, City" // Optional
}
```

**Success Response (201 Created):**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "role": "SEEKER",
  "phone_number": "1234567890",
  "address": "123 Green St, City"
}
```

---

### 2. Login (Obtain Token)

Authenticate a user and receive access and refresh tokens.

- **URL**: `/users/login/`
- **Method**: `POST`
- **Auth Required**: No

**Request Body (JSON):**

```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 3. Refresh Token

Get a new access token using a valid refresh token.

- **URL**: `/users/token/refresh/`
- **Method**: `POST`
- **Auth Required**: No

**Request Body (JSON):**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 4. Get Current User Profile

Retrieve details of the currently logged-in user.

- **URL**: `/users/me/`
- **Method**: `GET`
- **Auth Required**: Yes

---

### 5. Admin User Management (Super Admin Only)

Manage all users in the system.

- **URL**: `/users/admin/users/`
- **Method**: `GET` (List), `POST` (Create)
- **Auth Required**: Yes (Admin)

- **URL**: `/users/admin/users/{id}/`
- **Method**: `GET`, `PUT`, `PATCH`, `DELETE`
- **Auth Required**: Yes (Admin)

**Create Admin User Payload:**

```json
{
  "username": "adminuser",
  "email": "admin@example.com",
  "password": "password",
  "role": "ADMIN"
}
```

---

### 6. Food Listings

Manage food donations.

- **URL**: `/listings/`
- **Method**: `GET`
    - **Seekers**: View all `AVAILABLE` listings.
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
  "image": "(file upload)" // Optional
}
```

- **URL**: `/listings/{id}/`
- **Method**: `GET`, `PUT`, `PATCH`, `DELETE` (Provider/Admin)

- **URL**: `/listings/{id}/approve/`
- **Method**: `POST` (Admin only)
    - Approves a listing and sets status to `AVAILABLE`.

---

### 7. Food Applications

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
  "message": "We need this for our shelter."
}
```

- **URL**: `/applications/{id}/update_status/`
- **Method**: `POST` (Provider/Admin)

**Update Status Payload:**

```json
{
  "status": "APPROVED" // Options: "APPROVED", "REJECTED", "COLLECTED"
}
```

---

### 8. Payments & Subscriptions

Manage plans and payments.

#### Subscription Plans
- **URL**: `/payments/plans/`
- **Method**: `GET` (Public)
- **Method**: `POST` (Admin Only)

**Create Plan Payload:**

```json
{
  "name": "Premium Plan",
  "description": "Unlimited access",
  "price": "9.99",
  "duration_days": 30,
  "features": {"priority": true, "analytics": true}
}
```

#### Initiate Payment
- **URL**: `/payments/payments/initiate/`
- **Method**: `POST` (Authenticated)

**Payload:**

```json
{
  "plan_id": 1
}
```

**Response:**

```json
{
  "transaction_id": 123,
  "payment_url": "http://localhost:8000/api/payments/mock_gateway/uuid-ref/",
  "message": "Payment initiated..."
}
```

#### Complete Payment (Mock Webhook)
- **URL**: `/payments/payments/webhook/`
- **Method**: `POST` (Public - simulate gateway callback)

**Payload:**

```json
{
  "provider_ref": "uuid-ref-from-initiate-response",
  "status": "SUCCESS"
}
```

#### Transaction History
- **URL**: `/payments/payments/history/`
- **Method**: `GET` (Authenticated)

## Notes for Frontend Developers

1.  **Roles**: Ensure the registration form allows users to select their role (Seeker or Provider). Admin role should probably not be exposed in the public registration form unless intended.
2.  **Token Management**: Store the `access` token securely (e.g., in memory or HttpOnly cookie) and the `refresh` token.
3.  **Token Expiry**: When the `access` token expires (401 Unauthorized), use the `refresh` token endpoint to get a new `access` token.
4.  **Error Handling**: API will return 400 Bad Request for validation errors (e.g., username already exists). Display these errors to the user.
5.  **Payments**: For the mock payment flow, redirect the user to the `payment_url` returned by the initiate endpoint. In a real app, this would be the Stripe checkout page.
