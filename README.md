# SkillBridge Backend API

Backend API for the SkillBridge prototype attendance management system.

## 1. Live API Base URL & Deployment Notes
**Live URL:** N/A (Deployment incomplete)

**Deployment Notes:**
I have fully developed the API and tested it locally. However, actual deployment to a service like Render, Railway, or Fly.io requires an account and credentials which were not available in this environment. If deployed, the deployment process would involve:
- Creating a Postgres database (e.g., on Neon).
- Pushing the code to GitHub and connecting the repo to Render/Railway.
- Setting the environment variables (`DATABASE_URL`, `SECRET_KEY`, `MONITORING_API_KEY`) in the platform's dashboard.
- Specifying the start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

## 2. Local Setup Instructions
To run this project locally, follow these steps:

1. **Clone the repository and enter the directory**:
   ```bash
   cd submission
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy the example environment file and adjust if necessary (defaults work for a local postgres instance or you can use sqlite for quick testing by modifying `DATABASE_URL`):
   ```bash
   cp .env.example .env
   ```
   *Note: For a quick test without installing PostgreSQL, you can change the `DATABASE_URL` in `.env` to `sqlite:///./skillbridge.db`.*

5. **Seed the database**:
   Run the seed script to populate the database with test data:
   ```bash
   python -m src.seed
   ```

6. **Run the server**:
   ```bash
   uvicorn src.main:app --reload
   ```

7. **Run the tests**:
   ```bash
   PYTHONPATH=. pytest tests/
   ```

## 3. Test Accounts
Run the seed script (`python -m src.seed`) to generate these accounts. The password for all accounts is **`password123`**.

- **Student**: `student1@example.com` (up to student15@example.com)
- **Trainer**: `trainer1@example.com` (up to trainer4@example.com)
- **Institution**: `inst1@example.com` or `inst2@example.com`
- **Programme Manager**: `pm@example.com`
- **Monitoring Officer**: `mo@example.com`

## 4. Sample curl Commands

**Login (Get Standard JWT)**
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "trainer1@example.com", "password": "password123"}'
```
*Extract the `access_token` from the response for the following requests.*

**Create a Batch (Trainer/Institution)**
```bash
curl -X POST "http://localhost:8000/batches" \
     -H "Authorization: Bearer <YOUR_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "New Batch", "institution_id": 3}'
```

**Generate Batch Invite (Trainer)**
```bash
curl -X POST "http://localhost:8000/batches/1/invite" \
     -H "Authorization: Bearer <TRAINER_TOKEN>"
```

**Join a Batch (Student)**
```bash
curl -X POST "http://localhost:8000/batches/join" \
     -H "Authorization: Bearer <STUDENT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"token": "<INVITE_TOKEN>"}'
```

**Mark Attendance (Student)**
```bash
curl -X POST "http://localhost:8000/attendance/mark" \
     -H "Authorization: Bearer <STUDENT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"session_id": 1, "status": "present"}'
```

**Get Monitoring Token (Monitoring Officer)**
```bash
curl -X POST "http://localhost:8000/auth/monitoring-token" \
     -H "Authorization: Bearer <MO_STANDARD_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"key": "hardcoded_monitoring_key_123"}'
```

**View Monitoring Attendance (Monitoring Officer)**
```bash
curl -X GET "http://localhost:8000/monitoring/attendance" \
     -H "Authorization: Bearer <MO_SCOPED_TOKEN>"
```

## 5. Schema Decisions
- **`batch_trainers`**: A many-to-many relationship table. This allows multiple trainers to co-teach a batch, and a single trainer to manage multiple batches.
- **`batch_invites`**: Stores uniquely generated tokens with an expiration date and a `used` boolean flag. This provides a secure, stateful way to invite students instead of just a static link, ensuring links can expire and can be one-time use if enforced (though currently implemented as reusable until expired, depending on business logic).
- **Dual-Token Approach**: 
  - Standard JWTs have a 24-hour expiry and are used for normal operations.
  - The Monitoring Officer requires a secondary "scoped" token explicitly for reading attendance data. This adds a layer of security, meaning if the standard MO token is compromised, the attacker still needs the explicit API key to generate the read-only scoped token. The scoped token has a shorter expiry (1 hour).

### JWT Payload Structure
- **Standard Token**: `{"user_id": 1, "role": "student", "exp": <timestamp>, "iat": <timestamp>}`
- **Monitoring Token**: `{"user_id": 5, "role": "monitoring_officer", "type": "monitoring", "exp": <timestamp>, "iat": <timestamp>}`

### Token Rotation/Revocation
In a real deployment, JWTs are stateless, so revoking them is tricky. I would implement a Redis-based blocklist (blacklist) storing the `jti` (JWT ID) of revoked tokens until their expiration time. For rotation, a short-lived access token + long-lived refresh token strategy would be used.

### Security Issue & Fix
Currently, the API key for the monitoring token is hardcoded/stored in `.env` as a single shared secret. A better approach would be to assign individual, rotatable API keys to each Monitoring Officer, stored securely (hashed) in the database.

## 6. Project Status
- **Fully Working**: Core API endpoints, Database models/schema, JWT Auth and RBAC, Pytest suite, Seed script.
- **Partially Done/Skipped**: Live deployment was skipped due to environment constraints.

## 7. What I'd do differently with more time
I would implement Alembic for database migrations rather than using `Base.metadata.create_all`. I would also add pagination to the GET endpoints, use asynchronous database drivers (`asyncpg`) for better concurrency, and implement a refresh token flow for better security.
