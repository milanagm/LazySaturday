# Authentication Flow

Endpoints under `/api/auth` power the interactive user login cycle.

## Register

- **POST** `/api/auth/register`
- **Body**

```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}
```

- **Response**

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 900
}
```

The response immediately signs the user in after registration. Passwords are hashed with Argon2 before storage.

## Login

- **POST** `/api/auth/login`
- **Body**

```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}
```

- **Response** identical to register.

## Current Profile

- **GET** `/api/auth/me`
- **Headers**: `Authorization: Bearer <jwt>`

- **Response**

```json
{
  "id": "f83408c1-5a47-4fc0-af4c-7f1b5cb9cb59",
  "email": "newuser@example.com",
  "is_verified": false
}
```

## Token Usage

Include the `Authorization` header for all endpoints that operate on user data (`/user/preferences`, `/plans/*`). Tokens expire after 15 minutes; re-login (or later, refresh tokens) to renew access.

## Environment

| Variable | Purpose | Default |
|----------|---------|---------|
| `DIET_DATABASE_URL` | SQLAlchemy DSN | `postgresql+psycopg://dp:dp@localhost:5432/dietplanner` |
| `DIET_JWT_SECRET_KEY` | JWT signing secret | `change-me` |
| `DIET_ACCESS_TOKEN_EXPIRES_MINUTES` | Access token TTL | `15` |

## Frontend integration

- Landing page “Start Your Cultural Plan” sends unauthenticated visitors to `/auth?redirect=/preferences`.
- Authenticated users open `/preferences` directly where their stored profile auto-populates the form.
- Tokens persist in the browser's storage and attach to subsequent API requests via the shared API client.
