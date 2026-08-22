# System Architecture Document - Dayflow HRMS

## 1. System Overview

Dayflow is a decoupled, modern Human Resource Management System (HRMS) built using a **Flask REST API backend** and a **Vanilla HTML5/CSS3/ES6 JavaScript frontend**.

```text
[ Browser / Single-Page Client ]
          |
    HTTP REST API (JSON) + JWT Bearer Token
          v
[ Flask App Factory & Blueprints ] -> [ Auth & RBAC Middleware (@role_required) ]
          |
    Flask-SQLAlchemy ORM
          v
[ MySQL Database (dayflow_hrms) ]
```

---

## 2. Layered Architecture Breakdown

### 2.1 Presentation Layer (Frontend)
- Built with standard HTML5 elements, CSS3 variables design system, and modular vanilla JavaScript.
- Implements state management using browser `localStorage` for storing JWT access tokens and user profile info.
- Communicates asynchronously via standard `fetch()` API calls to `/api/...` backend endpoints.

### 2.2 Application / API Layer (Backend Flask)
- **Application Factory Pattern**: `backend/app.py` initializes extensions, configuration parameters, database connection pool, and registers modular blueprints.
- **Blueprints**:
  - `/api/auth`: Handles user sign up, email token verification, sign in, and active token introspection.
  - `/api/employees`: Manages employee profile listings, detail views, and edit permissions.
  - `/api/attendance`: Handles check-in/out timestamping, daily/weekly attendance logs, and status updates.
  - `/api/leaves`: Processes leave applications and Admin approval/rejection workflows.
  - `/api/payroll`: Manages read-only employee salary breakdown and Admin payroll controls.

### 2.3 Middleware & Security Layer
- **JWT Authorization**: Protects sensitive endpoints with `@token_required` decorator.
- **Role-Based Access Control (RBAC)**: Decorator `@role_required(['admin'])` verifies that the requesting user's decoded token role permits access. If unauthorized, returns HTTP 403 Forbidden.
- **Input Validation**: Centralized validation utility (`backend/utils/validators.py`) validates email format, strict password complexity, date bounds, and numeric inputs.

### 2.4 Persistence Layer (Database)
- MySQL instance storing relational entities: `users`, `email_verifications`, `employees`, `attendance`, `leaves`, and `payroll`.
- Managed via SQLAlchemy ORM models with explicit foreign key cascading rules and indexing.

---

## 3. Request-Response Lifecycle Flow

```text
User Action (e.g., Approve Leave)
  └─> JS event listener captures submit in `leaves.js`
  └─> Client fires `PUT /api/leaves/4/approve` with header `Authorization: Bearer <jwt_token>`
  └─> Flask handles request:
        1. `@token_required` validates JWT signature and expiration.
        2. `@role_required('admin')` verifies role == 'admin'.
        3. `leaves.py` route fetches Leave record from database.
        4. Status updated to 'Approved'.
        5. Attendance records automatically created/updated for the leave date range.
        6. DB transaction committed.
  └─> Returns HTTP 200 OK `{ "message": "Leave request approved successfully" }`.
  └─> Client receives JSON, displays success toast, updates leave table DOM dynamically.
```

---

## 4. Entity-Relationship Diagram (ERD - ASCII Representation)

```text
 +-------------------+       1:1      +-------------------+
 |       USERS       |--------------->|     EMPLOYEES     |
 +-------------------+                +-------------------+
 | id (PK)           |                | id (PK)           |
 | employee_id (UQ)  |                | user_id (FK)      |
 | email (UQ)        |                | first_name        |
 | password_hash     |                | last_name         |
 | role (ENUM)       |                | designation       |
 | is_verified (BOOL)|                | department        |
 +-------------------+                +-------------------+
           |                                  |
           | 1:N                              | 1:N
           v                                  v
 +-------------------+                +-------------------+
 | EMAIL_VERIFICATIONS|                |    ATTENDANCE     |
 +-------------------+                +-------------------+
 | id (PK)           |                | id (PK)           |
 | user_id (FK)      |                | employee_id (FK)  |
 | token (UQ)        |                | date              |
 | expires_at        |                | check_in/check_out|
 +-------------------+                | status (ENUM)     |
                                      +-------------------+
                                              |
                                              | 1:N
                                              v
                                      +-------------------+
                                      |      LEAVES       |
                                      +-------------------+
                                      | id (PK)           |
                                      | employee_id (FK)  |
                                      | leave_type (ENUM) |
                                      | start_date/end    |
                                      | status (ENUM)     |
                                      +-------------------+
                                              |
                                              | 1:1
                                              v
                                      +-------------------+
                                      |      PAYROLL      |
                                      +-------------------+
                                      | id (PK)           |
                                      | employee_id (FK)  |
                                      | basic_salary      |
                                      | allowances        |
                                      | deductions        |
                                      | net_salary        |
                                      +-------------------+
```
