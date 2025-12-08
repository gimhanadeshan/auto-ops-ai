"""
Backend Setup Script - One-command setup for Auto-Ops-AI Backend

This script handles:
1. Database initialization
2. Running all migrations in correct order
3. Creating test users and agents
4. Ingesting knowledge base data into RAG
5. Verifying setup

Usage:
    python setup_backend.py
"""
import os
import sys
import subprocess
from pathlib import Path

def print_header(message):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {message}")
    print("="*70 + "\n")

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'  # Replace undecodable characters instead of crashing
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        return False
    except FileNotFoundError:
        print(f"❌ Script not found: {script_name}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'langchain',
        'langchain_chroma',
        'langchain_huggingface',
        'chromadb'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print(f"\nPlease run: pip install -r requirements.txt")
        print(f"Then run this setup script again.\n")
        sys.exit(1)
    else:
        print("✅ All required packages installed")
        return True

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("⚠️  WARNING: .env file not found!")
        print("   Copy .env.example to .env and add your API keys:")
        print("   - GOOGLE_API_KEY (required for LLM and embeddings)")
        print("   - SECRET_KEY (optional, will be auto-generated)")
        response = input("\n   Continue anyway? (y/n): ")
        return response.lower() == 'y'
    else:
        print("✅ .env file found")
        return True

def check_database():
    """Check if database directory exists"""
    db_dir = Path(__file__).parent / "data" / "processed"
    db_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Database directory ready: {db_dir}")
    return True

def main():
    """Main setup routine"""
    print_header("🚀 AUTO-OPS-AI BACKEND SETUP")
    
    print("This script will set up the backend in the following steps:")
    print("  1. Check environment configuration")
    print("  2. Initialize database schema")
    print("  3. Run migrations (assignments, specializations, etc.)")
    print("  4. Create test users and support agents")
    print("  5. Ingest knowledge base into RAG database")
    print("  6. Verify setup\n")
    
    response = input("Continue with setup? (y/n): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Step 1: Check environment
    print_header("STEP 1: Environment Check")
    
    if not check_dependencies():
        print("\n❌ Setup cancelled. Please install dependencies first.")
        return
    
    if not check_env_file():
        print("\n❌ Setup cancelled. Please configure .env file first.")
        return
    
    if not check_database():
        print("\n❌ Setup cancelled. Could not create database directory.")
        return
    
    # Step 2: Initialize database
    print_header("STEP 2: Database Initialization")
    if not run_script("init_db.py", "Initialize database schema"):
        print("\n❌ Setup failed at database initialization.")
        return
    
    # Step 3: Run migrations (only if database already existed)
    print_header("STEP 3: Running Migrations")
    
    # Check if this is a fresh database or existing one
    db_path = Path(__file__).parent / "data" / "processed" / "auto_ops.db"
    migrations_needed = False
    
    if db_path.exists():
        # Check if migrations table exists to determine if this is pre-existing
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        has_migrations_table = cursor.fetchone() is not None
        conn.close()
        
        if has_migrations_table:
            migrations_needed = True
    
    if migrations_needed:
        print("📋 Existing database detected - running migrations...")
        
        migrations = [
            ("migrate_add_assignment.py", "Add assignment and specialization columns"),
            # Add other migration scripts here as they are created
            # ("migrate_add_sla.py", "Add SLA tracking columns"),
        ]
        
        for script, description in migrations:
            script_path = Path(__file__).parent / script
            if script_path.exists():
                if not run_script(script, description):
                    print(f"\n⚠️  Migration '{script}' failed but continuing...")
            else:
                print(f"⏭️  Skipping {script} (not found)")
    else:
        print("✅ Fresh database - schema includes all fields, no migrations needed!")
    
    # Step 4: Create test data
    print_header("STEP 4: Creating Test Users and Agents")
    if not run_script("create_test_agents.py", "Create test support agents"):
        print("\n⚠️  Test agent creation failed but continuing...")
    
    # Step 5: Ingest knowledge base
    print_header("STEP 5: Ingesting Knowledge Base into RAG")
    if not run_script("ingestion_script.py", "Ingest knowledge base data"):
        print("\n⚠️  Knowledge base ingestion failed")
        print("   You can run 'python ingestion_script.py' manually later")
        print("   Make sure GOOGLE_API_KEY is set in .env file")
    
    # Step 6: Verify setup
    print_header("STEP 6: Verification")
    verify_setup()
    
    # Final summary
    print_header("✅ SETUP COMPLETE!")
    print("Backend is ready to run!")
    print("\nNext steps:")
    print("  1. Start the backend server:")
    print("     cd backend")
    print("     uvicorn app.main:app --reload")
    print("\n  2. Or use the run script:")
    print("     .\\run.ps1 (Windows)")
    print("     ./run.sh (Linux/Mac)")
    print("\n  3. Access API documentation:")
    print("     http://localhost:8000/docs")
    print("\n  4. Test credentials:")
    print("     Email: admin@acme.com")
    print("     Password: admin123")
    print("\n" + "="*70 + "\n")

def verify_setup():
    """Verify that setup completed successfully"""
    checks = []
    
    # Check database file exists
    db_path = Path(__file__).parent / "data" / "processed" / "auto_ops.db"
    checks.append(("Database file", db_path.exists()))
    
    # Check ChromaDB directory exists
    chroma_path = Path(__file__).parent / "data" / "processed" / "chroma_db"
    checks.append(("RAG database", chroma_path.exists()))
    
    # Check if we can import main modules
    try:
        from app.main import app
        checks.append(("FastAPI app", True))
    except Exception as e:
        checks.append(("FastAPI app", False))
    
    # Display results
    print("Verification checks:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All checks passed!")
    else:
        print("\n⚠️  Some checks failed. Review errors above.")
    
    return all_passed

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
