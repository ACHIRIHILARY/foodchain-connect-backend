# API & Backend Development Guide

This document outlines the API endpoints, data models, and backend logic for the FoodChain Connect application. This guide serves as a comprehensive blueprint for backend developers implementing the server-side logic, ideally using a service like Firebase Firestore and Authentication.

## 1. Data Models

These are the core data structures for the application.

### 1.1. User

Represents a user of the platform. This document would be stored in a `/users` collection in Firestore.

| Field | Type | Description | Notes |
| :--- | :--- | :--- | :--- |
| **`id`** | `string` | Unique identifier from Firebase Authentication (UID). | Primary key. |
| **`name`** | `string` | User's full name or organization name. | Required. |
| **`email`** | `string` | User's unique email address. | Required, used for login. |
| **`role`** | `string` | `'Donor'`, `'Receiver'`, `'Admin'`, `'Main Admin'` | Determines user permissions. |
| **`phone`** | `string` | User's contact phone number. | Required for coordination. |
| **`address`** | `string` | User's physical address for pickup/location context. | Optional. |
| **`isVerified`**| `boolean`| Flag to indicate if the user is trusted. | Default `false`. Can only be changed by Admins. |
| **`subscriptionStatus`** | `string` | `'Basic'`, `'Pro'` | Determines access to premium features. Default `'Basic'`. |
| **`createdAt`**| `Timestamp`| Server-side timestamp of when the user was created. | For auditing and records. |

### 1.2. Donation

Represents a food donation. This document would be stored in a `/donations` collection in Firestore.

| Field | Type | Description | Notes |
| :--- | :--- | :--- | :--- |
| **`id`** | `string` | Unique identifier for the donation (Firestore Auto-ID). | Primary key. |
| **`foodName`** | `string` | Name of the food item. | Required. |
| **`quantity`** | `string` | Description of the quantity (e.g., "15 loaves"). | Required. |
| **`category`** | `string` | `'Produce'`, `'Baked Goods'`, `'Dairy'`, etc. | For filtering and sorting. |
| **`bestBeforeDate`**| `Timestamp`| The best-before date for the food item. | Required. |
| **`status`** | `string` | `'Available'`, `'Claimed'`, `'PickedUp'`, `'Expired'`| Manages the donation lifecycle. Default `'Available'`. |
| **`donorInfo`** | `object` | Embedded object with information about the donor. |
| `id` | `string` | The donor's user ID (references `/users/{userId}`). | Required. |
| `name` | `string` | The name of the donating person or organization. | Denormalized for quick display. |
| **`claimedByInfo`**| `object` | Information about the user who claimed the donation. | Optional. Present when `status` is 'Claimed' or 'PickedUp'. |
| `id` | `string` | The receiver's user ID (references `/users/{userId}`). | |
| `name` | `string` | The name of the receiving person or organization. | Denormalized for quick display. |
| **`imageUrl`** | `string` | URL for a photo of the donation. | Stored in a service like Firebase Storage. |
| **`imageHint`**| `string` | AI-powered image search keywords. | e.g., "baked goods" |
| **`location`** | `GeoPoint`| Geolocation for map view. | Optional, for proximity searches. |
| **`createdAt`**| `Timestamp`| Server-side timestamp of when the donation was posted. | For sorting by newness. |
| **`updatedAt`**| `Timestamp`| Server-side timestamp for the last update. | For tracking changes. |

### 1.3. PlatformSettings

Represents global settings for the application. This could be a single document in a `/settings` collection (e.g., `/settings/platform`).

| Field | Type | Description | Notes |
| :--- | :--- | :--- | :--- |
| **`proPlanPrice`** | `number` | The monthly price for the 'Pro' subscription. | e.g., 10.00 |

---

## 2. API Endpoints

These endpoints define the contract between the frontend and backend. All requests should be authenticated unless specified otherwise.

### 2.1. Authentication (`/api/auth`)

- **`POST /api/auth/signup`**: Create a new user account.
  - **Logic**: Creates a new user with Firebase Auth, then creates a corresponding user document in the `/users` collection in Firestore.
  - **Request Body**:
    ```json
    {
      "firstName": "Jane",
      "lastName": "Doe",
      "email": "jane.doe@example.com",
      "password": "strongpassword123",
      "role": "Donor" // or "Receiver"
    }
    ```
  - **Response (Success `201`)**:
    ```json
    {
      "user": { /* User object from Firestore */ },
      "token": "FIREBASE_AUTH_JWT"
    }
    ```
  - **Response (Error `400`)**: If email is already in use or validation fails.

