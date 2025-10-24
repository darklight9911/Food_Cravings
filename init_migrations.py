#!/usr/bin/env python3
"""
Initialize Flask-Migrate for the canteen management system.
This script sets up the migration repository and creates the initial migration.
"""

from flask_migrate import init, migrate, upgrade
from app import app, db
import os

def initialize_migrations():
    """Initialize the migration repository"""
    with app.app_context():
        try:
            # Check if migrations folder already exists
            if os.path.exists('migrations'):
                print("Migrations folder already exists. Skipping initialization...")
            else:
                # Initialize migration repository
                init()
                print("✅ Migration repository initialized successfully!")
            
            # Create initial migration
            migrate(message='Initial migration with all models')
            print("✅ Initial migration created successfully!")
            
            # Apply the migration
            upgrade()
            print("✅ Database upgraded successfully!")
            
            print("\n🎉 Flask-Migrate setup completed!")
            print("\nNow you can use these commands:")
            print("  python manage_db.py migrate    # Create new migration")
            print("  python manage_db.py upgrade    # Apply migrations")
            print("  python manage_db.py downgrade  # Rollback migrations")
            
        except Exception as e:
            print(f"❌ Error during migration setup: {str(e)}")
            print("Make sure your models are properly defined in app.py")

if __name__ == '__main__':
    initialize_migrations()