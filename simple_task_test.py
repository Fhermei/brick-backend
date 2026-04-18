import requests

# Create a session and login
session = requests.Session()

login_response = session.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "oyewoleoluwafemidavid1@gmail.com", "password": "Fatunbi11."}
)

print(f"Login: {login_response.status_code}")
print(f"Cookies: {session.cookies.get_dict()}")

# Get organizations
org_response = session.get("http://localhost:8000/api/v1/organizations/mine")
print(f"Organizations: {org_response.status_code}")

if org_response.status_code == 200:
    orgs = org_response.json().get("organizations", [])
    if orgs:
        org_id = orgs[0]["id"]
        print(f"Org ID: {org_id}")
        
        # Get projects
        proj_response = session.get(f"http://localhost:8000/api/v1/projects?org_id={org_id}")
        print(f"Projects: {proj_response.status_code}")
        
        if proj_response.status_code == 200:
            projects = proj_response.json().get("projects", [])
            if projects:
                project_id = projects[0]["id"]
                print(f"Project ID: {project_id}")
                
                # Create task - using the exact same format as curl
                task_data = {
                    "title": "API Test Task",
                    "description": "Created via API test",
                    "type": "task",
                    "priority": "medium",
                    "status": "todo",
                    "due_date": "2026-06-01",
                    "budget_allocated": 50000
                }
                
                # Try with and without trailing slash
                print("\nTrying without trailing slash...")
                task_response = session.post(
                    f"http://localhost:8000/api/v1/tasks?project_id={project_id}",
                    json=task_data
                )
                print(f"Response: {task_response.status_code}")
                if task_response.status_code != 201:
                    print(f"Error: {task_response.text}")
                
                # If that fails, try with trailing slash
                if task_response.status_code != 201:
                    print("\nTrying with trailing slash...")
                    task_response = session.post(
                        f"http://localhost:8000/api/v1/tasks/?project_id={project_id}",
                        json=task_data
                    )
                    print(f"Response: {task_response.status_code}")
                    if task_response.status_code != 201:
                        print(f"Error: {task_response.text}")