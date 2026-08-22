# Dayflow - Human Resource Management System (HRMS)

> **Tagline:** *"Every workday, perfectly aligned."*  
> **Submission:** odoo-nmit-hackathon-2026

---

## Overview

**Dayflow** is a full-stack, enterprise-grade Human Resource Management System designed to streamline core HR operations. From automated onboarding and email verification to real-time attendance tracking, leave approval workflows, and payroll structure visibility, Dayflow brings clarity and alignment to every workday.

---

## Key Features

### 1. Authentication & Role-Based Access Control (RBAC)
- **Registration**: Register with Employee ID, Email, Password, and Role (`Admin / HR Officer` vs `Employee`).
- **Password Enforcement**: Validates minimum 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character (both client-side and server-side).
- **Email Verification**: Token generation flow with verification endpoint (`/api/auth/verify/<token>`) and interactive UI modal.
- **Role Enforcement**: Strict server-side RBAC using `@role_required(['admin'])` decorators to ensure employees cannot access management APIs.

### 2. Employee Profile Management
- Comprehensive profile views with personal info, job details, department, date of joining, documents list, and profile avatar.
- **Granular Permissions**: Employees can edit limited profile fields (phone, address, avatar), while HR Admins can update all details.

### 3. Attendance Management
- **One-Click Check-In / Check-Out**: Record real-time timestamps directly from the dashboard.
- **Status Lifecycle**: `Present`, `Absent`, `Half-day`, and `Leave`.
- **Views**: Daily and weekly matrix views with date range filtering. Admin can view and override attendance for any employee.

### 4. Leave & Time-Off Workflows
- **Apply for Leave**: Select leave type (`Paid`, `Sick`, `Unpaid`), date range (with end date ≥ start date validation), and optional remarks.
- **Approval Engine**: Admins can review, approve, or reject leave applications with comments.
- **Automated Sync**: Approving a leave application automatically updates attendance status to `Leave` across the specified date range.

### 5. Payroll Visibility & Governance
- **Employee View**: Read-only breakdown of Basic Salary, Allowances, Deductions, and Net Pay.
- **Admin Control**: HR Officers can view and update salary structures for any employee. Server-side validation guarantees non-negative numeric inputs and auto-calculates Net Pay (`Basic + Allowances - Deductions`).

---

## Technology Stack

- **Backend**: Python 3.11+, Flask (Application Factory), Flask-SQLAlchemy, PyJWT, Flask-CORS, bcrypt / `werkzeug.security`, Gunicorn WSGI.
- **Database**: MySQL (via PyMySQL / mysqlclient).
- **Frontend**: Vanilla HTML5, CSS3 (Modern SaaS design system with CSS custom properties), Vanilla JavaScript ES6 (`fetch` API, modular JS files).

---

## Setup & Installation Instructions

### Prerequisites
- Python 3.11 or higher
- MySQL Server (v8.0+ recommended)
- Web browser (Chrome, Firefox, Safari, Edge)

### 1. Database Initialization
Create the MySQL database and schema:
```bash
mysql -u root -p < database/schema.sql
```

### 2. Backend Setup
1. Navigate to the backend directory or project root:
```bash
cd "odoo hackathon 1"
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

2. Configure environment variables:
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Edit `.env` to match your local MySQL credentials (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`).

3. Launch Flask Server:
```bash
python backend/app.py
```
The backend REST API will run on `http://127.0.0.1:5005`.

### 3. Frontend Setup
Simply open `frontend/index.html` in your browser, or serve it using a simple static server:
```bash
# Using Python built-in server
python -m http.server 8000 --directory frontend
```
Then visit `http://localhost:8000` in your web browser.

---

## Deploying to Railway

Follow these steps to deploy Dayflow to [Railway](https://railway.app):

1. **Push Repository**: Push this codebase to your GitHub repository.
2. **Create Railway Project**: Log into Railway, click **New Project**, and select **Deploy from GitHub repo**. Select this repository.
3. **Add Railway MySQL Database**:
   - In the same Railway project dashboard, click **+ New** -> **Database** -> **Add MySQL**.
   - Railway will automatically generate connection variables (`MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`).
4. **Import Database Schema**:
   - Connect to your Railway MySQL instance using any MySQL GUI client (TablePlus, DBeaver) or Railway CLI query console.
   - Run the full contents of `database/schema.sql` to initialize tables.
5. **Configure Environment Variables**:
   - In your Railway Web Service -> **Variables** tab, set:
     - `SECRET_KEY`: A secure random secret key.
     - `JWT_SECRET_KEY`: A secure random JWT secret key.
     - `CORS_ORIGINS`: Set to your deployed frontend domain or wildcard `*`.
6. **Verify Deployment & Gunicorn**:
   - Railway will detect the `Procfile` and execute `gunicorn 'backend.app:create_app()'`.
   - Check the Railway deployment logs to confirm zero boot errors.
7. **Frontend API URL Setup**:
   - If deploying the static frontend separately (e.g. Netlify/Vercel), set `const API_BASE_URL` in `frontend/js/auth.js` to your Railway backend URL (e.g. `https://your-dayflow-backend.up.railway.app/api`).
   - If serving frontend from Flask directly, no change is required — Dayflow serves both automatically!

---

## API Endpoint Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/signup` | Register new user & issue verification token | Public |
| `GET` | `/api/auth/verify/<token>` | Verify user account email | Public |
| `POST` | `/api/auth/login` | Authenticate user & issue JWT token | Public |
| `GET` | `/api/auth/me` | Fetch active logged-in user profile | Authenticated |
| `GET` | `/api/employees` | List all employees (with search/filter) | Admin |
| `GET` | `/api/employees/<id>` | View employee detail profile | Admin / Owner |
| `PUT` | `/api/employees/<id>` | Update profile (granular field permissions) | Admin / Owner |
| `POST` | `/api/attendance/check-in` | Record check-in timestamp for today | Authenticated |
| `POST` | `/api/attendance/check-out` | Record check-out timestamp for today | Authenticated |
| `GET` | `/api/attendance` | Fetch attendance records | Admin (All) / Employee (Own) |
| `POST` | `/api/leaves` | Apply for new leave request | Authenticated |
| `GET` | `/api/leaves` | View leave requests | Admin (All) / Employee (Own) |
| `PUT` | `/api/leaves/<id>/approve` | Approve/Reject leave request & sync attendance | Admin |
| `GET` | `/api/payroll/me` | View own salary breakdown (read-only) | Employee |
| `GET` | `/api/payroll/<id>` | View salary breakdown of an employee | Admin |
| `PUT` | `/api/payroll/<id>` | Update employee salary components | Admin |

---

## 📄 License
Developed for **odoo-nmit-hackathon-2026**. All rights reserved.
