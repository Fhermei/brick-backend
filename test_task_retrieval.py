import requests

session = requests.Session()

# Login
login_response = session.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "oyewoleoluwafemidavid1@gmail.com", "password": "Fatunbi11."}
)
print(f"Login: {login_response.status_code}")

if login_response.status_code == 200:
    # Get organizations
    org_response = session.get("http://localhost:8000/api/v1/organizations/mine")
    if org_response.status_code == 200:
        orgs = org_response.json().get("organizations", [])
        if orgs:
            org_id = orgs[0]["id"]
            
            # Get projects
            proj_response = session.get(f"http://localhost:8000/api/v1/projects?org_id={org_id}")
            if proj_response.status_code == 200:
                projects = proj_response.json().get("projects", [])
                if projects:
                    project_id = projects[0]["id"]
                    
                    # List tasks for this project
                    tasks_response = session.get(f"http://localhost:8000/api/v1/tasks?project_id={project_id}")
                    print(f"List tasks: {tasks_response.status_code}")
                    
                    if tasks_response.status_code == 200:
                        tasks = tasks_response.json().get("tasks", [])
                        print(f"Found {len(tasks)} tasks")
                        
                        if tasks:
                            task_id = tasks[0]["id"]
                            print(f"First task ID: {task_id}")
                            print(f"Task title: {tasks[0]['title']}")
                            print(f"Task status: {tasks[0]['status']}")
                            
                            # Get single task
                            single_task = session.get(f"http://localhost:8000/api/v1/tasks/{task_id}")
                            print(f"Get single task: {single_task.status_code}")
                            
                            if single_task.status_code == 200:
                                print(f"Task details: {single_task.json()}")