- **`POST /api/auth/login`**: Log in a user.
  - **Logic**: Authenticates user with Firebase Auth using email and password. Returns the JWT and user profile.
  - **Request Body**:
    ```json
    {
      "email": "jane.doe@example.com",
      "password": "strongpassword123"
    }
    ```
  - **Response (Success `200`)**:
    ```json
    {
      "user": { /* User object from Firestore */ },
      "token": "FIREBASE_AUTH_JWT"
    }
    ```
  - **Response (Error `401`)**: If credentials are invalid.

- **`POST /api/auth/logout`**: Log out a user.
  - **Logic**: Invalidates the user's session on the server-side if necessary (clears cookie). Client-side will clear the token.
  - **Response (Success `200`)**: `{ "message": "Logout successful" }`

- **`GET /api/auth/session`**: Get the current authenticated user's session from the auth token (cookie/header).
  - **Logic**: Verifies the JWT and fetches the user document from Firestore.
  - **Response (Success `200`)**: `{ "user": { /* User object */ } }`
  - **Response (No Session `200`)**: `{ "user": null }`

### 2.2. Users (`/api/users`)

- **`GET /api/users`**: Get a list of all users.
  - **Auth**: `Admin` or `Main Admin` only.
  - **Logic**: Fetches all documents from the `/users` collection. Implement pagination for performance.
  - **Response (Success `200`)**: `User[]` (Array of user objects).

- **`GET /api/users/{userId}`**: Get a single user's public profile.
  - **Auth**: Any authenticated user.
  - **Logic**: Fetches a specific user document. Can be used to view donor profiles.
  - **Response (Success `200`)**: `User` object.
  - **Response (Error `404`)**: If user not found.

- **`PUT /api/users/{userId}`**: Update a user's own profile information.
  - **Auth**: Authenticated user (must match `{userId}`).
  - **Logic**: Updates fields on the user document. The `role`, `isVerified`, and `subscriptionStatus` fields cannot be changed here.
  - **Request Body**:
    ```json
    {
      "name": "Jane Doe Smith",
      "phone": "555-111-2222",
      "address": "124 Main St, Anytown, USA"
    }
    ```
  - **Response (Success `200`)**: Updated `User` object.

### 2.3. Donations (`/api/donations`)

- **`GET /api/donations`**: Get a list of donations.
  - **Auth**: Any authenticated user.
  - **Logic**: Fetches donations from the `/donations` collection. Can be filtered by status, category, or donor ID.
  - **Query Params**:
    - `?status=Available` (filters by status)
    - `?donorId={id}` (gets donations for a specific donor)
  - **Response (Success `200`)**: `Donation[]`

- **`POST /api/donations`**: Create a new donation listing.
  - **Auth**: `Donor` role only.
  - **Logic**: Creates a new document in the `/donations` collection. `donorInfo` is populated from the authenticated user's data.
  - **Request Body**:
    ```json
    {
      "foodName": "Croissants",
      "quantity": "2 dozen",
      "category": "Baked Goods",
      "bestBeforeDate": "2024-10-28T10:00:00Z",
      "imageUrl": "https://path/to/image.jpg"
    }
    ```
  - **Response (Success `201`)**: The newly created `Donation` object.

- **`PUT /api/donations/{donationId}`**: Update a donation.
  - **Auth**: The `Donor` who owns the donation, or any `Admin`/`Main Admin`.
  - **Logic**: Updates fields on a donation document. A donor cannot change the `status` to anything other than `Available`.
  - **Request Body**: Partial `Donation` object.
  - **Response (Success `200`)**: The updated `Donation` object.

- **`DELETE /api/donations/{donationId}`**: Delete a donation.
  - **Auth**: The `Donor` who owns the donation, or any `Admin`/`Main Admin`.
  - **Logic**: Deletes the donation document from Firestore.
  - **Response (Success `204`)**: No content.

