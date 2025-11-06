# FoodChain Connect Backend

A Django REST API backend for the FoodChain Connect food donation platform.

## Features

- **User Authentication & Authorization**: JWT-based authentication with role-based permissions
- **Donation Management**: Complete CRUD operations for food donations
- **User Roles**: Donor, Receiver, Admin, and Main Admin roles with appropriate permissions
- **Image Upload**: Support for donation photos
- **Real-time Dashboard**: Statistics and analytics for users
- **Admin Panel**: Administrative controls for user and platform management
- **CORS Support**: Configured for frontend integration

## Tech Stack

- **Django 5.2.8**: Web framework
- **Django REST Framework**: API framework
- **JWT Authentication**: Token-based authentication
- **PostgreSQL/SQLite**: Database support
- **Pillow**: Image processing
- **CORS Headers**: Cross-origin resource sharing

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd foodchain-connect-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication

- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/session/` - Get current session
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users

- `GET /api/users/` - List all users (Admin only)
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/profile/` - Update own profile

### Donations

- `GET /api/donations/` - List donations with filtering
- `POST /api/donations/` - Create new donation (Donor only)
- `GET /api/donations/{id}/` - Get donation details
- `PUT /api/donations/{id}/` - Update donation (Owner/Admin only)
- `DELETE /api/donations/{id}/` - Delete donation (Owner/Admin only)
- `POST /api/donations/{id}/claim/` - Claim donation (Receiver only)

### Admin

- `POST /api/admin/users/` - Create user (Main Admin only)
- `PATCH /api/admin/users/{id}/verification/` - Toggle user verification
- `PATCH /api/admin/users/{id}/subscription/` - Change subscription status
- `DELETE /api/admin/users/{id}/` - Delete user
- `GET /api/admin/settings/` - Get platform settings
- `PUT /api/admin/settings/` - Update platform settings

### Dashboard

- `GET /api/dashboard/stats/` - Get user dashboard statistics

## User Roles & Permissions

### Donor
- Create and manage their own donations
- View all donations
- Update their profile

### Receiver
- View all donations
- Claim available donations
- View their claimed donations

### Admin
- All Donor and Receiver permissions
- View all users
- Verify/unverify users
- Change user subscription status
- Delete Donor/Receiver accounts

### Main Admin
- All Admin permissions
- Create new users (including Admins)
- Delete any user account (except themselves)
- Modify platform settings

## Data Models

### User
- `id`: Unique identifier
- `name`: Full name
- `email`: Email address (used for login)
- `role`: User role (Donor/Receiver/Admin/Main Admin)
- `phone`: Phone number
- `address`: Physical address
- `is_verified`: Verification status
- `subscription_status`: Basic/Pro subscription
- `created_at`: Registration timestamp

### Donation
- `id`: Unique identifier
- `food_name`: Name of food item
- `quantity`: Quantity description
- `category`: Food category
- `best_before_date`: Expiration date
- `status`: Available/Claimed/PickedUp/Expired
- `donor`: Reference to donor user
- `claimed_by`: Reference to receiver user (if claimed)
- `image`: Donation photo
- `image_hint`: AI search keywords
- `location_lat/lng`: Geolocation coordinates
- `created_at/updated_at`: Timestamps

## Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3  # or PostgreSQL URL
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Testing the API

### Using curl

**Register a new user:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "role": "Donor"
  }'
```

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Create a donation (include JWT token):**
```bash
curl -X POST http://127.0.0.1:8000/api/donations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "food_name": "Bread Loaves",
    "quantity": "5 loaves",
    "category": "Baked Goods",
    "best_before_date": "2025-12-01T10:00:00Z"
  }'
```

## Deployment

### Production Settings

1. Set `DEBUG=False`
2. Configure production database (PostgreSQL recommended)
3. Set secure `SECRET_KEY`
4. Configure static/media file serving
5. Set up proper CORS origins
6. Use production WSGI/ASGI server (Gunicorn/Uvicorn)

### Docker Support

Add a `Dockerfile` and `docker-compose.yml` for containerized deployment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
