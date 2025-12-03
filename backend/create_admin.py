"""
Create an admin user for Auto-Ops-AI
"""
from app.core.database import SessionLocal, engine
from app.models.user import UserDB
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(UserDB).filter(UserDB.email == "admin@autoops.ai").first()
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Email: admin@autoops.ai")
            print(f"   Current Tier: {existing_admin.tier}")
            
            # Update to admin if not already
            if existing_admin.tier != "admin":
                existing_admin.tier = "admin"
                db.commit()
                print("✅ Updated existing user to admin tier")
            return
        
        # Create new admin user
        admin_user = UserDB(
            email="admin@autoops.ai",
            name="Admin User",
            hashed_password=get_password_hash("Admin123!"),
            tier="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("=" * 50)
        print("   Email: admin@autoops.ai")
        print("   Password: Admin123!")
        print("   Tier: admin")
        print("=" * 50)
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
