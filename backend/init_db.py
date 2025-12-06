"""
Database initialization script with seed data for RBAC system.
Run this to set up the database with initial users and roles.
"""
import sys
from pathlib import Path
import sqlite3
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# DON'T import models here - we need to check database first
# from sqlalchemy.orm import Session
# from app.core.database import engine, SessionLocal, Base
# from app.models.user import UserDB
# from app.models.ticket import TicketDB
# from app.models.audit_log import AuditLogDB
# from app.models.role import Role
# from app.core.security import get_password_hash


def init_database():
    """Initialize database tables."""
    db_path = "data/processed/auto_ops.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # First, check if database exists and has old schema
    if os.path.exists(db_path):
        print("[i] Existing database detected, checking schema...")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone() is not None
            
            if table_exists:
                # Check if role column exists in users table
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'role' not in columns:
                    print("[*] Old database schema detected (missing RBAC fields).")
                    print("   Recreating database...")
                    conn.close()
                    try:
                        os.remove(db_path)
                        print(f"[OK] Old database removed")
                    except PermissionError:
                        print(f"[!] Could not remove locked database file, will attempt forced removal...")
                        import time
                        time.sleep(0.5)
                        try:
                            os.remove(db_path)
                        except:
                            print(f"[!] Failed to remove database, using fresh schema")
                else:
                    print("[OK] Database schema is up to date")
                    conn.close()
            else:
                conn.close()
        except Exception as e:
            print(f"[!] Database check error")
    
    # NOW import models and create tables
    print("Creating database tables...")
    from sqlalchemy.orm import Session
    from app.core.database import engine, SessionLocal, Base
    from app.models.user import UserDB
    from app.models.ticket import TicketDB
    from app.models.audit_log import AuditLogDB
    from app.models.role import Role
    from app.core.security import get_password_hash
    
    # Drop and recreate all tables to ensure fresh schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created successfully")
    
    return SessionLocal, UserDB, Role, get_password_hash


def seed_initial_users(db, UserDB, Role, get_password_hash):
    """Seed initial users with different roles."""
    print("\nSeeding initial users...")
    
    # Check if users already exist
    try:
        existing_users = db.query(UserDB).count()
        if existing_users > 0:
            print(f"[i] Database already has {existing_users} users. Skipping seed.")
            return
    except Exception as e:
        print(f"[i] Existing users table detected, checking schema...")
        db.rollback()
    
    users = [
        # System Admin
        UserDB(
            email="admin@acme.com",
            name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=Role.SYSTEM_ADMIN.value,
            department="IT",
            is_active=True
        ),
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print(f"[OK] Seeded {len(users)} users successfully")
    
    # Print credentials
    print("\n[*] Initial User Credentials:")
    print("=" * 60)
    print(f"{'Email':<35} {'Password':<15} {'Role':<20}")
    print("=" * 60)
    print(f"{'admin@acme.com':<35} {'admin123':<15} {'System Admin':<20}")
    print("=" * 60)
    print("\n[i] Other users can be registered through the /auth/register endpoint")


def main():
    """Main initialization function."""
    print("[*] Initializing Auto-Ops AI Database with RBAC System")
    print("=" * 80)
    
    # Initialize database and get imports
    SessionLocal, UserDB, Role, get_password_hash = init_database()
    
    # Create session and seed data
    db = SessionLocal()
    try:
        seed_initial_users(db, UserDB, Role, get_password_hash)
        
        print("\n[OK] Database initialization completed successfully!")
        print("\n[i] You can now login with the admin user listed above")
        
    except Exception as e:
        print(f"\n[ERROR] Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