- **`POST /api/donations/{donationId}/claim`**: Claim an available donation.
  - **Auth**: `Receiver` role only.
  - **Logic**: Updates the donation's `status` to `'Claimed'` and populates the `claimedByInfo` object with the authenticated receiver's data. This action should fail if the donation `status` is not `'Available'`.
  - **Response (Success `200`)**: The updated `Donation` object.

### 2.4. Admin (`/api/admin`)

- **`POST /api/admin/users`**: Create a new user (e.g., an Admin creating another Admin).
    - **Auth**: `Main Admin` only.
    - **Logic**: Creates a user in Firebase Auth and a user document in Firestore. Useful for creating other Admin accounts.
    - **Request Body**: Similar to signup, but with explicit role assignment.
      ```json
      {
        "name": "New Admin",
        "email": "new.admin@example.com",
        "password": "strongpassword123",
        "role": "Admin"
      }
      ```
    - **Response (Success `201`)**: The newly created `User` object.

- **`PUT /api/admin/users/{userId}/verification`**: Toggles a user's verification status.
  - **Auth**: `Admin` or `Main Admin` only.
  - **Logic**: Sets the `isVerified` flag on a user's document.
  - **Request Body**: `{ "isVerified": true }`
  - **Response (Success `200`)**: Updated `User` object.

- **`PUT /api/admin/users/{userId}/subscription`**: Change a user's subscription plan.
  - **Auth**: `Admin` or `Main Admin` only.
  - **Logic**: Updates the `subscriptionStatus` field on a user's document.
  - **Request Body**: `{ "subscriptionStatus": "Pro" }`
  - **Response (Success `200`)**: Updated `User` object.

- **`DELETE /api/admin/users/{userId}`**: Delete a user account.
  - **Auth**:
    - `Main Admin` can delete any user (except themselves).
    - `Admin` can delete `Donor` or `Receiver` roles, but not other `Admin` or `Main Admin` roles.
  - **Logic**: Deletes the user from Firebase Auth and then deletes their document from the `/users` collection in Firestore. This should be a cascading delete if possible (e.g., anonymize their donations).
  - **Response (Success `204`)**: No content.
  - **Response (Error `403`)**: Forbidden, if an Admin tries to delete another Admin or a Main Admin.

- **`PUT /api/admin/settings`**: Update global platform settings.
  - **Auth**: `Main Admin` only.
  - **Logic**: Updates the singleton document in the `/settings` collection.
  - **Request Body**:
    ```json
    {
      "proPlanPrice": 12.00
    }
    ```
  - **Response (Success `200`)**: The updated `PlatformSettings` object.

### 2.5. Dashboard (`/api/dashboard`)

- **`GET /api/dashboard/stats`**: Get aggregated statistics for the current user's dashboard.
  - **Auth**: Any authenticated user.
  - **Logic**:
    - **For Donors**: Counts their total donations, active donations, and number of claims on their items this month.
    - **For Receivers**: Counts their total claims and active claims.
  - **Response (Success `200`)**:
    ```json
    {
      "activeDonations": 3,
      "totalDonations": 125,
      "claimsThisMonth": 92
    }
    ```

## 3. High-Level Firestore Security Rules

This is a conceptual outline. The actual rules would be implemented in `firestore.rules`.

- **`/users/{userId}`**:
  - `read`: Any authenticated user can read public profiles. A user can read their own full document. Admins can read all fields of any user.
  - `write`: A user can only write to their own document (`request.auth.uid == userId`) for non-privileged fields.
  - `create`: Any user can create their own user document during signup.
  - Privileged fields like `role`, `isVerified`, and `subscriptionStatus` can only be changed by an Admin or Main Admin (with specific logic for role changes being `Main Admin` only).

- **`/donations/{donationId}`**:
  - `read`: Any authenticated user can read all donations.
  - `create`: Only users with `role == 'Donor'` can create. The `donorInfo.id` must match the creator's UID (`request.auth.uid`).
  - `update`:
    - The original donor can update their own donation if the status is `Available`.
    - A user with `role == 'Receiver'` can update a donation to set the `status` to `'Claimed'` and add their `claimedByInfo`.
    - `Admin` or `Main Admin` can update any field on any donation.
  - `delete`: The original donor can delete their own donation. `Admin` or `M` can delete any donation.

- **`/settings/platform`**:
  - `read`: Any authenticated user can read the settings (e.g., to see the Pro price).
  - `write`: Only users with the custom claim `role == 'Main Admin'` can write.
```