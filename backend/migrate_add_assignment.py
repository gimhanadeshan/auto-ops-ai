"""
Database Migration: Add Agent Assignment Fields

Adds specialization and workload tracking to users table for smart ticket assignment.

Run this BEFORE starting the application if you have existing data.
If this is a fresh database, init_db.py will create the table with these fields.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import get_settings

settings = get_settings()


def migrate_database():
    """Add assignment-related columns to users table."""
    engine = create_engine(settings.database_url)
    
    print("🔄 Starting database migration...")
    print(f"📁 Database: {settings.database_url}")
    
    try:
        with engine.connect() as conn:
            # SQLite: Check if columns already exist using PRAGMA
            result = conn.execute(text("PRAGMA table_info(users);"))
            existing_columns = [row[1] for row in result]  # row[1] is column name
            
            print(f"📋 Found existing columns: {', '.join(existing_columns)}")
            
            if 'specialization' in existing_columns and 'current_workload' in existing_columns:
                print("✅ Migration already applied - columns exist")
                return
            
            print("📝 Adding new columns to users table...")
            
            # Add specialization column (JSON array of expertise areas)
            if 'specialization' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN specialization TEXT NULL;
                """))
                conn.commit()
                print("  ✓ Added 'specialization' column")
            
            # Add current_workload column (number of active tickets)
            if 'current_workload' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN current_workload INTEGER DEFAULT 0;
                """))
                conn.commit()
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Next steps:")
            print("   1. Create support agents via Admin Panel")
            print("   2. Set their specializations (e.g., ['hardware', 'software'])")
            print("   3. New tickets will be auto-assigned!")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\n⚠️  Alternative: Run init_db.py to recreate database with new schema")
        print("   (This will preserve existing data if using SQLAlchemy models)")
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
