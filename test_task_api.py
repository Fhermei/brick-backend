import requests

# Login first
session = requests.Session()
login_data = {
    "email": "oyewoleoluwafemidavid1@gmail.com",
    "password": "Fatunbi11."
}

print("Logging in...")
login_response = session.post("http://localhost:8000/api/v1/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")
print(f"Cookies: {session.cookies.get_dict()}")

if login_response.status_code == 200:
    print("Login successful!")
    
    # First, get an organization
    org_response = session.get("http://localhost:8000/api/v1/organizations/mine")
    print(f"Organizations response: {org_response.status_code}")
    
    if org_response.status_code == 200:
        orgs = org_response.json().get("organizations", [])
        if orgs:
            org_id = orgs[0]["id"]
            print(f"Using organization: {org_id}")
            
            # Get projects for this org
            projects_response = session.get(f"http://localhost:8000/api/v1/projects?org_id={org_id}")
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
                        print(f"Task created: {task_response.json()}")
                    else:
                        print(f"Error: {task_response.text}")
                else:
                    print("No projects found")
            else:
                print(f"Failed to get projects: {projects_response.status_code}")
        else:
            print("No organizations found")
    else:
        print(f"Failed to get organizations: {org_response.status_code}")
else:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")