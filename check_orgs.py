import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db.session import SessionLocal
from src.models.organization import Organization
from src.models.user import User

db = SessionLocal()

print("=== USERS ===")
users = db.query(User).all()
for u in users:
    print(f"  {u.id} - {u.email} - {u.cognito_sub}")

print("\n=== ORGANIZATIONS ===")
orgs = db.query(Organization).all()
if orgs:
    for o in orgs:
        print(f"  {o.id} - {o.name} - Owner: {o.owner_id}")
else:
    print("  No organizations found!")

db.close()