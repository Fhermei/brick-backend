"""
Complete Database Reset Script for Supabase
Deletes all tables and recreates them with fresh schema
"""

import os
import sys

# Set the DATABASE_URL for Supabase
os.environ['DATABASE_URL'] = 'postgresql://postgres.fsqcwiylxboofkgtvfez:Fatunbi1111.@aws-1-eu-central-1.pooler.supabase.com:5432/postgres'

from src.db.session import Base, engine
from src.models import *

def drop_all_tables():
    """Drop all existing tables"""
    print("=" * 60)
    print("DROPPING ALL TABLES...")
    print("=" * 60)
    
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise

def create_all_tables():
    """Create all tables fresh"""
    print("\n" + "=" * 60)
    print("CREATING FRESH TABLES...")
    print("=" * 60)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List all created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Tables created ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

def verify_connection():
    """Verify database connection"""
    print("\n" + "=" * 60)
    print("VERIFYING DATABASE CONNECTION...")
    print("=" * 60)
    
    try:
        connection = engine.connect()
        print("✅ Database connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SUPABASE DATABASE RESET TOOL")
    print("=" * 60)
    print("\n⚠️  WARNING: This will DELETE ALL data in your database!")
    print("⚠️  This action cannot be undone!\n")
    
    confirm = input("Type 'RESET' to continue: ")
    
    if confirm != "RESET":
        print("\n❌ Reset cancelled.")
        sys.exit(0)
    
    # Verify connection first
    if not verify_connection():
        print("\n❌ Cannot proceed. Database connection failed.")
        sys.exit(1)
    
    # Drop all tables
    drop_all_tables()
    
    # Create fresh tables
    create_all_tables()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE RESET COMPLETE!")
    print("=" * 60)
    print("\nYour database is now clean and ready for fresh seeding.")
    print("Run your seed script to populate with new data.")