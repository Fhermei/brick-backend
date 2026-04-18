"""
Run this script to add the current user to the organization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db.session import SessionLocal
from src.models.organization import OrgMember, Organization
from src.models.user import User
import uuid

def add_user_to_organization():
    db = SessionLocal()
    
    try:
        # Get the user by email or by cognito_sub
        user = db.query(User).filter(
            User.email == "oyewoleoluwafemidavid1@gmail.com"
        ).first()
        
        if not user:
            # Try to find by the cognito_sub from logs
            user = db.query(User).filter(
                User.cognito_sub == "f498e478-50e1-7054-38a9-61d2fcdff165"
            ).first()
        
        if not user:
            print("User not found! Please login first to create user record.")
            print("Available users:")
            users = db.query(User).all()
            for u in users:
                print(f"  {u.id} - {u.email} - {u.cognito_sub}")
            return
        
        print(f"Found user: {user.id} - {user.email}")
        
        # Get the organization
        org_id = uuid.UUID("d0cfc4c9-bcd6-4f96-b539-5a4cb8c4501b")
        org = db.query(Organization).filter(Organization.id == org_id).first()
        
        if not org:
            print(f"Organization {org_id} not found!")
            print("Available organizations:")
            orgs = db.query(Organization).all()
            for o in orgs:
                print(f"  {o.id} - {o.name}")
            return
        
        print(f"Found organization: {org.id} - {org.name}")
        
        # Check if already a member
        existing = db.query(OrgMember).filter(
            OrgMember.org_id == org.id,
            OrgMember.user_id == user.id
        ).first()
        
        if existing:
            print(f"User is already a member of {org.name} with role {existing.role}")
            if existing.status == "pending":
                existing.status = "active"
                db.commit()
                print(f"Updated status from pending to active")
        else:
            # Add as owner
            member = OrgMember(
                id=uuid.uuid4(),
                org_id=org.id,
                user_id=user.id,
                role='owner',
                status='active'
            )
            db.add(member)
            db.commit()
            print(f"Successfully added user to {org.name} as owner")
        
        # Verify membership
        verify = db.query(OrgMember).filter(
            OrgMember.org_id == org.id,
            OrgMember.user_id == user.id,
            OrgMember.status == "active"
        ).first()
        
        if verify:
            print(f"\nVerification: User is now an active member of {org.name} with role {verify.role}")
        else:
            print("\nVerification failed: User is not an active member")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_user_to_organization()