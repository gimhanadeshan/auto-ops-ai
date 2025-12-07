"""
Quick script to create test agents for assignment testing
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def login_as_admin():
    """Login as admin to get token"""
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@acme.com", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def create_agent(token, agent_data):
    """Create a support agent"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/admin/users",
        headers=headers,
        json=agent_data
    )
    
    if response.status_code in [200, 201]:
        user = response.json()
        print(f"✅ Created: {user['name']} ({user['email']}) - {user['role']}")
        print(f"   Specializations: {user.get('specialization', [])}")
        return user
    else:
        print(f"❌ Failed to create {agent_data['name']}: {response.text}")
        return None

def get_assignable_agents(token):
    """List all assignable agents"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/users/assignable", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get agents: {response.text}")
        return []

def main():
    print("🚀 Setting up test agents for smart assignment...\n")
    
    # Login
    print("1️⃣ Logging in as admin...")
    token = login_as_admin()
    if not token:
        return
    print("   ✅ Logged in successfully\n")
    
    # Create test agents
    print("2️⃣ Creating support agents...\n")
    
    agents = [
        {
            "email": "john.hardware@company.com",
            "name": "John Smith",
            "password": "agent123",
            "role": "support_l2",
            "department": "IT Support",
            "specialization": ["hardware", "critical"]
        },
        {
            "email": "alex.software@company.com",
            "name": "Alex Turner",
            "password": "agent123",
            "role": "support_l1",
            "department": "IT Support",
            "specialization": ["software", "performance"]
        },
        {
            "email": "priya.network@company.com",
            "name": "Priya Nair",
            "password": "agent123",
            "role": "support_l1",
            "department": "IT Support",
            "specialization": ["network", "vpn"]
        }
    ]
    
    for agent_data in agents:
        create_agent(token, agent_data)
        print()
    
    # List all agents
    print("3️⃣ Verifying assignable agents...\n")
    assignable = get_assignable_agents(token)
    
    print(f"📋 Found {len(assignable)} assignable agents:")
    for agent in assignable:
        workload = agent.get('current_workload', 0)
        specs = agent.get('specialization', [])
        print(f"   • {agent['name']} ({agent['role']}) - Workload: {workload}")
        if specs:
            print(f"     Specializations: {', '.join(specs)}")
    
    print("\n✅ Setup complete! Ready to test assignment.")
    print("\n📋 Next steps:")
    print("   1. Start frontend: cd frontend; npm run dev")
    print("   2. Login as user: staff@acme-soft.com / staff123")
    print("   3. Create tickets via chat:")
    print("      • 'My laptop keeps blue screening' → Should assign to John (hardware)")
    print("      • 'VS Code is freezing' → Should assign to Alex (software)")
    print("      • 'VPN not connecting' → Should assign to Priya (network)")

if __name__ == "__main__":
    main()
