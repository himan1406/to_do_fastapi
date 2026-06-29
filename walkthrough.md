# Walkthrough - User Authentication and Todo Multi-Tenancy

We have successfully implemented user authentication and isolated todo tasks so that each registered user can only access their own todos.

## Changes Made

### 1. Database Schema Migration
* Added `User` database model in [models.py](file:///c:/Users/himan/to-do-fastapi/models.py).
* Added `user_id` foreign key column (referencing `users.id` with cascade deletion) to the `Todo` model.
* Generated and applied a database migration script [5f0498e2d7ee_add_users_table.py](file:///c:/Users/himan/to-do-fastapi/alembic/versions/5f0498e2d7ee_add_users_table.py) using Alembic, including removing the unique constraint on the todo `title` to allow different users to have todos with the same title.

### 2. Backend Security & Hashing
* Implemented [auth_utils.py](file:///c:/Users/himan/to-do-fastapi/auth_utils.py) using `bcrypt` for secure, salted password hashing and validation. Bcrypt automatically generates a unique cryptographic salt for each password and embeds it inside the stored hash string.
* Wired up JWT token signing and decoding helper functions using `pyjwt`.
* Created authentication check dependency `get_current_user` in [routers/deps.py](file:///c:/Users/himan/to-do-fastapi/routers/deps.py) to authenticate incoming API requests via Bearer token in the `Authorization` header.

### 3. API Routers
* Created [routers/auth.py](file:///c:/Users/himan/to-do-fastapi/routers/auth.py) defining:
  - `POST /auth/signup` for registration (requires name, email, phone number, password).
  - `POST /auth/login` returning a JWT access token.
  - `POST /auth/forgot-password` to securely reset a password if the user provides matching email and phone details.
* Updated [routers/todo.py](file:///c:/Users/himan/to-do-fastapi/routers/todo.py) to secure todos by enforcing authorization checks. Every operation (create, read, update, delete) is restricted and isolated using the authenticated `current_user.id`.

### 4. Frontend Integration
* **Signup & Login Forms**: Wired [static/js/signup.js](file:///c:/Users/himan/to-do-fastapi/static/js/signup.js) and [static/js/login.js](file:///c:/Users/himan/to-do-fastapi/static/js/login.js) to send payload data to the new backend auth endpoints, store the JWT in `localStorage`, and redirect pages accordingly.
* **Forgot Password Page**: Added [static/forgot.html](file:///c:/Users/himan/to-do-fastapi/static/forgot.html), [static/css/forgot.css](file:///c:/Users/himan/to-do-fastapi/static/css/forgot.css), and [static/js/forgot.js](file:///c:/Users/himan/to-do-fastapi/static/js/forgot.js) to allow users to reset their password safely.
* **Dashboard Isolation**: Updated [static/js/dashboard.js](file:///c:/Users/himan/to-do-fastapi/static/js/dashboard.js) to enforce token existence upon load, add Bearer headers to all API fetch calls, handle auth failure (by redirecting to login page), and clear token storage on logout.

## Verification

The Docker containers (`db` and `app`) are built and running. The complete user registration flow, login flow, forgot-password reset flow, and todo list multi-tenancy are fully operational.
