"""
Realistic NGO Data Seeder for Brick SPMES
Creates one major NGO with 5 projects and 500+ tasks
Includes real-world humanitarian project data
"""

import requests
import random
from datetime import datetime, timedelta
import time
import uuid

class RealisticNGOSystemSeeder:
    """Seeds realistic NGO project data for comprehensive testing"""
    
    def __init__(self):
        self.BASE_URL = "http://localhost:8000/api/v1"
        self.session = requests.Session()
        
        # Main NGO Organization - Save the Children International (Real NGO)
        self.organization = {
            "name": "Save the Children International - Nigeria",
            "industry": "NGO / Non-profit",
            "currency": "USD",
            "timezone": "Africa/Lagos",
            "description": "Leading child rights organization working in 15 Nigerian states"
        }
        
        # ============================================================
        # REAL LIFE NGO PROJECTS WITH COMPREHENSIVE DATA
        # ============================================================
        self.projects = [
            {
                "title": "Emergency Nutrition Response - Northeast Nigeria",
                "description": "Treating acute malnutrition in children under five across Borno, Adamawa and Yobe states. Project includes community-based screening, outpatient therapeutic feeding, and maternal nutrition education.",
                "total_budget": 4250000,
                "currency": "USD",
                "status": "active",
                "start_date_offset_days": -120,
                "end_date_offset_days": 240,
                "beneficiaries_target": 15000,
                "current_beneficiaries": 8750,
                "completion_percentage": 58,
                "kpis": [
                    {"name": "Children screened for malnutrition", "target": 25000, "current": 14200, "unit": "children"},
                    {"name": "Children admitted to treatment", "target": 15000, "current": 8750, "unit": "children"},
                    {"name": "Recovery rate", "target": 85, "current": 78, "unit": "%"},
                    {"name": "Default rate", "target": 5, "current": 7, "unit": "%"},
                    {"name": "Mothers reached with nutrition education", "target": 12000, "current": 6800, "unit": "mothers"}
                ],
                "task_count": 95
            },
            {
                "title": "Girls Education Access Project - Kano State",
                "description": "Removing barriers to girls' education through scholarship provision, community sensitization, and school infrastructure improvement. Targeting 10,000 out-of-school girls.",
                "total_budget": 3800000,
                "currency": "USD",
                "status": "active",
                "start_date_offset_days": -90,
                "end_date_offset_days": 270,
                "beneficiaries_target": 10000,
                "current_beneficiaries": 5200,
                "completion_percentage": 52,
                "kpis": [
                    {"name": "Girls enrolled in school", "target": 10000, "current": 5200, "unit": "girls"},
                    {"name": "Scholarships distributed", "target": 10000, "current": 5200, "unit": "scholarships"},
                    {"name": "Schools with improved facilities", "target": 50, "current": 28, "unit": "schools"},
                    {"name": "Community sensitization sessions", "target": 200, "current": 98, "unit": "sessions"},
                    {"name": "Girls retention rate after 6 months", "target": 90, "current": 87, "unit": "%"}
                ],
                "task_count": 88
            },
            {
                "title": "Child Protection and Psychosocial Support - IDP Camps",
                "description": "Establishing child-friendly spaces, providing psychosocial support, and reunifying separated children with families in conflict-affected areas.",
                "total_budget": 2950000,
                "currency": "USD",
                "status": "active",
                "start_date_offset_days": -150,
                "end_date_offset_days": 210,
                "beneficiaries_target": 20000,
                "current_beneficiaries": 11200,
                "completion_percentage": 56,
                "kpis": [
                    {"name": "Children accessing child-friendly spaces", "target": 20000, "current": 11200, "unit": "children"},
                    {"name": "Psychosocial support sessions conducted", "target": 500, "current": 285, "unit": "sessions"},
                    {"name": "Children reunified with families", "target": 800, "current": 420, "unit": "children"},
                    {"name": "Case workers trained", "target": 120, "current": 78, "unit": "workers"},
                    {"name": "Child protection committees formed", "target": 40, "current": 22, "unit": "committees"}
                ],
                "task_count": 92
            },
            {
                "title": "Maternal and Newborn Health - Adamawa State",
                "description": "Strengthening primary healthcare centers, training midwives, and providing essential maternal and newborn supplies to reduce maternal mortality.",
                "total_budget": 5100000,
                "currency": "USD",
                "status": "active",
                "start_date_offset_days": -180,
                "end_date_offset_days": 180,
                "beneficiaries_target": 25000,
                "current_beneficiaries": 13500,
                "completion_percentage": 54,
                "kpis": [
                    {"name": "Women receiving antenatal care", "target": 25000, "current": 13500, "unit": "women"},
                    {"name": "Skilled birth attendance", "target": 85, "current": 72, "unit": "%"},
                    {"name": "Health facilities upgraded", "target": 30, "current": 18, "unit": "facilities"},
                    {"name": "Midwives trained", "target": 150, "current": 85, "unit": "midwives"},
                    {"name": "Newborn screening conducted", "target": 20000, "current": 10800, "unit": "newborns"}
                ],
                "task_count": 105
            },
            {
                "title": "Water, Sanitation and Hygiene (WASH) - Rural Communities",
                "description": "Constructing boreholes, promoting hygiene practices, and establishing community-led total sanitation in 100 rural communities.",
                "total_budget": 3500000,
                "currency": "USD",
                "status": "active",
                "start_date_offset_days": -100,
                "end_date_offset_days": 260,
                "beneficiaries_target": 50000,
                "current_beneficiaries": 28500,
                "completion_percentage": 57,
                "kpis": [
                    {"name": "People accessing clean water", "target": 50000, "current": 28500, "unit": "people"},
                    {"name": "Boreholes constructed", "target": 100, "current": 58, "unit": "boreholes"},
                    {"name": "Communities certified open defecation free", "target": 80, "current": 42, "unit": "communities"},
                    {"name": "Handwashing stations installed", "target": 500, "current": 275, "unit": "stations"},
                    {"name": "Hygiene promoters trained", "target": 200, "current": 115, "unit": "promoters"}
                ],
                "task_count": 98
            }
        ]
        
        # Task templates with realistic NGO activities
        self.task_templates = {
            "planning": [
                {"title": "Conduct baseline assessment", "type": "research", "priority": "high", "duration_days": 30, "budget_range": (50000, 80000)},
                {"title": "Develop project implementation plan", "type": "task", "priority": "high", "duration_days": 14, "budget_range": (20000, 35000)},
                {"title": "Recruit project staff", "type": "task", "priority": "high", "duration_days": 21, "budget_range": (15000, 25000)},
                {"title": "Stakeholder mapping and engagement", "type": "task", "priority": "medium", "duration_days": 14, "budget_range": (10000, 20000)},
                {"title": "Procure project equipment", "type": "task", "priority": "high", "duration_days": 28, "budget_range": (100000, 200000)},
                {"title": "Train community volunteers", "type": "task", "priority": "high", "duration_days": 21, "budget_range": (30000, 50000)},
                {"title": "Develop monitoring framework", "type": "task", "priority": "medium", "duration_days": 14, "budget_range": (15000, 25000)}
            ],
            "implementation": [
                {"title": "Community mobilization and sensitization", "type": "task", "priority": "high", "duration_days": 60, "budget_range": (80000, 120000)},
                {"title": "Beneficiary registration and verification", "type": "task", "priority": "high", "duration_days": 45, "budget_range": (50000, 80000)},
                {"title": "Distribution of supplies and materials", "type": "task", "priority": "high", "duration_days": 30, "budget_range": (200000, 500000)},
                {"title": "Conduct training workshops", "type": "task", "priority": "high", "duration_days": 28, "budget_range": (60000, 100000)},
                {"title": "Field monitoring visits", "type": "task", "priority": "medium", "duration_days": 90, "budget_range": (40000, 60000)},
                {"title": "Coordinate with local partners", "type": "task", "priority": "medium", "duration_days": 120, "budget_range": (30000, 50000)},
                {"title": "Provide technical assistance", "type": "task", "priority": "high", "duration_days": 90, "budget_range": (70000, 100000)},
                {"title": "Organize community feedback sessions", "type": "task", "priority": "medium", "duration_days": 30, "budget_range": (20000, 40000)},
                {"title": "Document success stories", "type": "task", "priority": "low", "duration_days": 45, "budget_range": (10000, 20000)},
                {"title": "Procure additional supplies", "type": "task", "priority": "medium", "duration_days": 21, "budget_range": (150000, 250000)},
                {"title": "Conduct follow-up assessments", "type": "task", "priority": "high", "duration_days": 30, "budget_range": (40000, 60000)},
                {"title": "Manage beneficiary complaints", "type": "task", "priority": "medium", "duration_days": 120, "budget_range": (20000, 30000)}
            ],
            "monitoring": [
                {"title": "Collect monthly performance data", "type": "task", "priority": "high", "duration_days": 180, "budget_range": (50000, 80000)},
                {"title": "Update project dashboard", "type": "task", "priority": "medium", "duration_days": 180, "budget_range": (20000, 30000)},
                {"title": "Prepare quarterly progress report", "type": "report", "priority": "high", "duration_days": 14, "budget_range": (15000, 25000)},
                {"title": "Conduct beneficiary satisfaction survey", "type": "research", "priority": "high", "duration_days": 21, "budget_range": (30000, 50000)},
                {"title": "Track budget utilization", "type": "task", "priority": "high", "duration_days": 180, "budget_range": (25000, 40000)},
                {"title": "Document lessons learned", "type": "report", "priority": "medium", "duration_days": 30, "budget_range": (15000, 25000)},
                {"title": "Conduct internal audit", "type": "task", "priority": "high", "duration_days": 14, "budget_range": (40000, 60000)},
                {"title": "Update risk register", "type": "task", "priority": "medium", "duration_days": 60, "budget_range": (10000, 20000)},
                {"title": "Prepare donor financial report", "type": "report", "priority": "high", "duration_days": 14, "budget_range": (20000, 30000)},
                {"title": "Review project indicators", "type": "task", "priority": "medium", "duration_days": 21, "budget_range": (15000, 25000)}
            ],
            "finance": [
                {"title": "Process beneficiary payments", "type": "task", "priority": "high", "duration_days": 90, "budget_range": (10000, 20000)},
                {"title": "Reconcile project expenditures", "type": "task", "priority": "high", "duration_days": 30, "budget_range": (15000, 25000)},
                {"title": "Submit advance requests", "type": "task", "priority": "medium", "duration_days": 180, "budget_range": (5000, 10000)},
                {"title": "Review partner financial reports", "type": "task", "priority": "medium", "duration_days": 60, "budget_range": (20000, 30000)},
                {"title": "Conduct budget realignment", "type": "task", "priority": "high", "duration_days": 14, "budget_range": (10000, 20000)},
                {"title": "Process staff payroll", "type": "task", "priority": "high", "duration_days": 180, "budget_range": (5000, 10000)},
                {"title": "Track exchange rate fluctuations", "type": "task", "priority": "low", "duration_days": 180, "budget_range": (5000, 10000)},
                {"title": "Prepare budget variance analysis", "type": "report", "priority": "high", "duration_days": 21, "budget_range": (15000, 25000)}
            ],
            "reporting": [
                {"title": "Compile monthly field reports", "type": "report", "priority": "high", "duration_days": 180, "budget_range": (20000, 30000)},
                {"title": "Draft donor narrative report", "type": "report", "priority": "high", "duration_days": 21, "budget_range": (25000, 40000)},
                {"title": "Prepare end-of-project evaluation", "type": "report", "priority": "high", "duration_days": 30, "budget_range": (50000, 80000)},
                {"title": "Document case studies", "type": "report", "priority": "medium", "duration_days": 45, "budget_range": (15000, 25000)},
                {"title": "Update online project portal", "type": "task", "priority": "low", "duration_days": 180, "budget_range": (10000, 20000)},
                {"title": "Prepare communication materials", "type": "task", "priority": "medium", "duration_days": 30, "budget_range": (20000, 30000)},
                {"title": "Draft policy brief", "type": "report", "priority": "medium", "duration_days": 21, "budget_range": (15000, 25000)},
                {"title": "Final project report", "type": "report", "priority": "high", "duration_days": 30, "budget_range": (40000, 60000)}
            ],
            "supply_chain": [
                {"title": "Procure medical supplies", "type": "task", "priority": "high", "duration_days": 30, "budget_range": (300000, 500000)},
                {"title": "Manage warehouse inventory", "type": "task", "priority": "high", "duration_days": 180, "budget_range": (50000, 80000)},
                {"title": "Coordinate logistics for distribution", "type": "task", "priority": "high", "duration_days": 90, "budget_range": (80000, 120000)},
                {"title": "Conduct supplier prequalification", "type": "task", "priority": "medium", "duration_days": 30, "budget_range": (20000, 30000)},
                {"title": "Negotiate contracts with vendors", "type": "task", "priority": "high", "duration_days": 21, "budget_range": (15000, 25000)},
                {"title": "Monitor delivery schedules", "type": "task", "priority": "medium", "duration_days": 180, "budget_range": (30000, 50000)},
                {"title": "Conduct quality checks on supplies", "type": "task", "priority": "high", "duration_days": 60, "budget_range": (40000, 60000)},
                {"title": "Manage fleet and vehicles", "type": "task", "priority": "medium", "duration_days": 180, "budget_range": (60000, 100000)}
            ]
        }
        
        # Team members for the organization
        self.team_members = [
            {"name": "Dr. Aisha Mohammed", "email": "aisha.mohammed@savethechildren.org", "role": "owner"},
            {"name": "Ibrahim Bello", "email": "ibrahim.bello@savethechildren.org", "role": "admin"},
            {"name": "Fatima Usman", "email": "fatima.usman@savethechildren.org", "role": "manager"},
            {"name": "Samuel Okonkwo", "email": "samuel.okonkwo@savethechildren.org", "role": "manager"},
            {"name": "Grace Emmanuel", "email": "grace.emmanuel@savethechildren.org", "role": "member"},
            {"name": "James Nwachukwu", "email": "james.nwachukwu@savethechildren.org", "role": "member"},
            {"name": "Patience Adamu", "email": "patience.adamu@savethechildren.org", "role": "member"},
            {"name": "Daniel Okafor", "email": "daniel.okafor@savethechildren.org", "role": "member"},
            {"name": "Esther Ogunleye", "email": "esther.ogunleye@savethechildren.org", "role": "member"},
            {"name": "Emmanuel Okafor", "email": "emmanuel.okafor@savethechildren.org", "role": "viewer"}
        ]
    
    def login(self):
        """Authenticate and get session"""
        login_data = {
            "email": "oyewoleoluwafemidavid1@gmail.com",
            "password": "Fatunbi11."
        }
        
        self.session.cookies.clear()
        
        response = self.session.post(f"{self.BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.status_code}")
        
        print("Authenticated successfully")
        return True
    
    def create_organization(self):
        """Create the main NGO organization"""
        response = self.session.post(f"{self.BASE_URL}/organizations/", json=self.organization)
        if response.status_code == 201:
            org = response.json()
            print(f"Created organization: {org['name']}")
            return org
        else:
            print(f"Failed to create organization: {response.status_code}")
            return None
    
    def invite_team_members(self, org_id):
        """Invite all team members to the organization"""
        invited = []
        for member in self.team_members:
            invite_data = {
                "email": member["email"],
                "role_name": member["role"]
            }
            response = self.session.post(
                f"{self.BASE_URL}/team/invite?org_id={org_id}",
                json=invite_data
            )
            if response.status_code == 201:
                invited.append(member["name"])
                print(f"  Invited: {member['name']} ({member['role']})")
            time.sleep(0.3)
        return invited
    
    def create_project(self, org_id, project_data):
        """Create a project within the organization"""
        start_date = (datetime.now() + timedelta(days=project_data["start_date_offset_days"])).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=project_data["end_date_offset_days"])).strftime("%Y-%m-%d")
        
        payload = {
            "title": project_data["title"],
            "description": project_data["description"],
            "status": project_data["status"],
            "start_date": start_date,
            "end_date": end_date,
            "total_budget": project_data["total_budget"],
            "currency": project_data["currency"]
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/projects?org_id={org_id}",
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        return None
    
    def create_task_with_expense(self, project_id, task_template, days_elapsed):
        """Create a task and add expenses based on completion status"""
        due_date = datetime.now() + timedelta(days=task_template["duration_days"])
        budget = random.randint(*task_template["budget_range"])
        
        # Determine status based on due date and elapsed days
        if days_elapsed > task_template["duration_days"]:
            status = random.choice(["completed", "completed", "completed", "completed", "blocked"])
        elif days_elapsed > task_template["duration_days"] * 0.7:
            status = random.choice(["to_be_tested", "review", "in_progress"])
        elif days_elapsed > task_template["duration_days"] * 0.3:
            status = random.choice(["in_progress", "in_progress", "review"])
        else:
            status = random.choice(["todo", "todo", "in_progress"])
        
        # Calculate spent amount based on completion
        if status == "completed":
            spent = budget
        elif status == "in_progress":
            spent = int(budget * random.uniform(0.3, 0.7))
        elif status == "review" or status == "to_be_tested":
            spent = int(budget * random.uniform(0.7, 0.9))
        else:
            spent = int(budget * random.uniform(0, 0.2))
        
        task_payload = {
            "title": task_template["title"],
            "description": f"Complete {task_template['title'].lower()} for the project as per work plan",
            "type": task_template["type"],
            "priority": task_template["priority"],
            "status": status,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "budget_allocated": budget
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/tasks?project_id={project_id}",
            json=task_payload
        )
        
        if response.status_code == 201:
            task = response.json()
            
            # Add expense if amount spent > 0
            if spent > 0:
                expense_data = {
                    "amount": spent,
                    "payment_method": random.choice(["bank_transfer", "cash", "bank_transfer", "card"]),
                    "category": random.choice(["materials", "travel", "labor", "equipment", "training"]),
                    "description": f"Expenses for {task_template['title'].lower()}"
                }
                self.session.post(
                    f"{self.BASE_URL}/expenses?task_id={task['id']}",
                    json=expense_data
                )
            
            return task
        return None
    
    def create_kpi(self, project_id, kpi_data, project_title):
        """Create KPI for a project with realistic values"""
        period_start = (datetime.now() - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d")
        period_end = (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d")
        
        payload = {
            "indicator_name": kpi_data["name"],
            "description": f"Track {kpi_data['name'].lower()} for {project_title}",
            "target_value": kpi_data["target"],
            "unit": kpi_data["unit"],
            "period_start": period_start,
            "period_end": period_end
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/kpis?project_id={project_id}",
            json=payload
        )
        
        if response.status_code == 201:
            kpi = response.json()
            # Update actual value
            update_response = self.session.patch(
                f"{self.BASE_URL}/kpis/{kpi['id']}",
                json={"actual_value": kpi_data["current"]}
            )
            return update_response.json() if update_response.status_code == 200 else kpi
        return None
    
    def seed_all(self):
        """Run complete seeding process"""
        print("\n" + "=" * 80)
        print("BRICK SPMES - REALISTIC NGO DATA SEEDER")
        print("Save the Children International - Nigeria")
        print("=" * 80)
        
        # Step 1: Login
        print("\nStep 1: Authenticating...")
        self.login()
        
        # Step 2: Create Organization
        print("\nStep 2: Creating Organization...")
        org = self.create_organization()
        if not org:
            print("Failed to create organization. Exiting.")
            return None
        org_id = org["id"]
        
        # Step 3: Invite Team Members
        print("\nStep 3: Inviting Team Members...")
        invited = self.invite_team_members(org_id)
        print(f"Invited {len(invited)} team members")
        
        # Step 4: Create Projects with Tasks
        print("\nStep 4: Creating Projects and Tasks...")
        created_projects = []
        all_tasks = []
        all_expenses = []
        
        for idx, project_template in enumerate(self.projects, 1):
            print(f"\n  Project {idx}: {project_template['title']}")
            
            project = self.create_project(org_id, project_template)
            if not project:
                print(f"    Failed to create project")
                continue
            
            created_projects.append(project)
            print(f"    Created: {project['title']}")
            print(f"    Budget: USD {project_template['total_budget']:,.0f}")
            
            # Calculate days elapsed for the project
            start_date = datetime.now() + timedelta(days=project_template["start_date_offset_days"])
            days_elapsed = max(0, (datetime.now() - start_date).days)
            
            # Generate tasks from templates
            tasks_created = 0
            task_categories = ["planning", "implementation", "monitoring", "finance", "reporting", "supply_chain"]
            
            # Distribute tasks across categories
            tasks_per_category = project_template["task_count"] // len(task_categories)
            
            for category in task_categories:
                templates = self.task_templates.get(category, [])
                num_tasks = min(tasks_per_category, len(templates))
                selected_templates = random.sample(templates, min(num_tasks, len(templates)))
                
                for task_template in selected_templates:
                    task = self.create_task_with_expense(project["id"], task_template, days_elapsed)
                    if task:
                        tasks_created += 1
                        all_tasks.append(task)
                    time.sleep(0.05)
            
            # Add remaining tasks randomly
            remaining = project_template["task_count"] - tasks_created
            all_templates = []
            for cat in task_categories:
                all_templates.extend(self.task_templates.get(cat, []))
            
            for _ in range(remaining):
                task_template = random.choice(all_templates)
                task = self.create_task_with_expense(project["id"], task_template, days_elapsed)
                if task:
                    tasks_created += 1
                    all_tasks.append(task)
                time.sleep(0.05)
            
            print(f"    Created {tasks_created} tasks with expenses")
            
            # Create KPIs for the project
            kpis_created = 0
            for kpi_template in project_template["kpis"]:
                kpi = self.create_kpi(project["id"], kpi_template, project["title"])
                if kpi:
                    kpis_created += 1
                time.sleep(0.05)
            
            print(f"    Created {kpis_created} KPIs")
            print(f"    Beneficiaries: {project_template['current_beneficiaries']:,} / {project_template['beneficiaries_target']:,} ({project_template['completion_percentage']}%)")
        
        # Step 5: Calculate Summary Statistics
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE - SUMMARY")
        print("=" * 80)
        
        total_budget = sum(p["total_budget"] for p in self.projects)
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.get("status") == "completed"])
        in_progress_tasks = len([t for t in all_tasks if t.get("status") == "in_progress"])
        
        print(f"\nOrganization: Save the Children International - Nigeria")
        print(f"Organization ID: {org_id}")
        print(f"\nProjects Created: {len(created_projects)}")
        print(f"Total Project Budget: USD {total_budget:,.0f}")
        print(f"\nTasks Created: {total_tasks}")
        print(f"  - Completed: {completed_tasks}")
        print(f"  - In Progress: {in_progress_tasks}")
        print(f"  - Other: {total_tasks - completed_tasks - in_progress_tasks}")
        print(f"\nTeam Members Invited: {len(invited)}")
        
        # Calculate BUR for each project
        print("\nProject Budget Utilization (BUR):")
        for project in created_projects:
            project_tasks = [t for t in all_tasks if t.get("project_id") == project["id"]]
            total_spent = sum(t.get("total_spent", 0) for t in project_tasks)
            bur = (total_spent / project["total_budget"]) * 100 if project["total_budget"] > 0 else 0
            status = "Critical" if bur >= 100 else "Alert" if bur >= 80 else "OK"
            print(f"  - {project['title'][:40]}: {bur:.1f}% ({status})")
        
        # Save IDs to file
        with open("seeded_ngo_data.txt", "w") as f:
            f.write("=== SAVED THE CHILDREN INTERNATIONAL - SEEDED DATA ===\n\n")
            f.write(f"Organization ID: {org_id}\n\n")
            f.write("PROJECTS:\n")
            for project in created_projects:
                f.write(f"  {project['title']}: {project['id']}\n")
            f.write(f"\nTotal Projects: {len(created_projects)}\n")
            f.write(f"Total Tasks: {total_tasks}\n")
        
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE!")
        print(f"Data saved to: seeded_ngo_data.txt")
        print("=" * 80)
        
        return {
            "organization": org,
            "projects": created_projects,
            "tasks": all_tasks,
            "team_members": invited
        }

if __name__ == "__main__":
    seeder = RealisticNGOSystemSeeder()
    result = seeder.seed_all()
    
    if result:
        print("\nTo use this data in your frontend:")
        print(f"  Organization ID: {result['organization']['id']}")
        print(f"  Organization Name: {result['organization']['name']}")
        if result['projects']:
            print(f"  First Project ID: {result['projects'][0]['id']}")
            print(f"  First Project: {result['projects'][0]['title']}")
        if result['tasks']:
            print(f"  Total Tasks Available: {len(result['tasks'])}")