"""
Create test support agents directly in database (no API calls needed)
"""
import sys
import io
# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import json

# Import models
from app.models.user import UserDB

# Database setup
DATABASE_URL = "sqlite:///./data/processed/auto_ops.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_agent_in_db(db, email, name, password, role, department, specializations):
    """Create agent directly in database"""
    # Check if user already exists
    existing = db.query(UserDB).filter(UserDB.email == email).first()
    if existing:
        print(f"⚠️  User {email} already exists, skipping...")
        return existing
    
    # Create new user
    hashed_password = pwd_context.hash(password)
    user = UserDB(
        email=email,
        name=name,
        hashed_password=hashed_password,
        role=role,
        department=department,
        specialization=specializations,
        current_workload=0,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✅ Created: {name} ({email})")
    print(f"   Role: {role}")
    print(f"   Specializations: {specializations}")
    return user

def main():
    print("🚀 Creating test support agents...\n")
    
    db = SessionLocal()
    
    try:
        # Define test agents
        agents = [
            {
                "email": "john.hardware@company.com",
                "name": "John Smith",
                "password": "agent123",
                "role": "support_l2",
                "department": "IT Support",
                "specializations": ["hardware", "critical"]
            },
            {
                "email": "alex.software@company.com",
                "name": "Alex Johnson",
                "password": "agent123",
                "role": "support_l2",
                "department": "IT Support",
                "specializations": ["software", "account"]
            },
            {
                "email": "priya.network@company.com",
                "name": "Priya Patel",
                "password": "agent123",
                "role": "support_l2",
                "department": "Network Operations",
                "specializations": ["network", "critical"]
            }
        ]
        
        # Create agents
        created = 0
        for agent_data in agents:
            user = create_agent_in_db(
                db,
                email=agent_data["email"],
                name=agent_data["name"],
                password=agent_data["password"],
                role=agent_data["role"],
                department=agent_data["department"],
                specializations=agent_data["specializations"]
            )
            if user:
                created += 1
            print()
        
        print(f"\n✅ Setup complete! Created/verified {created} support agents")
        print("\nTest agent credentials:")
        print("  Email: john.hardware@company.com")
        print("  Email: alex.software@company.com")
        print("  Email: priya.network@company.com")
        print("  Password: agent123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
