"""
Enhanced NGO Data Seeder - Creates comprehensive test data for NGOs
"""

import requests
import random
from datetime import datetime, timedelta
import time
import uuid

class NGOSystemSeeder:
    """Seeds realistic NGO project data for testing"""
    
    def __init__(self):
        self.BASE_URL = "http://localhost:8000/api/v1"
        self.session = requests.Session()
        
        # NGO Organizations with real humanitarian focus
        self.organizations = [
            {
                "name": "International Rescue Committee Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos"
            },
            {
                "name": "CARE International Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos"
            },
            {
                "name": "Oxfam Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos"
            },
            {
                "name": "Plan International Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos"
            },
            {
                "name": "ActionAid Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "NGN",
                "timezone": "Africa/Lagos"
            }
        ]
        
        # NGO Project Templates
        self.ngo_projects = [
            {
                "title": "Emergency Food Security Response",
                "description": "Providing emergency food assistance to 10,000 households",
                "budget": 2500000,
                "duration_months": 12,
                "tasks": [
                    {"title": "Rapid needs assessment", "priority": "urgent", "type": "research", "duration_days": 14},
                    {"title": "Food distribution planning", "priority": "high", "type": "task", "duration_days": 21},
                    {"title": "Procurement of food supplies", "priority": "high", "type": "task", "duration_days": 30},
                    {"title": "Beneficiary registration", "priority": "high", "type": "task", "duration_days": 45},
                    {"title": "Food distribution execution", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Post-distribution monitoring", "priority": "medium", "type": "research", "duration_days": 60}
                ]
            },
            {
                "title": "Girls Education Empowerment Program",
                "description": "Supporting 5,000 girls to complete secondary education",
                "budget": 3500000,
                "duration_months": 24,
                "tasks": [
                    {"title": "Community sensitization", "priority": "high", "type": "task", "duration_days": 30},
                    {"title": "Scholarship distribution", "priority": "high", "type": "task", "duration_days": 45},
                    {"title": "Mentorship program setup", "priority": "medium", "type": "task", "duration_days": 60},
                    {"title": "School infrastructure improvement", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Parent engagement workshops", "priority": "medium", "type": "task", "duration_days": 90},
                    {"title": "Learning outcomes assessment", "priority": "medium", "type": "research", "duration_days": 30}
                ]
            },
            {
                "title": "WASH in Schools Project",
                "description": "Providing clean water and sanitation facilities in 50 schools",
                "budget": 1800000,
                "duration_months": 18,
                "tasks": [
                    {"title": "School needs assessment", "priority": "high", "type": "research", "duration_days": 30},
                    {"title": "Borehole drilling", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Latrine construction", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Handwashing stations installation", "priority": "medium", "type": "task", "duration_days": 45},
                    {"title": "Hygiene education training", "priority": "high", "type": "task", "duration_days": 30},
                    {"title": "Water quality testing", "priority": "high", "type": "research", "duration_days": 21}
                ]
            },
            {
                "title": "Maternal Health Initiative",
                "description": "Reducing maternal mortality in rural communities",
                "budget": 4200000,
                "duration_months": 36,
                "tasks": [
                    {"title": "Baseline health survey", "priority": "high", "type": "research", "duration_days": 45},
                    {"title": "Midwife training program", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Mobile clinic deployment", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Birth kit distribution", "priority": "medium", "type": "task", "duration_days": 90},
                    {"title": "Emergency referral system", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Endline evaluation", "priority": "medium", "type": "research", "duration_days": 45}
                ]
            },
            {
                "title": "Child Protection Centers",
                "description": "Establishing safe spaces for vulnerable children",
                "budget": 2200000,
                "duration_months": 24,
                "tasks": [
                    {"title": "Child protection mapping", "priority": "high", "type": "research", "duration_days": 30},
                    {"title": "Center construction", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Social worker recruitment", "priority": "high", "type": "task", "duration_days": 45},
                    {"title": "Psychosocial support training", "priority": "high", "type": "task", "duration_days": 30},
                    {"title": "Case management system", "priority": "medium", "type": "task", "duration_days": 60},
                    {"title": "Community awareness campaign", "priority": "medium", "type": "task", "duration_days": 90}
                ]
            }
        ]
    
    def login(self):
        """Authenticate and get session"""
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        response = self.session.post(f"{self.BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code}")
        print("Authenticated successfully")
        return True
    
    def create_organization(self, org_data):
        """Create an organization"""
        response = self.session.post(f"{self.BASE_URL}/organizations/", json=org_data)
        if response.status_code == 201:
            return response.json()
        return None
    
    def create_project(self, org_id, project_data, currency):
        """Create a project"""
        start_date = datetime.now() - timedelta(days=random.randint(30, 180))
        end_date = datetime.now() + timedelta(days=project_data["duration_months"] * 30)
        
        payload = {
            "title": project_data["title"],
            "description": project_data["description"],
            "status": "active",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_budget": project_data["budget"],
            "currency": currency
        }
        response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={org_id}",
            json=payload
        )
        if response.status_code == 201:
            return response.json()
        return None
    
    def create_task(self, project_id, task_data):
        """Create a task"""
        due_date = datetime.now() + timedelta(days=task_data["duration_days"])
        payload = {
            "title": task_data["title"],
            "description": f"Complete {task_data['title'].lower()} for the project",
            "type": task_data["type"],
            "priority": task_data["priority"],
            "status": random.choice(["todo", "in_progress", "review"]),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "budget_allocated": random.randint(50000, 500000)
        }
        response = self.session.post(
            f"{self.BASE_URL}/tasks?project_id={project_id}",
            json=payload
        )
        if response.status_code == 201:
            return response.json()
        return None
    
    def seed_all(self):
        """Run complete seeding process"""
        print("\n" + "=" * 70)
        print("BRICK SPMES - NGO DATA SEEDER")
        print("=" * 70)
        
        print("\nStep 1: Authenticating...")
        self.login()
        
        print("\nStep 2: Creating NGO Organizations...")
        created_orgs = []
        for org_data in self.organizations:
            org = self.create_organization(org_data)
            if org:
                created_orgs.append(org)
                print(f"  Created: {org['name']}")
            time.sleep(0.3)
        
        print(f"\nCreated {len(created_orgs)} organizations")
        
        print("\nStep 3: Creating Projects and Tasks...")
        total_projects = 0
        total_tasks = 0
        
        for org in created_orgs:
            print(f"\n  Organization: {org['name']}")
            for project_template in self.ngo_projects:
                project = self.create_project(org["id"], project_template, org["currency"])
                if project:
                    total_projects += 1
                    print(f"    Project: {project['title']} (Budget: {org['currency']} {project_template['budget']:,.0f})")
                    
                    task_count = 0
                    for task_template in project_template["tasks"]:
                        task = self.create_task(project["id"], task_template)
                        if task:
                            task_count += 1
                            total_tasks += 1
                        time.sleep(0.1)
                    print(f"      Created {task_count} tasks")
                time.sleep(0.2)
        
        print("\n" + "=" * 70)
        print("SEEDING COMPLETE")
        print("=" * 70)
        print(f"  Organizations created: {len(created_orgs)}")
        print(f"  Projects created: {total_projects}")
        print(f"  Tasks created: {total_tasks}")
        print("=" * 70)
        
        return created_orgs

if __name__ == "__main__":
    seeder = NGOSystemSeeder()
    seeder.seed_all()