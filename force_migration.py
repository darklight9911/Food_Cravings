#!/usr/bin/env python3
"""
Force create initial migration for Flask-Migrate
"""

from alembic import command
from alembic.config import Config
from app import app
import os

def create_initial_migration():
    """Create initial migration by force"""
    with app.app_context():
        # Get the migrations directory
        migrations_dir = os.path.join(os.getcwd(), 'migrations')
        
        # Create alembic config
        alembic_cfg = Config(os.path.join(migrations_dir, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', migrations_dir)
        
        try:
            # Generate migration
            command.revision(alembic_cfg, message='Initial migration - all models', autogenerate=True)
            print("✅ Initial migration created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating migration: {str(e)}")

if __name__ == '__main__':
    create_initial_migration()