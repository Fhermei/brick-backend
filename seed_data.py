"""
Database seeding script for testing
Creates organizations, projects, and tasks with realistic data
"""

import requests
import random
from datetime import datetime, timedelta
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class BrickSeeder:
    """Seeder class for Brick Backend"""
    
    def __init__(self):
        self.BASE_URL = "http://localhost:8000/api/v1"
        self.session = requests.Session()
        self.created_orgs = []
        self.created_projects = []
        self.created_tasks = []
        self.created_expenses = []
        self.created_kpis = []
        self.auth_cookies = None
        
        # ============================================================
        # ORGANIZATIONS
        # ============================================================
        self.organizations = [
            {
                "name": "Sterling Engineering & Construction Ltd",
                "industry": "Engineering / Construction",
                "currency": "NGN",
                "timezone": "Africa/Lagos",
            },
            {
                "name": "Red Cross Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "NGN",
                "timezone": "Africa/Lagos",
            },
            {
                "name": "Doctors Without Borders - Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos",
            },
            {
                "name": "Save the Children International",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos",
            },
            {
                "name": "World Food Programme Nigeria",
                "industry": "NGO / Non-profit",
                "currency": "USD",
                "timezone": "Africa/Lagos",
            },
            {
                "name": "Green Earth Initiative",
                "industry": "Environmental",
                "currency": "NGN",
                "timezone": "Africa/Lagos",
            }
        ]
        
        # ============================================================
        # ENGINEERING PROJECTS
        # ============================================================
        self.engineering_projects = [
            {
                "title": "Lagos-Ibadan Expressway Phase 2",
                "description": "50km dual carriageway construction including bridges and drainage systems",
                "budget": 85000000000,
                "start_offset_days": -180,
                "end_offset_days": 540,
                "status": "active",
                "tasks": [
                    {"title": "Site clearing and preparation", "priority": "high", "type": "task", "duration_days": 30},
                    {"title": "Geotechnical soil investigation", "priority": "high", "type": "research", "duration_days": 21},
                    {"title": "Earthworks and embankment", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Drainage system installation", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Pavement layer construction", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Bridge construction", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Asphalt paving", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Road marking and signage", "priority": "medium", "type": "task", "duration_days": 30},
                    {"title": "Quality control testing", "priority": "high", "type": "task", "duration_days": 210},
                    {"title": "Project management and reporting", "priority": "high", "type": "report", "duration_days": 365}
                ]
            },
            {
                "title": "Eko Atlantic City - Phase 3",
                "description": "Land reclamation and infrastructure development",
                "budget": 45000000000,
                "start_offset_days": -90,
                "end_offset_days": 450,
                "status": "active",
                "tasks": [
                    {"title": "Marine geotechnical survey", "priority": "high", "type": "research", "duration_days": 30},
                    {"title": "Land reclamation using sand filling", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Sea wall construction", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Drainage and flood control", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Road network development", "priority": "high", "type": "task", "duration_days": 150},
                    {"title": "Underground utility installation", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Power distribution network", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Water supply and sewage systems", "priority": "high", "type": "task", "duration_days": 100}
                ]
            },
            {
                "title": "Abuja Light Rail Project - Phase 1",
                "description": "Light rail transit system connecting Abuja city center to airport",
                "budget": 120000000000,
                "start_offset_days": -365,
                "end_offset_days": 730,
                "status": "active",
                "tasks": [
                    {"title": "Route survey and feasibility study", "priority": "high", "type": "research", "duration_days": 60},
                    {"title": "Track alignment design", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Land acquisition and compensation", "priority": "high", "type": "task", "duration_days": 120},
                    {"title": "Track bed preparation", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Rail track installation", "priority": "high", "type": "task", "duration_days": 240},
                    {"title": "Station construction", "priority": "high", "type": "task", "duration_days": 300},
                    {"title": "Electrification and power systems", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Signaling and communication", "priority": "high", "type": "task", "duration_days": 150},
                    {"title": "Testing and commissioning", "priority": "high", "type": "task", "duration_days": 90}
                ]
            }
        ]
        
        # ============================================================
        # NGO PROJECTS
        # ============================================================
        self.ngo_projects = [
            {
                "title": "North-East Emergency Response - IDP Camps",
                "description": "Emergency relief for internally displaced persons",
                "budget": 3500000000,
                "start_offset_days": -60,
                "end_offset_days": 270,
                "status": "active",
                "tasks": [
                    {"title": "Emergency needs assessment", "priority": "urgent", "type": "research", "duration_days": 14},
                    {"title": "Distribution of food supplies", "priority": "urgent", "type": "task", "duration_days": 180},
                    {"title": "Provision of clean water", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Emergency shelter construction", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Medical clinic setup", "priority": "high", "type": "task", "duration_days": 45},
                    {"title": "Psychosocial support services", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Child protection activities", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "WASH facilities construction", "priority": "high", "type": "task", "duration_days": 90}
                ]
            },
            {
                "title": "Maternal and Child Health Program",
                "description": "Reducing maternal and child mortality",
                "budget": 2800000000,
                "start_offset_days": -120,
                "end_offset_days": 300,
                "status": "active",
                "tasks": [
                    {"title": "Health facility assessment", "priority": "high", "type": "research", "duration_days": 30},
                    {"title": "Recruitment of medical staff", "priority": "high", "type": "task", "duration_days": 45},
                    {"title": "Medical equipment procurement", "priority": "high", "type": "task", "duration_days": 60},
                    {"title": "Antenatal care services", "priority": "high", "type": "task", "duration_days": 240},
                    {"title": "Vaccination campaigns", "priority": "high", "type": "task", "duration_days": 90},
                    {"title": "Nutritional screening", "priority": "high", "type": "task", "duration_days": 180},
                    {"title": "Health promotion activities", "priority": "medium", "type": "task", "duration_days": 180}
                ]
            }
        ]
        
        # ============================================================
        # KPI Templates
        # ============================================================
        self.kpi_templates = {
            "construction": [
                {"indicator_name": "Construction Progress vs Schedule", "target_value": 95, "unit": "%"},
                {"indicator_name": "Safety Incident Rate", "target_value": 0, "unit": "incidents"},
                {"indicator_name": "Quality Control Pass Rate", "target_value": 98, "unit": "%"},
                {"indicator_name": "Budget Utilization Efficiency", "target_value": 100, "unit": "%"},
                {"indicator_name": "Workforce Productivity", "target_value": 90, "unit": "%"}
            ],
            "ngo": [
                {"indicator_name": "Beneficiary Reach", "target_value": 100000, "unit": "people"},
                {"indicator_name": "Program Completion Rate", "target_value": 95, "unit": "%"},
                {"indicator_name": "Fund Utilization Efficiency", "target_value": 95, "unit": "%"},
                {"indicator_name": "Community Satisfaction", "target_value": 85, "unit": "%"},
                {"indicator_name": "Staff Training Completion", "target_value": 100, "unit": "%"}
            ]
        }
    
    def login(self):
        """Authenticate and get session"""
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        
        # Clear any existing cookies
        self.session.cookies.clear()
        
        response = self.session.post(f"{self.BASE_URL}/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Login failed: {response.status_code}")
        
        print("✅ Authenticated successfully")
        print(f"   Session cookies: {list(self.session.cookies.keys())}")
        return True
    
    def create_organization(self, org_data):
        """Create a single organization"""
        response = self.session.post(f"{self.BASE_URL}/organizations/", json=org_data)
        
        if response.status_code == 201:
            org = response.json()
            print(f"   ✅ Created: {org['name']}")
            return org
        else:
            print(f"   ❌ Failed to create {org_data['name']}: {response.status_code}")
            if response.status_code == 401:
                print(f"      Authentication failed - please check your login credentials")
            return None
    
    def create_project(self, org_id, project_data, org_currency):
        """Create a project within an organization"""
        payload = {
            "title": project_data["title"],
            "description": project_data["description"],
            "status": project_data["status"],
            "start_date": (datetime.now() + timedelta(days=project_data["start_offset_days"])).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=project_data["end_offset_days"])).strftime("%Y-%m-%d"),
            "total_budget": project_data["budget"],
            "currency": org_currency
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={org_id}",
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"     ❌ Failed: {project_data['title']} - {response.status_code}")
            return None
    
    def create_task(self, project_id, task_data):
        """Create a task within a project"""
        due_date = datetime.now() + timedelta(days=task_data["duration_days"])
        
        # Random status based on due date
        days_from_now = (due_date - datetime.now()).days
        if days_from_now < 0:
            status = random.choice(["completed", "blocked"])
        elif days_from_now < 30:
            status = random.choice(["in_progress", "review"])
        else:
            status = random.choice(["todo", "in_progress"])
        
        task_payload = {
            "title": task_data["title"],
            "description": f"Complete {task_data['title'].lower()} for the project",
            "type": task_data["type"],
            "priority": task_data["priority"],
            "status": status,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "budget_allocated": random.randint(500000, 5000000)
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/tasks?project_id={project_id}",
                json=task_payload
            )
            
            if response.status_code == 201:
                return response.json()
            return None
        except Exception as e:
            print(f"        Task error: {e}")
            return None
    
    def create_kpi(self, project_id, kpi_data, project_title):
        """Create a KPI for a project"""
        period_start = datetime.now() - timedelta(days=random.randint(30, 90))
        period_end = datetime.now() + timedelta(days=random.randint(30, 180))
        
        # Generate random actual value (between 40-100% of target)
        actual_value = random.randint(int(kpi_data["target_value"] * 0.4), int(kpi_data["target_value"]))
        
        payload = {
            "indicator_name": kpi_data["indicator_name"],
            "description": f"Track {kpi_data['indicator_name'].lower()} for {project_title}",
            "target_value": kpi_data["target_value"],
            "unit": kpi_data["unit"],
            "period_start": period_start.strftime("%Y-%m-%d"),
            "period_end": period_end.strftime("%Y-%m-%d")
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/kpis?project_id={project_id}",
                json=payload
            )
            
            if response.status_code == 201:
                kpi = response.json()
                # Update actual value
                update_response = self.session.patch(
                    f"{self.BASE_URL}/kpis/{kpi['id']}",
                    json={"actual_value": actual_value}
                )
                return update_response.json() if update_response.status_code == 200 else kpi
            return None
        except Exception as e:
            return None
    
    def seed_all(self):
        """Run the complete seeding process"""
        print("\n" + "=" * 80)
        print("🌱 BRICK BACKEND SEEDER - Real-World Data")
        print("=" * 80)
        
        # Step 1: Login
        print("\n📋 Step 1: Authenticating...")
        try:
            self.login()
        except Exception as e:
            print(f"❌ Login failed: {e}")
            print("Please make sure your backend server is running on http://localhost:8000")
            return None
        
        # Step 2: Create organizations
        print("\n📋 Step 2: Creating Organizations...")
        for org_data in self.organizations:
            org = self.create_organization(org_data)
            if org:
                self.created_orgs.append(org)
            time.sleep(0.3)
        
        print(f"\n✅ Created {len(self.created_orgs)} organizations")
        
        if len(self.created_orgs) == 0:
            print("\n❌ No organizations created. Exiting.")
            return None
        
        # Step 3: Create projects and tasks
        print("\n📋 Step 3: Creating Projects and Tasks...")
        
        for org in self.created_orgs:
            org_name = org["name"]
            org_currency = org["currency"]
            
            # Determine if engineering or NGO
            if "Engineering" in org["industry"] or "Construction" in org["industry"]:
                projects_data = self.engineering_projects
                project_type = "construction"
            else:
                projects_data = self.ngo_projects
                project_type = "ngo"
            
            print(f"\n  🏢 {org_name}:")
            
            for proj_data in projects_data:
                project = self.create_project(org["id"], proj_data, org_currency)
                if not project:
                    continue
                
                self.created_projects.append(project)
                print(f"    📐 Project: {project['title']}")
                print(f"       Budget: {org_currency} {proj_data['budget']:,.0f}")
                
                # Create tasks
                task_count = 0
                for task_data in proj_data["tasks"]:
                    task = self.create_task(project["id"], task_data)
                    if task:
                        self.created_tasks.append(task)
                        task_count += 1
                    time.sleep(0.05)
                
                print(f"       ✅ Created {task_count} tasks")
                
                # Create KPIs
                kpi_templates = self.kpi_templates.get(project_type, self.kpi_templates["ngo"])
                kpi_count = 0
                for kpi_data in kpi_templates:
                    kpi = self.create_kpi(project["id"], kpi_data, project["title"])
                    if kpi:
                        self.created_kpis.append(kpi)
                        kpi_count += 1
                    time.sleep(0.05)
                
                print(f"       📊 Created {kpi_count} KPIs")
                time.sleep(0.2)
        
        # Step 4: Summary
        print("\n" + "=" * 80)
        print("📊 SEEDING COMPLETE SUMMARY")
        print("=" * 80)
        print(f"\n  ✅ Organizations: {len(self.created_orgs)}")
        print(f"  ✅ Projects: {len(self.created_projects)}")
        print(f"  ✅ Tasks: {len(self.created_tasks)}")
        print(f"  ✅ KPIs: {len(self.created_kpis)}")
        
        print("\n📋 Organization Breakdown:")
        for org in self.created_orgs:
            projects_in_org = [p for p in self.created_projects if p["org_id"] == org["id"]]
            tasks_in_org = len([t for t in self.created_tasks if any(p["id"] == t["project_id"] for p in projects_in_org)])
            kpis_in_org = len([k for k in self.created_kpis if any(p["id"] == k["project_id"] for p in projects_in_org)])
            print(f"  • {org['name']}: {len(projects_in_org)} projects, {tasks_in_org} tasks, {kpis_in_org} KPIs")
        
        print("\n" + "=" * 80)
        print("🎉 SEEDING COMPLETE! Real-world data is ready.")
        print("=" * 80)
        
        # Save IDs
        with open("seeded_data.txt", "w") as f:
            f.write("=== SEEDED DATA IDs ===\n\n")
            f.write("ORGANIZATIONS:\n")
            for org in self.created_orgs:
                f.write(f"  {org['name']}: {org['id']}\n")
            
            f.write("\nPROJECTS:\n")
            for project in self.created_projects:
                f.write(f"  {project['title']}: {project['id']}\n")
        
        return {
            "organizations": self.created_orgs,
            "projects": self.created_projects,
            "tasks": self.created_tasks,
            "kpis": self.created_kpis
        }


def main():
    """Main function to run the seeder"""
    seeder = BrickSeeder()
    result = seeder.seed_all()
    
    if result:
        print("\n📌 To use this data in your frontend:")
        if result["organizations"]:
            print(f"  • First Org ID: {result['organizations'][0]['id']}")
            print(f"  • First Org Name: {result['organizations'][0]['name']}")
        if result["projects"]:
            print(f"  • First Project ID: {result['projects'][0]['id']}")
            print(f"  • First Project: {result['projects'][0]['title']}")
    else:
        print("\n❌ Seeding failed. Please check your backend server.")


if __name__ == "__main__":
    main()