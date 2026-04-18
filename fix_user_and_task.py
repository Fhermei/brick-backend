"""
Fix user in local database and test task creation
"""

import requests
import uuid
from src.db.session import SessionLocal
from src.models.user import User

# First, add the user to local database if not exists
db = SessionLocal()

# Check if user exists
cognito_sub = "f498e478-50e1-7054-38a9-61d2fcdff165"
user = db.query(User).filter(User.cognito_sub == cognito_sub).first()

if not user:
    print("User not found in local DB. Creating...")
    user = User(
        id=uuid.uuid4(),
        name="Test User",
        email="oyewoleoluwafemidavid1@gmail.com",
        cognito_sub=cognito_sub,
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user with ID: {user.id}")
else:
    print(f"User already exists: {user.id} - {user.email}")

db.close()

# Now test task creation with proper session
session = requests.Session()

# Login
login_data = {
    "email": "oyewoleoluwafemidavid1@gmail.com",
    "password": "Fatunbi11."
}

print("\nLogging in...")
login_response = session.post("http://localhost:8000/api/v1/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    print("Login successful!")
    
    # Get organizations
    org_response = session.get("http://localhost:8000/api/v1/organizations/mine")
    print(f"Organizations response: {org_response.status_code}")
    
    if org_response.status_code == 200:
        orgs = org_response.json().get("organizations", [])
        if orgs:
            org_id = orgs[0]["id"]
            print(f"Using organization: {org_id}")
            
            # Get projects
            projects_response = session.get(f"http://localhost:8000/api/v1/projects?org_id={org_id}")
            print(f"Projects response: {projects_response.status_code}")
            
            if projects_response.status_code == 200:
                projects = projects_response.json().get("projects", [])
                if projects:
                    project_id = projects[0]["id"]
                    print(f"Using project: {project_id}")
                    
                    # Create a test task
                    task_data = {
                        "title": "Test Task from Script",
                        "description": "This is a test task",
                        "type": "task",
                        "priority": "high",
                        "status": "todo",
                        "due_date": "2026-05-15",
                        "budget_allocated": 100000
                    }
                    
                    task_response = session.post(
                        f"http://localhost:8000/api/v1/tasks?project_id={project_id}",
                        json=task_data
                    )
                    print(f"Task creation status: {task_response.status_code}")
                    if task_response.status_code == 201:
                        print(f"Task created successfully!")
                        print(f"Task data: {task_response.json()}")
                    else:
                        print(f"Error: {task_response.text}")
                else:
                    print("No projects found - create one first")
            else:
                print(f"Failed to get projects")
        else:
            print("No organizations found")
    else:
        print(f"Failed to get organizations")
else:
    print(f"Login failed: {login_response.text}")