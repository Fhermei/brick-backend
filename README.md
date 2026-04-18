# Brick SPMES Backend API

## Project Overview

Brick SPMES (Smart Project Monitoring & Evaluation System) is a comprehensive backend API built with FastAPI that provides robust project management, budget tracking, KPI monitoring, and reporting capabilities for organizations. The system is designed to handle real-time data processing with high scalability and performance.

## Developed By

- **Developer:** Oyewole Oluwafemi David
- **Phone:** 08106108753
- **Email:** fhermei2@gmail.com

## Technology Stack

### Core Framework
- **FastAPI** (v0.104.1) - High-performance async web framework
- **Uvicorn** (v0.24.0) - ASGI server for production
- **Pydantic** (v2.5.0) - Data validation and settings management

### Database
- **PostgreSQL** - Primary relational database
- **SQLAlchemy** (v2.0.23) - ORM for database operations
- **Alembic** (v1.12.1) - Database migrations
- **Redis** (v5.0.1) - Caching and rate limiting

### Authentication & Security
- **AWS Cognito** - User authentication and management
- **Python-JOSE** (v3.3.0) - JWT token handling
- **Passlib** (v1.7.4) - Password hashing
- **BCrypt** (v4.0.1) - Secure password encryption

### AWS Services
- **S3** - File storage (receipts, logos, reports)
- **SES** - Email sending for invitations
- **Cognito** - User management

### Reporting & Analytics
- **ReportLab** (v4.0.7) - PDF report generation
- **Matplotlib** (v3.8.2) - Chart generation for reports
- **Pandas** (v2.1.3) - Data analysis and KPI calculations
- **NumPy** (v1.26.2) - Numerical operations

## Project Structure
brick-backend/
├── src/
│ ├── init.py
│ ├── main.py # FastAPI application entry point
│ ├── core/
│ │ ├── init.py
│ │ ├── config.py # Application configuration
│ │ ├── security.py # Authentication & authorization
│ │ ├── kpi.py # KPI calculation utilities
│ │ └── permissions.py # Role-based access control
│ ├── models/
│ │ ├── init.py
│ │ ├── user.py # User model
│ │ ├── organization.py # Organization model
│ │ ├── project.py # Project model
│ │ ├── task.py # Task model with multi-assignee
│ │ ├── expense.py # Expense tracking model
│ │ ├── comment.py # Comments model
│ │ ├── role.py # Role management
│ │ ├── notification.py # Notifications model
│ │ ├── invite.py # Invitation tracking
│ │ ├── activity_log.py # Activity logging
│ │ ├── audit_log.py # Audit trail
│ │ ├── kpi.py # KPI tracking model
│ │ └── report.py # Report metadata
│ ├── schemas/
│ │ ├── init.py
│ │ ├── auth.py # Authentication schemas
│ │ ├── organization.py # Organization schemas
│ │ ├── project.py # Project schemas
│ │ ├── task.py # Task schemas
│ │ ├── expense.py # Expense schemas
│ │ ├── team.py # Team management schemas
│ │ ├── comment.py # Comment schemas
│ │ ├── notification.py # Notification schemas
│ │ ├── kpi.py # KPI schemas
│ │ ├── report.py # Report schemas
│ │ ├── budget.py # Budget schemas
│ │ └── audit.py # Audit schemas
│ ├── api/
│ │ ├── init.py
│ │ └── v1/
│ │ ├── init.py
│ │ ├── router.py # API router configuration
│ │ └── endpoints/
│ │ ├── auth.py # Authentication endpoints
│ │ ├── organizations.py # Organization CRUD
│ │ ├── projects.py # Project CRUD
│ │ ├── tasks.py # Task CRUD with status transitions
│ │ ├── expenses.py # Expense submission & approval
│ │ ├── team.py # Team invitation & management
│ │ ├── comments.py # Comment CRUD
│ │ ├── notifications.py # Notification management
│ │ ├── activities.py # Activity feed
│ │ ├── budget.py # Budget analytics
│ │ ├── kpis.py # KPI tracking
│ │ ├── reports.py # PDF report generation
│ │ ├── dashboard.py # Dashboard statistics
│ │ └── audit.py # Audit log retrieval
│ ├── services/
│ │ ├── init.py
│ │ ├── email_service.py # Email sending (SMTP/SES)
│ │ ├── notification_service.py # Notification creation
│ │ ├── audit_service.py # Audit logging
│ │ ├── storage_service.py # S3 file storage
│ │ ├── report_service.py # PDF report generation
│ │ └── kpi_service.py # KPI calculations
│ └── db/
│ ├── init.py
│ └── session.py # Database session management
├── templates/
│ └── emails/
│ ├── invite_email.html # Invitation email template
│ └── task_assigned.html # Task assignment email
├── .env.example # Environment variables template
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker Compose setup
└── seed_data.py # Database seeding script


## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register new user |
| POST | `/verify-email` | Verify email with code |
| POST | `/login` | User login (sets cookies) |
| POST | `/logout` | User logout (clears cookies) |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Get current user profile |
| POST | `/change-password` | Change user password |
| POST | `/forgot-password` | Request password reset |
| POST | `/confirm-forgot-password` | Reset password with code |

### Organizations (`/api/v1/organizations`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create organization |
| GET | `/mine` | List user's organizations |
| GET | `/{org_id}` | Get organization details |
| PATCH | `/{org_id}` | Update organization |
| DELETE | `/{org_id}` | Soft-delete organization |
| GET | `/{org_id}/members` | List organization members |

### Projects (`/api/v1/projects`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create project |
| GET | `/` | List projects (with filters) |
| GET | `/{project_id}` | Get project details |
| PATCH | `/{project_id}` | Update project |
| DELETE | `/{project_id}` | Soft-delete project |
| GET | `/{project_id}/members` | List project members |

### Tasks (`/api/v1/tasks`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create task (multi-assignee) |
| GET | `/` | List tasks (with filters) |
| GET | `/{task_id}` | Get task details |
| PATCH | `/{task_id}` | Update task |
| PATCH | `/{task_id}/status` | Update task status |
| DELETE | `/{task_id}` | Soft-delete task |
| GET | `/{task_id}/members` | Get available assignees |
| POST | `/{task_id}/budget` | Add budget item |

### Expenses (`/api/v1/expenses`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Submit expense (auto-approved) |
| GET | `/` | List expenses (with filters) |
| PATCH | `/{expense_id}/approve` | Approve expense |
| PATCH | `/{expense_id}/reject` | Reject expense |

### Team (`/api/v1/team`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/invite` | Invite team member |
| GET | `/` | List team members |
| GET | `/project/{project_id}` | List project members |
| PATCH | `/{member_id}/role` | Update member role |
| DELETE | `/{member_id}` | Remove member |
| DELETE | `/project/{project_id}/member/{user_id}` | Remove from project |

### KPIs (`/api/v1/kpis`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create KPI |
| GET | `/` | List KPIs for project |
| PATCH | `/{kpi_id}` | Update KPI actual value |
| DELETE | `/{kpi_id}` | Delete KPI |

### Budget (`/api/v1/budget`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/summary` | Get organization budget summary |
| GET | `/projects` | Get all project budgets |
| GET | `/project/{project_id}` | Get project budget |

### Reports (`/api/v1/reports`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/generate` | Generate PDF report |

### Dashboard (`/api/v1/dashboard`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats` | Get dashboard statistics |
| GET | `/recent-projects` | Get recent projects |
| GET | `/recent-tasks` | Get recent tasks |

### Other Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activities/recent` | Get recent activities |
| GET | `/notifications/` | Get user notifications |
| PATCH | `/notifications/mark-read` | Mark notifications read |
| GET | `/audit/` | Get audit logs (admin only) |

## KPI Formulas

### KAR (KPI Achievement Ratio)
KAR = (Actual Value / Target Value) × 100

**Thresholds:**
- **Good:** ≥ 100% (Emerald)
- **Satisfactory:** 75-99% (Green)
- **Warning:** 50-74% (Yellow)
- **Critical:** < 50% (Red)

### BUR (Budget Utilisation Rate)
BUR = (Total Spent / Total Budget) × 100


**Thresholds:**
- **OK:** < 80% (Green)
- **Alert:** 80-99% (Yellow)
- **Critical:** ≥ 100% (Red)

### BBR (Budget Burn Rate)
BBR = Total Spent / Days Elapsed

### Days to Exhaust
Days to Exhaust = Remaining Budget / BBR


## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Environment Variables (.env)
```env
# Application
APP_NAME=Brick SPMES API
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/brickdatabase
POSTGRES_DB=brickdatabase
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Redis
REDIS_URL=redis://localhost:6379

# AWS Cognito
AWS_REGION=us-east-1
COGNITO_CLIENT_ID=your_client_id
COGNITO_CLIENT_SECRET=your_client_secret
COGNITO_USER_POOL_ID=your_user_pool_id

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Frontend URL
FRONTEND_URL=http://localhost:5173

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

### Running with Docker
# Build and start containers
docker-compose up --build -d

# Check logs
docker-compose logs -f app

# Stop containers
docker-compose down

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
python -c "from src.db.session import Base, engine; from src.models import *; Base.metadata.create_all(bind=engine)"

# Seed data (optional)
python seed_data.py

# Run the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000