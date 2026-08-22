# Dayflow - Human Resource Management System

*Every workday, perfectly aligned.*

Built for **Odoo x NMIT Bangalore Hackathon 2026**

## Team

- **Nikita Raj** (Team Leader)
- **vishal-49**

## Overview

Dayflow is a Human Resource Management System (HRMS) that digitizes and streamlines core HR operations including employee onboarding, profile management, attendance tracking, leave management, payroll visibility, and approval workflows for Admins and HR officers.

## Features

- Secure authentication (Sign Up / Sign In) with role-based access
- Role-based dashboards (Admin vs Employee)
- Employee profile management (view/edit)
- Attendance tracking (check-in/check-out, daily/weekly view)
- Leave & time-off management with approval workflow
- Payroll/salary visibility (read-only for employees, full control for admin)

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Auth:** JWT (python-jose), password hashing (passlib)

## Project Structure
## Project Structure

​```
odoo-nmit-hackathon-2026/
│
├── README.md
├── .gitignore
├── requirements.txt
├── .env.example
│
├── backend/
│   ├── app.py                      # FastAPI app entry point
│   │
│   ├── models/                     # Database models (SQLAlchemy)
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── attendance.py
│   │   ├── leave.py
│   │   └── payroll.py
│   │
│   ├── routes/                     # API endpoints
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── attendance.py
│   │   ├── leaves.py
│   │   └── payroll.py
│   │
│   └── utils/                      # Helper functions
│       ├── auth.py                 # Password hashing, JWT helpers
│       └── validators.py           # Input validation helpers
│
├── frontend/
│   ├── index.html
│   │
│   ├── pages/
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── employee-dashboard.html
│   │   ├── admin-dashboard.html
│   │   ├── profile.html
│   │   ├── attendance.html
│   │   ├── leaves.html
│   │   └── payroll.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       ├── attendance.js
│       ├── leaves.js
│       └── payroll.js
│
├── database/
│   └── schema.sql                  # Database schema
│
└── docs/
    └── architecture.md
​```

## Setup & Installation

1. Clone the repository
```bash
   git clone https://github.com/nikitaraj3804-sudo/odoo-nmit-hackathon-2026.git
   cd odoo-nmit-hackathon-2026
```

2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Set up environment variables
```bash
   cp .env.example .env
```

4. Run the backend server
```bash
   uvicorn backend.app:app --reload
```

5. Open `frontend/index.html` in your browser

## User Roles

| Role | Access |
|---|---|
| Admin / HR Officer | Manages employees, approves leave & attendance, views/edits payroll |
| Employee | Views own profile, attendance, applies for leave, views own salary |

## Future Enhancements

- Email & notification alerts
- Analytics & reports dashboard (salary slips, attendance reports)