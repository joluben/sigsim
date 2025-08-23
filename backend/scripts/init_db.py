#!/usr/bin/env python3
"""
Database initialization script
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from alembic.config import Config
from alembic import command
from app.core.database import engine, Base
from app.schemas.database import Project, Device, Payload, TargetSystem


def init_database():
    """Initialize the database with Alembic"""
    print("🗄️  Initializing database...")
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Check if database has any tables
        inspector = engine.dialect.get_table_names(engine.connect())
        
        if not inspector:
            print("📝 Creating initial migration...")
            # Create initial migration
            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            
            print("⬆️  Running migrations...")
            # Run migrations
            command.upgrade(alembic_cfg, "head")
        else:
            print("📊 Database already exists, checking for pending migrations...")
            # Just run any pending migrations
            command.upgrade(alembic_cfg, "head")
            
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


def create_sample_data():
    """Create sample data for development"""
    from sqlalchemy.orm import sessionmaker
    from app.models.payload import PayloadType
    from app.models.target import TargetType
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if sample data already exists
        if session.query(Project).first():
            print("📊 Sample data already exists")
            return
        
        print("🌱 Creating sample data...")
        
        # Create sample payload
        sample_payload = Payload(
            name="Temperature Sensor",
            type=PayloadType.VISUAL,
            schema={
                "fields": [
                    {
                        "name": "device_id",
                        "type": "string",
                        "generator": {"type": "fixed", "value": "temp-001"}
                    },
                    {
                        "name": "temperature",
                        "type": "number",
                        "generator": {"type": "random_float", "min": 18.0, "max": 25.0, "decimals": 1}
                    },
                    {
                        "name": "timestamp",
                        "type": "timestamp"
                    }
                ]
            }
        )
        session.add(sample_payload)
        
        # Create sample target system
        sample_target = TargetSystem(
            name="HTTP Test Endpoint",
            type=TargetType.HTTP,
            config={
                "url": "https://httpbin.org/post",
                "method": "POST",
                "headers": {"Content-Type": "application/json"}
            }
        )
        session.add(sample_target)
        
        # Create sample project
        sample_project = Project(
            name="Demo Project",
            description="A demonstration project with sample IoT devices"
        )
        session.add(sample_project)
        session.flush()  # Get the project ID
        
        # Create sample device
        sample_device = Device(
            project_id=sample_project.id,
            name="Temperature Sensor 01",
            metadata={"location": "Office", "floor": 2},
            payload_id=sample_payload.id,
            target_system_id=sample_target.id,
            send_interval=30,
            is_enabled=True
        )
        session.add(sample_device)
        
        session.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize IoT Simulator database")
    parser.add_argument("--sample-data", action="store_true", help="Create sample data")
    args = parser.parse_args()
    
    init_database()
    
    if args.sample_data:
        create_sample_data()