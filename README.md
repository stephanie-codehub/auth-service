# Auth Service API
    
## Overview
An asynchronous auth service API.


## Tech Stack
* **Language:** Python 3.12+
* **API:** FastAPI, Pydantic v2, Alembic, SQLAlchemy v2, Uvicorn
* **Data Layer:** PostgreSQL 
* **Observability**: Structlog 
* **Tests**: Pytest
* **DevOps:** Docker, Docker-Compose, GitHub Actions


---

## Key Modules & Endpoints
*   **Authentication:** 
    * **POST /auth/register** — Registers a new  user account.
    * **POST /auth/login** — Verifies user credentials and returns a JWT Access Token and HTTP-Only Refresh Token cookie.
    * **POST /auth/token/refresh** — Validates the Refresh Token cookie to reissue a short-lived JWT Access Token.
    * **POST /auth/logout** — Invalidates the Refresh Token.
    * **POST /auth/forgot-password** — Initiates the password reset process.
    * **POST /auth/reset-password** — Completes the password reset process.
    

*   **User Management:** Manages the profile details for the currently logged-in user.
    * **GET /users/profile** — Fetches the profile details
    * **PATCH /users/profile** — Updates the profile details
    * **POST /users/profile/change-password** — Changes the password
    
*   **Administrative:** Administrative actions reserved for users with ADMIN roles.
    * **GET /admin/users** — Fetches a paginated set of all user profiles.
    * **GET /admin/users/{user_id}** — Fetches any user's profile details by ID.
    * **GET /audit-logs** — Fetches a paginated set of all audit logs.
    * **GET /audit-logs/{audit_log_id}** — Fetches any audit log by ID.

*   **Request/Response Middleware:**
    * CORS & Trusted Hosts
    * Rate Limiter
    * Requests Logger: Tracks request ID, latency, status code and errors.
    * Audit Logger: Logs sensitive application state to the database.
    
*   **Access Control Management :** 
    * Role Based Access Control: Restricts resource to specific user roles
    * IDOR checks: Restricts resource retrieval to the owner of the resource exclusive of ADMINs


## Quick Start (Local Deployment)

### Prerequisites
* Docker and Docker-Compose installed.

### Running the System
1. Clone the repository and navigate to the folder:
   ```bash
   git clone https://github.com/stephanie-codehub/auth-service 
   cd auth-service
   ```

2. Rename the `.env.example` file in the root directory to `.env` and populate with your values
   ```bash
   cp .env.example .env
   ```

3. Start the API and PostgreSQL database:
   ```bash
   docker-compose up --build -d
   ```

4. Access API Docs (Swagger) at `http://localhost:8000/docs`

---

## Tests
Run the test suite via:
```bash
docker-compose exec pytest 
```