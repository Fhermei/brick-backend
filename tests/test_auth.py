"""
Unit tests for authentication endpoints
"""

import pytest
import requests
from tests.conftest import BASE_URL, TEST_EMAIL, TEST_PASSWORD


class TestAuthentication:
    """Test authentication and user management"""
    
    def test_health_check(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_login_success(self, auth_session):
        """Test successful login with valid credentials"""
        assert auth_session.cookies.get("access_token") is not None
        assert auth_session.cookies.get("refresh_token") is not None
    
    def test_login_wrong_password(self):
        """Test login with incorrect password - should fail"""
        login_data = {"email": TEST_EMAIL, "password": "WrongPassword123"}
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_get_current_user(self, auth_session):
        """Test retrieving current user profile"""
        response = auth_session.get(f"{BASE_URL}/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == TEST_EMAIL
        assert "id" in response.json()
        assert "name" in response.json()
    
    def test_get_current_user_unauthenticated(self):
        """Test accessing protected endpoint without auth - should fail"""
        response = requests.get(f"{BASE_URL}/auth/me")
        assert response.status_code == 401
    
    def test_logout(self, auth_session):
        """Test logout functionality"""
        response = auth_session.post(f"{BASE_URL}/auth/logout")
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()


class TestOrganizations:
    """Test organization CRUD operations"""
    
    def test_list_organizations(self, auth_session):
        """Test listing user's organizations"""
        response = auth_session.get(f"{BASE_URL}/organizations/mine")
        assert response.status_code == 200
        assert "organizations" in response.json()
        assert isinstance(response.json()["organizations"], list)
    
    def test_create_organization(self, auth_session):
        """Test creating a new organization"""
        import uuid
        org_data = {
            "name": f"Test NGO {uuid.uuid4().hex[:8]}",
            "industry": "NGO / Non-profit",
            "currency": "USD",
            "timezone": "Africa/Lagos"
        }
        response = auth_session.post(f"{BASE_URL}/organizations/", json=org_data)
        assert response.status_code == 201
        assert response.json()["name"] == org_data["name"]
        assert response.json()["member_count"] >= 1
        
        # Clean up - delete the test organization
        org_id = response.json()["id"]
        delete_response = auth_session.delete(f"{BASE_URL}/organizations/{org_id}")
        assert delete_response.status_code == 200
    
    def test_get_organization(self, auth_session, test_org):
        """Test retrieving a single organization"""
        response = auth_session.get(f"{BASE_URL}/organizations/{test_org['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_org["id"]
    
    def test_update_organization(self, auth_session, test_org):
        """Test updating organization details"""
        update_data = {"name": f"Updated NGO {test_org['name']}"}
        response = auth_session.patch(
            f"{BASE_URL}/organizations/{test_org['id']}",
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]

class TestProjects:
    """Test project CRUD operations"""
    
    def test_create_project(self, auth_session, test_org):
        """Test creating a new project"""
        import uuid
        project_data = {
            "title": f"Clean Water Initiative {uuid.uuid4().hex[:8]}",
            "description": "Providing clean water to rural communities",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 2500000,
            "currency": "USD"
        }
        response = auth_session.post(
            f"{BASE_URL}/projects?org_id={test_org['id']}",
            json=project_data
        )
        assert response.status_code == 201
        assert response.json()["title"] == project_data["title"]
        assert float(response.json()["total_budget"]) == project_data["total_budget"]
    
    def test_list_projects(self, auth_session, test_org):
        """Test listing all projects"""
        response = auth_session.get(f"{BASE_URL}/projects?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "projects" in response.json()
        assert isinstance(response.json()["projects"], list)
    
    def test_get_project(self, auth_session, test_project):
        """Test retrieving a single project"""
        response = auth_session.get(f"{BASE_URL}/projects/{test_project['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_project["id"]
    
    def test_update_project(self, auth_session, test_project):
        """Test updating project details"""
        update_data = {"title": "Updated Water Sanitation Project"}
        response = auth_session.patch(
            f"{BASE_URL}/projects/{test_project['id']}",
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]
    
    def test_delete_project(self, auth_session, test_org):
        """Test deleting (archiving) a project"""
        import uuid
        project_data = {
            "title": f"Project to Delete {uuid.uuid4().hex[:8]}",
            "description": "Temporary project",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_budget": 100000,
            "currency": "USD"
        }
        create_response = auth_session.post(
            f"{BASE_URL}/projects?org_id={test_org['id']}",
            json=project_data
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]
        
        delete_response = auth_session.delete(f"{BASE_URL}/projects/{project_id}")
        assert delete_response.status_code == 200


class TestTasks:
    """Test task CRUD operations"""
    
    def test_create_task(self, auth_session, test_project):
        """Test creating a new task"""
        import uuid
        task_data = {
            "title": f"Conduct beneficiary survey {uuid.uuid4().hex[:8]}",
            "description": "Survey 200 households",
            "type": "research",
            "priority": "high",
            "due_date": "2026-07-31",
            "budget_allocated": 250000
        }
        response = auth_session.post(
            f"{BASE_URL}/tasks?project_id={test_project['id']}",
            json=task_data
        )
        assert response.status_code == 201
        assert response.json()["title"] == task_data["title"]
    
    def test_list_tasks(self, auth_session, test_org):
        """Test listing all tasks"""
        response = auth_session.get(f"{BASE_URL}/tasks?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "tasks" in response.json()
    
    def test_get_task(self, auth_session, test_task):
        """Test retrieving a single task"""
        response = auth_session.get(f"{BASE_URL}/tasks/{test_task['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == test_task["id"]
    
    def test_update_task_status(self, auth_session, test_task):
        """Test updating task status"""
        status_data = {"status": "in_progress"}
        response = auth_session.patch(
            f"{BASE_URL}/tasks/{test_task['id']}/status",
            json=status_data
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"


class TestKPIs:
    """Test KPI CRUD operations"""
    
    def test_create_kpi(self, auth_session, test_project):
        """Test creating a new KPI"""
        import uuid
        kpi_data = {
            "indicator_name": f"Beneficiary Reach {uuid.uuid4().hex[:8]}",
            "description": "Number of people reached",
            "target_value": 10000,
            "unit": "people",
            "period_start": "2026-01-01",
            "period_end": "2026-12-31"
        }
        response = auth_session.post(
            f"{BASE_URL}/kpis?project_id={test_project['id']}",
            json=kpi_data
        )
        assert response.status_code == 201
        assert response.json()["indicator_name"] == kpi_data["indicator_name"]
    
    def test_list_kpis(self, auth_session, test_project):
        """Test listing KPIs for a project"""
        response = auth_session.get(f"{BASE_URL}/kpis?project_id={test_project['id']}")
        assert response.status_code == 200
        assert "kpis" in response.json()


class TestBudget:
    """Test budget and expense tracking"""
    
    def test_get_budget_summary(self, auth_session, test_org):
        """Test retrieving budget summary"""
        response = auth_session.get(f"{BASE_URL}/budget/summary?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "total_budget" in response.json()
        assert "total_spent" in response.json()
        assert "bur" in response.json()
    
    def test_get_project_budgets(self, auth_session, test_org):
        """Test retrieving all project budgets"""
        response = auth_session.get(f"{BASE_URL}/budget/projects?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "projects" in response.json()
    
    def test_submit_expense(self, auth_session, test_task):
        """Test submitting an expense"""
        expense_data = {
            "amount": 50000,
            "payment_method": "bank_transfer",
            "category": "travel",
            "description": "Field visit to beneficiary communities"
        }
        response = auth_session.post(
            f"{BASE_URL}/expenses?task_id={test_task['id']}",
            json=expense_data
        )
        assert response.status_code == 201
        assert response.json()["status"] == "approved"
        assert float(response.json()["amount"]) == expense_data["amount"]


class TestDashboard:
    """Test dashboard endpoints"""
    
    def test_dashboard_stats(self, auth_session, test_org):
        """Test retrieving dashboard statistics"""
        response = auth_session.get(f"{BASE_URL}/dashboard/stats?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "task_stats" in response.json()
        assert "budget_stats" in response.json()
        assert "kpi_stats" in response.json()
    
    def test_recent_projects(self, auth_session, test_org):
        """Test retrieving recent projects"""
        response = auth_session.get(
            f"{BASE_URL}/dashboard/recent-projects?org_id={test_org['id']}&limit=5"
        )
        assert response.status_code == 200
        assert "projects" in response.json()
    
    def test_recent_tasks(self, auth_session, test_org):
        """Test retrieving recent tasks"""
        response = auth_session.get(
            f"{BASE_URL}/dashboard/recent-tasks?org_id={test_org['id']}&limit=5"
        )
        assert response.status_code == 200
        assert "tasks" in response.json()


class TestTeam:
    """Test team management"""
    
    def test_list_team_members(self, auth_session, test_org):
        """Test listing team members"""
        response = auth_session.get(f"{BASE_URL}/team?org_id={test_org['id']}")
        assert response.status_code == 200
        assert "members" in response.json()
    
    def test_invite_member(self, auth_session, test_org):
        """Test inviting a team member"""
        invite_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "role_name": "member"
        }
        response = auth_session.post(
            f"{BASE_URL}/team/invite?org_id={test_org['id']}",
            json=invite_data
        )
        assert response.status_code == 201
        assert "sent" in response.json()["message"].lower()


class TestReports:
    """Test report generation"""
    
    def test_generate_organization_report(self, auth_session, test_org):
        """Test generating organization report"""
        report_data = {
            "type": "organization",
            "org_id": test_org["id"],
            "date_from": None,
            "date_to": None
        }
        response = auth_session.post(
            f"{BASE_URL}/reports/generate",
            json=report_data
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"