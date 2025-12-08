"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and apply pending migrations."""
    Base.metadata.create_all(bind=engine)
    
    # Auto-apply pending migrations
    try:
        from migrations import init_migrations_table, migration_applied, record_migration
        import os
        
        db_path = "data/processed/auto_ops.db"
        if os.path.exists(db_path):
            init_migrations_table(db_path)
            
            # Auto-apply agent assignment migration if needed
            if not migration_applied("add_agent_assignment_fields"):
                try:
                    from sqlalchemy import text
                    
                    with engine.connect() as conn:
                        result = conn.execute(text("PRAGMA table_info(users);"))
                        existing_columns = [row[1] for row in result]
                        
                        if 'specialization' not in existing_columns:
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN specialization TEXT NULL;
                            """))
                            conn.commit()
                        
                        if 'current_workload' not in existing_columns:
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN current_workload INTEGER DEFAULT 0;
                            """))
                            conn.commit()
                    
                    record_migration("add_agent_assignment_fields")
                except Exception:
                    pass  # Columns may already exist or DB may not be SQLite
    except Exception:
        pass  # Migrations not available - continue anyway
