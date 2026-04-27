"""
Complete Supabase Seed Script for Save the Children International
Populates all tables with realistic NGO data
"""

import os
import sys
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
from src.models.comment import Comment
from src.models.notification import Notification


def create_tables():
    """Create all tables in Supabase"""
    from src.db.session import Base, engine
    print("Creating tables in Supabase...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!\n")


def seed_save_the_children():
    """Seed Save the Children International complete data"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("SEEDING SAVE THE CHILDREN INTERNATIONAL - NIGERIA")
        print("=" * 80)
        
        # ============================================================
        # STEP 1: CREATE ORGANIZATION
        # ============================================================
        print("\n[1] Creating Organization...")
        org = Organization(
            id=uuid.uuid4(),
            name="Save the Children International - Nigeria",
            industry="NGO / Non-profit",
            currency="USD",
            timezone="Africa/Lagos",
            is_active=True
        )
        db.add(org)
        db.flush()
        print(f"    ✅ Created: {org.name}")
        print(f"       ID: {org.id}")
        
        # ============================================================
        # STEP 2: CREATE USERS (10 Team Members)
        # ============================================================
        print("\n[2] Creating Team Members...")
        users = []
        team_data = [
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
        
        for idx, member in enumerate(team_data):
            user = User(
                id=uuid.uuid4(),
                name=member["name"],
                email=member["email"],
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.flush()
            users.append({"user": user, "role": member["role"]})
            print(f"    ✅ {member['name']} ({member['role']})")
        
        # ============================================================
        # STEP 3: ADD USERS TO ORGANIZATION
        # ============================================================
        print("\n[3] Adding Members to Organization...")
        for u in users:
            org_member = OrgMember(
                id=uuid.uuid4(),
                org_id=org.id,
                user_id=u["user"].id,
                role=u["role"],
                status="active"
            )
            db.add(org_member)
        db.flush()
        print(f"    ✅ Added {len(users)} members to organization")
        
        # ============================================================
        # STEP 4: CREATE 5 NGO PROJECTS
        # ============================================================
        print("\n[4] Creating Projects...")
        
        project_templates = [
            {
                "title": "Emergency Nutrition Response - Northeast Nigeria",
                "description": "Treating acute malnutrition in children under five across Borno, Adamawa and Yobe states. Project includes community-based screening, outpatient therapeutic feeding, and maternal nutrition education.",
                "total_budget": 4250000,
                "status": "active",
                "start_date": datetime.now() - timedelta(days=120),
                "end_date": datetime.now() + timedelta(days=240),
                "actual_spent": 1850000,
                "kpis": [
                    {"name": "Children screened for malnutrition", "target": 25000, "current": 14200, "unit": "children"},
                    {"name": "Children admitted to treatment", "target": 15000, "current": 8750, "unit": "children"},
                    {"name": "Recovery rate", "target": 85, "current": 78, "unit": "%"},
                    {"name": "Default rate", "target": 5, "current": 7, "unit": "%"},
                    {"name": "Mothers reached with nutrition education", "target": 12000, "current": 6800, "unit": "mothers"}
                ]
            },
            {
                "title": "Girls Education Access Project - Kano State",
                "description": "Removing barriers to girls' education through scholarship provision, community sensitization, and school infrastructure improvement. Targeting 10,000 out-of-school girls.",
                "total_budget": 3800000,
                "status": "active",
                "start_date": datetime.now() - timedelta(days=90),
                "end_date": datetime.now() + timedelta(days=270),
                "actual_spent": 1650000,
                "kpis": [
                    {"name": "Girls enrolled in school", "target": 10000, "current": 5200, "unit": "girls"},
                    {"name": "Scholarships distributed", "target": 10000, "current": 5200, "unit": "scholarships"},
                    {"name": "Schools with improved facilities", "target": 50, "current": 28, "unit": "schools"},
                    {"name": "Community sensitization sessions", "target": 200, "current": 98, "unit": "sessions"},
                    {"name": "Girls retention rate after 6 months", "target": 90, "current": 87, "unit": "%"}
                ]
            },
            {
                "title": "Child Protection and Psychosocial Support - IDP Camps",
                "description": "Establishing child-friendly spaces, providing psychosocial support, and reunifying separated children with families in conflict-affected areas.",
                "total_budget": 2950000,
                "status": "active",
                "start_date": datetime.now() - timedelta(days=150),
                "end_date": datetime.now() + timedelta(days=210),
                "actual_spent": 1350000,
                "kpis": [
                    {"name": "Children accessing child-friendly spaces", "target": 20000, "current": 11200, "unit": "children"},
                    {"name": "Psychosocial support sessions conducted", "target": 500, "current": 285, "unit": "sessions"},
                    {"name": "Children reunified with families", "target": 800, "current": 420, "unit": "children"},
                    {"name": "Case workers trained", "target": 120, "current": 78, "unit": "workers"},
                    {"name": "Child protection committees formed", "target": 40, "current": 22, "unit": "committees"}
                ]
            },
            {
                "title": "Maternal and Newborn Health - Adamawa State",
                "description": "Strengthening primary healthcare centers, training midwives, and providing essential maternal and newborn supplies to reduce maternal mortality.",
                "total_budget": 5100000,
                "status": "active",
                "start_date": datetime.now() - timedelta(days=180),
                "end_date": datetime.now() + timedelta(days=180),
                "actual_spent": 2350000,
                "kpis": [
                    {"name": "Women receiving antenatal care", "target": 25000, "current": 13500, "unit": "women"},
                    {"name": "Skilled birth attendance", "target": 85, "current": 72, "unit": "%"},
                    {"name": "Health facilities upgraded", "target": 30, "current": 18, "unit": "facilities"},
                    {"name": "Midwives trained", "target": 150, "current": 85, "unit": "midwives"},
                    {"name": "Newborn screening conducted", "target": 20000, "current": 10800, "unit": "newborns"}
                ]
            },
            {
                "title": "Water, Sanitation and Hygiene (WASH) - Rural Communities",
                "description": "Constructing boreholes, promoting hygiene practices, and establishing community-led total sanitation in 100 rural communities.",
                "total_budget": 3500000,
                "status": "active",
                "start_date": datetime.now() - timedelta(days=100),
                "end_date": datetime.now() + timedelta(days=260),
                "actual_spent": 1550000,
                "kpis": [
                    {"name": "People accessing clean water", "target": 50000, "current": 28500, "unit": "people"},
                    {"name": "Boreholes constructed", "target": 100, "current": 58, "unit": "boreholes"},
                    {"name": "Communities certified open defecation free", "target": 80, "current": 42, "unit": "communities"},
                    {"name": "Handwashing stations installed", "target": 500, "current": 275, "unit": "stations"},
                    {"name": "Hygiene promoters trained", "target": 200, "current": 115, "unit": "promoters"}
                ]
            }
        ]
        
        # Task templates for NGO activities
        task_templates = [
            {"title": "Conduct baseline assessment", "priority": "high", "type": "research", "budget": (40000, 60000), "duration": 30},
            {"title": "Recruit project staff", "priority": "high", "type": "task", "budget": (20000, 35000), "duration": 21},
            {"title": "Train community volunteers", "priority": "high", "type": "task", "budget": (30000, 50000), "duration": 21},
            {"title": "Community mobilization and sensitization", "priority": "high", "type": "task", "budget": (60000, 100000), "duration": 60},
            {"title": "Beneficiary registration and verification", "priority": "high", "type": "task", "budget": (40000, 70000), "duration": 45},
            {"title": "Distribution of supplies and materials", "priority": "high", "type": "task", "budget": (150000, 300000), "duration": 30},
            {"title": "Field monitoring visits", "priority": "medium", "type": "task", "budget": (30000, 50000), "duration": 90},
            {"title": "Prepare quarterly progress report", "priority": "medium", "type": "report", "budget": (15000, 25000), "duration": 14},
            {"title": "Conduct follow-up assessment", "priority": "high", "type": "research", "budget": (35000, 55000), "duration": 30},
            {"title": "Document lessons learned", "priority": "low", "type": "report", "budget": (10000, 20000), "duration": 45},
            {"title": "Submit funding request", "priority": "high", "type": "task", "budget": (5000, 15000), "duration": 14},
            {"title": "Organize stakeholder meeting", "priority": "medium", "type": "task", "budget": (20000, 40000), "duration": 7},
            {"title": "Update project dashboard", "priority": "low", "type": "task", "budget": (10000, 20000), "duration": 180},
            {"title": "Conduct beneficiary satisfaction survey", "priority": "medium", "type": "research", "budget": (25000, 45000), "duration": 21},
            {"title": "Manage budget tracking", "priority": "high", "type": "task", "budget": (15000, 30000), "duration": 180},
            {"title": "Coordinate with local partners", "priority": "medium", "type": "task", "budget": (20000, 40000), "duration": 120},
            {"title": "Provide technical assistance", "priority": "high", "type": "task", "budget": (50000, 80000), "duration": 90},
            {"title": "Organize community feedback sessions", "priority": "medium", "type": "task", "budget": (15000, 30000), "duration": 30},
            {"title": "Document success stories", "priority": "low", "type": "report", "budget": (10000, 20000), "duration": 45},
            {"title": "Procure additional supplies", "priority": "medium", "type": "task", "budget": (100000, 200000), "duration": 21},
            {"title": "Conduct endline evaluation", "priority": "high", "type": "research", "budget": (40000, 60000), "duration": 30},
            {"title": "Prepare final report", "priority": "high", "type": "report", "budget": (30000, 50000), "duration": 30}
        ]
        
        projects = []
        all_tasks = []
        all_expenses = []
        
        for idx, pt in enumerate(project_templates, 1):
            project = Project(
                id=uuid.uuid4(),
                org_id=org.id,
                title=pt["title"],
                description=pt["description"],
                status=pt["status"],
                start_date=pt["start_date"],
                end_date=pt["end_date"],
                total_budget=pt["total_budget"],
                currency="USD",
                created_by=users[0]["user"].id
            )
            db.add(project)
            db.flush()
            projects.append(project)
            
            bur = (pt["actual_spent"] / pt["total_budget"]) * 100
            print(f"\n    📁 Project {idx}: {project.title[:50]}...")
            print(f"       Budget: ${pt['total_budget']:,.0f} | Spent: ${pt['actual_spent']:,.0f} | BUR: {bur:.1f}%")
            
            # Add project members
            for u in users:
                project_member = ProjectMember(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    user_id=u["user"].id,
                    role_id=u["role"]
                )
                db.add(project_member)
            
            # Create tasks (10-15 per project)
            num_tasks = random.randint(10, 15)
            selected_tasks = random.sample(task_templates, min(num_tasks, len(task_templates)))
            task_count = 0
            
            for task_template in selected_tasks:
                due_date = datetime.now() + timedelta(days=random.randint(30, 180))
                progress = random.random()
                
                if progress > 0.8:
                    status = "completed"
                    spent_pct = 0.95
                elif progress > 0.5:
                    status = "in_progress"
                    spent_pct = random.uniform(0.3, 0.7)
                elif progress > 0.3:
                    status = "review"
                    spent_pct = random.uniform(0.6, 0.8)
                else:
                    status = "todo"
                    spent_pct = random.uniform(0, 0.2)
                
                budget = random.randint(task_template["budget"][0], task_template["budget"][1])
                spent = int(budget * spent_pct) if status != "todo" else 0
                
                task = Task(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    title=task_template["title"],
                    description=f"Complete {task_template['title'].lower()} for {project.title}",
                    type=task_template["type"],
                    priority=task_template["priority"],
                    status=status,
                    assigned_to=random.choice([u["user"].id for u in users]) if users else None,
                    due_date=due_date,
                    budget_allocated=budget,
                    total_spent=spent,
                    created_by=users[0]["user"].id
                )
                db.add(task)
                task_count += 1
                all_tasks.append(task)
                
                # Add task assignee
                assignee = TaskAssignee(
                    id=uuid.uuid4(),
                    task_id=task.id,
                    user_id=task.assigned_to if task.assigned_to else users[0]["user"].id,
                    is_supervisor=False
                )
                db.add(assignee)
                
                # Add expense if spent > 0
                if spent > 0:
                    expense = Expense(
                        id=uuid.uuid4(),
                        task_id=task.id,
                        user_id=users[0]["user"].id,
                        amount=spent,
                        payment_method=random.choice(["bank_transfer", "cash", "bank_transfer"]),
                        category=random.choice(["materials", "travel", "labor", "equipment", "training"]),
                        description=f"Expenses for {task_template['title'].lower()}",
                        status="approved",
                        approved_by=users[0]["user"].id,
                        approved_at=datetime.now()
                    )
                    db.add(expense)
                    all_expenses.append(expense)
            
            print(f"       ✅ Created {task_count} tasks with expenses")
            
            # Create KPIs
            kpi_count = 0
            for kpi_template in pt["kpis"]:
                period_start = datetime.now() - timedelta(days=random.randint(30, 90))
                period_end = datetime.now() + timedelta(days=random.randint(30, 180))
                current = kpi_template["current"]
                target = kpi_template["target"]
                kar = (current / target) * 100
                
                # Determine status based on KAR
                if kar >= 100:
                    status = "good"
                elif kar >= 75:
                    status = "satisfactory"
                    status = "warning"
                    status = "critical"
                elif kar >= 50:
                    status = "warning"
                else:
                    status = "critical"
                
                kpi = KPI(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    created_by=users[0]["user"].id,
                    indicator_name=kpi_template["name"],
                    description=f"Track {kpi_template['name'].lower()} for {project.title}",
                    target_value=target,
                    actual_value=current,
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
        # STEP 5: CREATE COMMENTS
        # ============================================================
        print("\n[5] Creating Comments...")
        comment_count = 0
        comment_templates = [
            "Great progress on this task!",
            "Need additional support from the team.",
            "Completed ahead of schedule.",
            "Waiting for approval from the donor.",
            "Community feedback is very positive.",
            "Experiencing delays due to weather.",
            "All beneficiaries have been registered.",
            "Training materials have been distributed.",
            "Monthly report submitted to the coordinator.",
            "Working with local partners on this activity."
        ]
        
        for task in all_tasks[:30]:  # Add comments to first 30 tasks
            num_comments = random.randint(1, 3)
            for _ in range(num_comments):
                comment = Comment(
                    id=uuid.uuid4(),
                    task_id=task.id,
                    user_id=task.assigned_to if task.assigned_to else users[0]["user"].id,
                    body=random.choice(comment_templates),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.add(comment)
                comment_count += 1
        
        print(f"    ✅ Created {comment_count} comments")
        
        # ============================================================
        # STEP 6: CREATE NOTIFICATIONS
        # ============================================================
        print("\n[6] Creating Notifications...")
        notification_count = 0
        notification_templates = [
            ("task_assigned", "New Task Assigned", "You have been assigned a new task"),
            ("task_status_change", "Task Status Updated", "A task status has been changed"),
            ("expense_approved", "Expense Approved", "Your expense has been approved"),
            ("kpi_warning", "KPI Warning", "A KPI is below the target threshold"),
            ("bur_alert", "Budget Alert", "Budget utilization has reached 80%")
        ]
        
        for user_data in users[:5]:  # Notify first 5 users
            num_notifications = random.randint(3, 6)
            for _ in range(num_notifications):
                ntype, title, message = random.choice(notification_templates)
                notification = Notification(
                    id=uuid.uuid4(),
                    user_id=user_data["user"].id,
                    org_id=org.id,
                    type=ntype,
                    title=title,
                    message=message,
                    is_read=random.choice([True, False]),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 14))
                )
                db.add(notification)
                notification_count += 1
        
        print(f"    ✅ Created {notification_count} notifications")
        
        # ============================================================
        # STEP 7: COMMIT ALL CHANGES
        # ============================================================
        db.commit()
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 80)
        print("SEEDING COMPLETE - SUMMARY")
        print("=" * 80)
        
        total_budget = sum(p.total_budget for p in projects)
        total_spent = sum(e.amount for e in all_expenses)
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.status == "completed"])
        in_progress_tasks = len([t for t in all_tasks if t.status == "in_progress"])
        
        print(f"\n🏢 ORGANIZATION:")
        print(f"   Name: {org.name}")
        print(f"   ID: {org.id}")
        print(f"   Team Members: {len(users)}")
        
        print(f"\n📁 PROJECTS:")
        print(f"   Total Projects: {len(projects)}")
        print(f"   Total Budget: ${total_budget:,.0f}")
        print(f"   Total Spent: ${total_spent:,.0f}")
        print(f"   Overall BUR: {(total_spent/total_budget*100):.1f}%")
        
        print(f"\n✅ TASKS:")
        print(f"   Total Tasks: {total_tasks}")
        print(f"   Completed: {completed_tasks}")
        print(f"   In Progress: {in_progress_tasks}")
        print(f"   Completion Rate: {(completed_tasks/total_tasks*100):.1f}%")
        
        print(f"\n💰 FINANCES:")
        print(f"   Total Expenses: {len(all_expenses)}")
        print(f"   Total Amount: ${total_spent:,.0f}")
        
        print(f"\n📊 KPIs:")
        print(f"   Total KPIs: {sum(len(p['kpis']) for p in project_templates)}")
        
        print(f"\n💬 ACTIVITIES:")
        print(f"   Comments: {comment_count}")
        print(f"   Notifications: {notification_count}")
        
        # Project breakdown
        print(f"\n📋 PROJECT BREAKDOWN:")
        for i, project in enumerate(projects):
            project_tasks = [t for t in all_tasks if t.project_id == project.id]
            project_spent = sum(t.total_spent or 0 for t in project_tasks)
            bur = (project_spent / project.total_budget) * 100 if project.total_budget > 0 else 0
            status_icon = "🔴" if bur >= 100 else "🟡" if bur >= 80 else "🟢"
            print(f"   {status_icon} {project.title[:45]}... | BUR: {bur:.1f}% | Tasks: {len(project_tasks)}")
        
        print("\n" + "=" * 80)
        print("🎉 SEEDING COMPLETE! Data is ready for the frontend.")
        print("=" * 80)
        
        # Save IDs to file
        with open("supabase_seeded_data.txt", "w") as f:
            f.write("=== SUPABASE SEEDED DATA IDs ===\n\n")
            f.write(f"ORGANIZATION:\n")
            f.write(f"  Name: {org.name}\n")
            f.write(f"  ID: {org.id}\n\n")
            f.write("PROJECTS:\n")
            for project in projects:
                f.write(f"  {project.title}: {project.id}\n")
        
        print(f"\n💾 Data IDs saved to: supabase_seeded_data.txt")
        
        return {
            "organization": org,
            "projects": projects,
            "tasks": all_tasks,
            "users": users
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
    seed_save_the_children()