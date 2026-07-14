# 🎓 College Management System (CMS)

A MODERN full-stack **College Management System** built with **FastAPI**, designed to simplify academic administration by managing students, teachers, courses, departments, authentication, sessions, and background tasks through a scalable REST API architecture. And with HTML, CSS, and JavaScript that streamlines academic administration through an intuitive web interface following modern backend architecture and clean software design principles.

This project with demonstrates modern backend development practices including RESTful API design, JWT authentication, asynchronous task processing, ORM-based database management, Docker integration, and clean project organization.

---

# 🛠 Tech Stack

-Frontend: HTML, CSS3, JavaScript, Ajax
-Backend: FastAPI, Python
-API Documentation: Swagger UI
-Database: PostgreSQL, SQLAlchemy ORM, Alembic
-Authentication: JWT, OAuth2, Passlib
-Background Tasks: Celery, Redis
-Email: SMTP, MailHog
-Validation: Pydantic
-Containerization: Docker, Docker Compose
-Package Manager: uv

## Frontend
- HTML
- CSS3
- JavaScript
- Ajax

## Backend
- FastAPI
- Python 

## API Documentation
- Swagger UI

## Database
- PostgreSQL
- SQLAlchemy ORM
- Alembic

## Authentication
- JWT
- OAuth2
- Passlib

## Background Tasks
- Celery
- Redis

## Email
- SMTP
- MailHog

## Validation
- Pydantic

## Containerization
- Docker
- Docker Compose

## Package Manager 
- uv

## Webserver
-  uvicorn
---

# 🚀 Features

## 🎨 Frontend
- Accounts/authentication interface
- Student management interface
- Teacher management interface
- Course management interface
- Form validation
- Dynamic UI with JavaScript
- API integration with FastAPI

## ⚙ Backend
- RESTful APIs
- JWT Authentication
- Session Management
- CRUD Operations
- ORM Relationships
- Validation
- Exception Handling
- Modular Router Architecture

## Authentication & Authorization
- JWT Access & Refresh Token authentication
- Secure password hashing using Passlib
- Login and Logout functionality
- Password change support
- Email confirmation for password changes
- OAuth2 authentication flow
- Session management
- Active device tracking
- Token revocation support

---

## Student Management
- Create student records
- Update student information
- Delete students
- Retrieve individual student details
- Retrieve all students
- Student-course enrollment
- Department assignment
- Academic session tracking

---

## Teacher Management
- Create teacher profiles
- Update teacher information
- Delete teachers
- Assign teachers to departments
- Assign teachers to courses
- HOD assignment support
- Retrieve teacher details

---

## Course Management
- Create courses
- Update courses
- Delete courses
- Assign course in-charge
- Assign multiple teachers
- Enroll multiple students
- Retrieve course information

---

## Department Management
- Create departments
- Manage department information
- Assign teachers to departments
- Department relationship mapping

---

## User Management
- User registration
- User login
- Role-based user creation
- Secure password storage
- User profile management

---

## Background Task Processing
Powered by **Celery + Redis**

- Email sending in background
- Automatic retry mechanism
- Manual retry endpoint
- Task status monitoring
- Task history logging
- Failure tracking

---

## Email System
- Password change confirmation emails
- SMTP integration
- MailHog support for local development
- Background email processing

---

## Session Management
- Device tracking
- IP address logging
- Login timestamp
- Last activity tracking
- Active/Inactive session handling

---

## REST API
- Fully RESTful architecture
- JSON responses
- Proper HTTP status codes
- Request validation
- Error handling
- Modular routers

---


# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/college-management-system.git

cd college-management-system
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install -e .
```

---

## 4. Configure Environment Variables

Create a `.env` file.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/cms

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_URL=redis://localhost:6379/0

SMTP_HOST=localhost

SMTP_PORT=1025

SMTP_USERNAME=

SMTP_PASSWORD=
```

---

## 5. Run Database Migrations

```bash
alembic upgrade head
```

---

## 6. Start Redis

```bash
docker compose up redis -d
```

---

## 7. Start MailHog

```bash
docker compose up mailhog -d
```

---

## 8. Start Celery Worker

```linux
celery -A tasks worker -l info
```
```bash
celery -A tasks worker --pool=solo --loglevel=info
```

## 9. Run FastAPI

```bash
uv run uvicorn main:app --reload
```

---

# 📖 API Documentation

Once the server is running:

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 🗄 Database Design

Main entities include:

- Users
- Students
- Teachers
- Courses
- Departments
- Authentication Tokens
- User Sessions
- Task Logs

Relationships:

- One User → One Student/Teacher
- Many Students ↔ Many Courses
- Many Teachers ↔ Many Courses
- One Department → Many Teachers
- One Teacher → Course In-charge

---

# 🔐 Security Features

- Password hashing with Passlib
- JWT Authentication
- Access & Refresh Tokens
- OAuth2 Password Flow
- Session Tracking
- Protected API Endpoints
- Token Revocation
- Input Validation
- Structured Error Responses

---

# ⚡ Background Tasks

The application uses Celery for asynchronous processing.

Supported tasks include:

- Sending emails
- Automatic retries
- Manual retry endpoint
- Task logging
- Failure monitoring

---

# 📬 Email Workflow

```
Password Changed
        │
        ▼
FastAPI API
        │
        ▼
Celery Task
        │
        ▼
Redis Queue
        │
        ▼
SMTP / MailHog
        │
        ▼
Email Delivered
```

---

# 📸 Screenshots

Add screenshots of:

- Swagger UI
- Login
- Dashboard
- Student APIs
- Teacher APIs
- Celery Worker
- Redis Commander
- MailHog

---

# 🧪 Testing

Run the test suite

```bash
pytest
```

---

# 👩‍💻 Author

**Arzoo Fatima**

Backend Developer | Python Developer

Tech Stack:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Celery
- Redis
- Docker
- JWT Authentication

---

# 📄 License

This project is intended for educational and portfolio purposes.
