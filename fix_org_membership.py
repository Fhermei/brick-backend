"""
Fix organization membership for the user
"""

from src.db.session import SessionLocal
from src.models.organization import OrgMember, Organization
from src.models.user import User
import uuid

db = SessionLocal()

try:
    # Get the user
    user = db.query(User).filter(User.cognito_sub == "f498e478-50e1-7054-38a9-61d2fcdff165").first()
    
    if not user:
        print("User not found!")
        exit()
    
    print(f"Found user: {user.id} - {user.email}")
    
    # Get all organizations
    orgs = db.query(Organization).all()
    print(f"\nFound {len(orgs)} organizations:")
    for org in orgs:
        print(f"  {org.id} - {org.name}")
    
    # Add user as member to each organization
    for org in orgs:
        existing = db.query(OrgMember).filter(
            OrgMember.org_id == org.id,
            OrgMember.user_id == user.id
        ).first()
        
        if existing:
            print(f"\nUser already in {org.name} with role {existing.role}")
            if existing.status != "active":
                existing.status = "active"
                db.commit()
                print(f"  Updated status to active")
        else:
            member = OrgMember(
                id=uuid.uuid4(),
                org_id=org.id,
                user_id=user.id,
                role="owner",
                status="active"
            )
            db.add(member)
            print(f"\nAdded user to {org.name} as owner")
    
    db.commit()
    
    # Verify
    print("\n=== Verification ===")
    memberships = db.query(OrgMember).filter(OrgMember.user_id == user.id).all()
    for m in memberships:
        org = db.query(Organization).filter(Organization.id == m.org_id).first()
        print(f"  {org.name}: {m.role} ({m.status})")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()