"""
Complete Supabase Seed Script for All NGOs
Seeds: International Rescue Committee, CARE International, Oxfam, Plan International, ActionAid
"""

import os
import uuid
import random
from datetime import datetime, timedelta

# Set the DATABASE_URL for Supabase
os.environ['DATABASE_URL'] = 'postgresql://postgres.fsqcwiylxboofkgtvfez:Fatunbi1111.@aws-1-eu-central-1.pooler.supabase.com:5432/postgres'

from src.db.session import SessionLocal
from src.models.user import User
from src.models.organization import Organization, OrgMember
from src.models.project import Project, ProjectMember
from src.models.task import Task, TaskAssignee
from src.models.expense import Expense
from src.models.kpi import KPI


def create_tables():
    """Tables already exist, just verify"""
    print("Tables already created. Proceeding with seeding...")


def seed_all_ngos():
    """Seed all NGO organizations"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("SEEDING ALL NGO ORGANIZATIONS")
        print("=" * 80)
        
        # ============================================================
        # STEP 1: CREATE ADMIN USER (will be owner of all orgs)
        # ============================================================
        print("\n[1] Creating Admin User...")
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@brick.org").first()
        if existing_admin:
            admin = existing_admin
            print(f"    ✅ Admin already exists: {admin.name}")
        else:
            admin = User(
                id=uuid.uuid4(),
                name="System Administrator",
                email="admin@brick.org",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.flush()
            print(f"    ✅ Created Admin: {admin.name} (ID: {admin.id})")
        
        # ============================================================
        # STEP 2: ORGANIZATIONS DATA
        # ============================================================
        print("\n[2] Creating NGO Organizations...")
        
        organizations_data = [
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
        
        organizations = []
        for org_data in organizations_data:
            # Check if organization already exists
            existing_org = db.query(Organization).filter(Organization.name == org_data["name"]).first()
            if existing_org:
                org = existing_org
                print(f"    ⏭️  Already exists: {org.name}")
            else:
                org = Organization(
                    id=uuid.uuid4(),
                    name=org_data["name"],
                    industry=org_data["industry"],
                    currency=org_data["currency"],
                    timezone=org_data["timezone"],
                    owner_id=admin.id,
                    is_active=True
                )
                db.add(org)
                db.flush()
                print(f"    ✅ Created: {org.name}")
            
            organizations.append(org)
            
            # Add admin as owner to organization
            existing_member = db.query(OrgMember).filter(
                OrgMember.org_id == org.id,
                OrgMember.user_id == admin.id
            ).first()
            if not existing_member:
                org_member = OrgMember(
                    id=uuid.uuid4(),
                    org_id=org.id,
                    user_id=admin.id,
                    role="owner",
                    status="active"
                )
                db.add(org_member)
        
        db.flush()
        print(f"\n    Total organizations: {len(organizations)}")
        
        # ============================================================
        # STEP 3: PROJECTS AND TASKS FOR EACH ORGANIZATION
        # ============================================================
        print("\n[3] Creating Projects and Tasks...")
        
        # Project templates for NGOs
        project_templates = [
            {
                "title": "Emergency Food Security Response",
                "description": "Providing emergency food assistance to 10,000 households",
                "budget": 2500000,
                "duration_months": 12,
                "tasks": [
                    {"title": "Rapid needs assessment", "priority": "urgent", "type": "research", "budget": 45000},
                    {"title": "Food distribution planning", "priority": "high", "type": "task", "budget": 25000},
                    {"title": "Procurement of food supplies", "priority": "high", "type": "task", "budget": 200000},
                    {"title": "Beneficiary registration", "priority": "high", "type": "task", "budget": 50000},
                    {"title": "Food distribution execution", "priority": "high", "type": "task", "budget": 150000},
                    {"title": "Post-distribution monitoring", "priority": "medium", "type": "research", "budget": 35000}
                ],
                "kpis": [
                    {"name": "Households reached", "target": 10000, "unit": "households"},
                    {"name": "Food distributed (MT)", "target": 500, "unit": "metric tons"},
                    {"name": "Beneficiary satisfaction", "target": 85, "unit": "%"}
                ]
            },
            {
                "title": "Girls Education Empowerment Program",
                "description": "Supporting 5,000 girls to complete secondary education",
                "budget": 3500000,
                "duration_months": 24,
                "tasks": [
                    {"title": "Community sensitization", "priority": "high", "type": "task", "budget": 60000},
                    {"title": "Scholarship distribution", "priority": "high", "type": "task", "budget": 500000},
                    {"title": "Mentorship program setup", "priority": "medium", "type": "task", "budget": 40000},
                    {"title": "School infrastructure improvement", "priority": "high", "type": "task", "budget": 300000},
                    {"title": "Parent engagement workshops", "priority": "medium", "type": "task", "budget": 35000},
                    {"title": "Learning outcomes assessment", "priority": "medium", "type": "research", "budget": 45000}
                ],
                "kpis": [
                    {"name": "Girls enrolled", "target": 5000, "unit": "girls"},
                    {"name": "School attendance rate", "target": 90, "unit": "%"},
                    {"name": "Grade completion rate", "target": 85, "unit": "%"}
                ]
            },
            {
                "title": "WASH in Schools Project",
                "description": "Providing clean water and sanitation facilities in 50 schools",
                "budget": 1800000,
                "duration_months": 18,
                "tasks": [
                    {"title": "School needs assessment", "priority": "high", "type": "research", "budget": 35000},
                    {"title": "Borehole drilling", "priority": "high", "type": "task", "budget": 250000},
                    {"title": "Latrine construction", "priority": "high", "type": "task", "budget": 200000},
                    {"title": "Handwashing stations installation", "priority": "medium", "type": "task", "budget": 50000},
                    {"title": "Hygiene education training", "priority": "high", "type": "task", "budget": 30000},
                    {"title": "Water quality testing", "priority": "high", "type": "research", "budget": 25000}
                ],
                "kpis": [
                    {"name": "Schools with clean water", "target": 50, "unit": "schools"},
                    {"name": "Students trained in hygiene", "target": 25000, "unit": "students"},
                    {"name": "Latrine coverage", "target": 100, "unit": "%"}
                ]
            },
            {
                "title": "Maternal Health Initiative",
                "description": "Reducing maternal mortality in rural communities",
                "budget": 4200000,
                "duration_months": 36,
                "tasks": [
                    {"title": "Baseline health survey", "priority": "high", "type": "research", "budget": 55000},
                    {"title": "Midwife training program", "priority": "high", "type": "task", "budget": 120000},
                    {"title": "Mobile clinic deployment", "priority": "high", "type": "task", "budget": 350000},
                    {"title": "Birth kit distribution", "priority": "medium", "type": "task", "budget": 80000},
                    {"title": "Emergency referral system", "priority": "high", "type": "task", "budget": 60000},
                    {"title": "Endline evaluation", "priority": "medium", "type": "research", "budget": 50000}
                ],
                "kpis": [
                    {"name": "Maternal mortality reduction", "target": 30, "unit": "%"},
                    {"name": "Skilled birth attendance", "target": 80, "unit": "%"},
                    {"name": "Antenatal care coverage", "target": 85, "unit": "%"}
                ]
            },
            {
                "title": "Child Protection Centers",
                "description": "Establishing safe spaces for vulnerable children",
                "budget": 2200000,
                "duration_months": 24,
                "tasks": [
                    {"title": "Child protection mapping", "priority": "high", "type": "research", "budget": 40000},
                    {"title": "Center construction", "priority": "high", "type": "task", "budget": 350000},
                    {"title": "Social worker recruitment", "priority": "high", "type": "task", "budget": 60000},
                    {"title": "Psychosocial support training", "priority": "high", "type": "task", "budget": 45000},
                    {"title": "Case management system", "priority": "medium", "type": "task", "budget": 35000},
                    {"title": "Community awareness campaign", "priority": "medium", "type": "task", "budget": 50000}
                ],
                "kpis": [
                    {"name": "Children reached", "target": 15000, "unit": "children"},
                    {"name": "Child protection cases handled", "target": 2000, "unit": "cases"},
                    {"name": "Community awareness events", "target": 100, "unit": "events"}
                ]
            }
        ]
        
        all_projects = []
        all_tasks = []
        
        for org in organizations:
            print(f"\n  🏢 {org.name} ({org.currency})")
            
            for idx, pt in enumerate(project_templates, 1):
                # Check if project already exists
                existing_project = db.query(Project).filter(
                    Project.org_id == org.id,
                    Project.title == pt["title"]
                ).first()
                
                if existing_project:
                    print(f"    ⏭️  Already exists: {pt['title']}")
                    continue
                
                start_date = datetime.now() - timedelta(days=random.randint(30, 180))
                end_date = datetime.now() + timedelta(days=pt["duration_months"] * 30)
                
                project = Project(
                    id=uuid.uuid4(),
                    org_id=org.id,
                    title=pt["title"],
                    description=pt["description"],
                    status="active",
                    start_date=start_date,
                    end_date=end_date,
                    total_budget=pt["budget"],
                    currency=org.currency,
                    created_by=admin.id
                )
                db.add(project)
                db.flush()
                all_projects.append(project)
                
                print(f"    📁 Project {idx}: {project.title[:45]}...")
                print(f"       Budget: {org.currency} {pt['budget']:,.0f}")
                
                # Add project members (admin only for simplicity)
                project_member = ProjectMember(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    user_id=admin.id,
                    role_id="owner"
                )
                db.add(project_member)
                
                # Create tasks
                task_count = 0
                for task_template in pt["tasks"]:
                    due_date = datetime.now() + timedelta(days=random.randint(30, 180))
                    status = random.choice(["todo", "in_progress", "review", "completed"])
                    
                    budget = task_template["budget"]
                    spent = budget if status == "completed" else (budget * random.uniform(0.1, 0.5) if status == "in_progress" else 0)
                    
                    task = Task(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        title=task_template["title"],
                        description=f"Complete {task_template['title'].lower()} for {project.title}",
                        type=task_template["type"],
                        priority=task_template["priority"],
                        status=status,
                        assigned_to=admin.id,
                        due_date=due_date,
                        budget_allocated=budget,
                        total_spent=spent,
                        created_by=admin.id
                    )
                    db.add(task)
                    task_count += 1
                    all_tasks.append(task)
                    
                    # Add task assignee
                    assignee = TaskAssignee(
                        id=uuid.uuid4(),
                        task_id=task.id,
                        user_id=admin.id,
                        is_supervisor=False
                    )
                    db.add(assignee)
                    
                    # Add expense if spent > 0
                    if spent > 0:
                        expense = Expense(
                            id=uuid.uuid4(),
                            task_id=task.id,
                            user_id=admin.id,
                            amount=spent,
                            payment_method=random.choice(["bank_transfer", "cash"]),
                            category=random.choice(["materials", "travel", "labor", "equipment"]),
                            description=f"Expenses for {task_template['title'].lower()}",
                            status="approved",
                            approved_by=admin.id,
                            approved_at=datetime.now()
                        )
                        db.add(expense)
                
                print(f"       ✅ Created {task_count} tasks")
                
                # Create KPIs
                kpi_count = 0
                for kpi_template in pt["kpis"]:
                    period_start = datetime.now() - timedelta(days=random.randint(30, 90))
                    period_end = datetime.now() + timedelta(days=random.randint(30, 180))
                    actual = random.randint(int(kpi_template["target"] * 0.3), kpi_template["target"])
                    kar = (actual / kpi_template["target"]) * 100
                    
                    if kar >= 75:
                        status = "satisfactory"
                    elif kar >= 50:
                        status = "warning"
                    else:
                        status = "critical"
                    
                    kpi = KPI(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        created_by=admin.id,
                        indicator_name=kpi_template["name"],
                        description=f"Track {kpi_template['name'].lower()} for {project.title}",
                        target_value=kpi_template["target"],
                        actual_value=actual,
                        kar=kar,
                        status=status,
                        unit=kpi_template["unit"],
                        period_start=period_start,
                        period_end=period_end
                    )
                    db.add(kpi)
                    kpi_count += 1
                
                print(f"       📊 Created {kpi_count} KPIs")
        
        # ============================================================
        # STEP 4: COMMIT ALL CHANGES
        # ============================================================
        db.commit()
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE - SUMMARY")
        print("=" * 80)
        
        total_budget = sum(p.total_budget for p in all_projects)
        total_spent = sum(t.total_spent or 0 for t in all_tasks)
        
        print(f"\n🏢 ORGANIZATIONS:")
        for org in organizations:
            org_projects = [p for p in all_projects if p.org_id == org.id]
            org_tasks = [t for t in all_tasks if any(p.id == t.project_id for p in org_projects)]
            print(f"   • {org.name}: {len(org_projects)} projects, {len(org_tasks)} tasks")
        
        print(f"\n📊 TOTALS:")
        print(f"   Organizations: {len(organizations)}")
        print(f"   Projects: {len(all_projects)}")
        print(f"   Tasks: {len(all_tasks)}")
        print(f"   Total Budget: ${total_budget:,.0f}")
        print(f"   Total Spent: ${total_spent:,.0f}")
        print(f"   Overall BUR: {(total_spent/total_budget*100):.1f}%")
        
        print("\n" + "=" * 80)
        print("🎉 ALL NGOs SEEDED SUCCESSFULLY!")
        print("=" * 80)
        
        # Save IDs to file
        with open("all_ngos_seeded_data.txt", "w") as f:
            f.write("=== ALL NGOs SEEDED DATA IDs ===\n\n")
            f.write("ORGANIZATIONS:\n")
            for org in organizations:
                f.write(f"  {org.name}: {org.id}\n")
            f.write(f"\nPROJECTS:\n")
            for project in all_projects[:10]:
                f.write(f"  {project.title}: {project.id}\n")
            f.write(f"\nTotal Projects: {len(all_projects)}\n")
            f.write(f"Total Tasks: {len(all_tasks)}\n")
        
        print(f"\n💾 Data IDs saved to: all_ngos_seeded_data.txt")
        
        return {
            "organizations": organizations,
            "projects": all_projects,
            "tasks": all_tasks
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_all_ngos()