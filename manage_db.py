#!/usr/bin/env python3
"""
Database management script for Flask-Migrate operations.
Usage: python manage_db.py [command]

Commands:
  init      - Initialize migration repository
  migrate   - Create a new migration
  upgrade   - Apply pending migrations
  downgrade - Rollback last migration
  current   - Show current migration
  history   - Show migration history
"""

import sys
from flask_migrate import init, migrate, upgrade, downgrade, current, history
from app import app, db

def show_help():
    """Display help information"""
    print(__doc__)

def run_init():
    """Initialize migration repository"""
    with app.app_context():
        try:
            init()
            print("✅ Migration repository initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing migrations: {str(e)}")

def run_migrate(message=None):
    """Create a new migration"""
    with app.app_context():
        try:
            if message:
                migrate(message=message)
            else:
                migrate()
            print("✅ Migration created successfully!")
        except Exception as e:
            print(f"❌ Error creating migration: {str(e)}")

def run_upgrade():
    """Apply pending migrations"""
    with app.app_context():
        try:
            upgrade()
            print("✅ Database upgraded successfully!")
        except Exception as e:
            print(f"❌ Error upgrading database: {str(e)}")

def run_downgrade():
    """Rollback last migration"""
    with app.app_context():
        try:
            downgrade()
            print("✅ Database downgraded successfully!")
        except Exception as e:
            print(f"❌ Error downgrading database: {str(e)}")

def run_current():
    """Show current migration"""
    with app.app_context():
        try:
            current()
        except Exception as e:
            print(f"❌ Error getting current migration: {str(e)}")

def run_history():
    """Show migration history"""
    with app.app_context():
        try:
            history()
        except Exception as e:
            print(f"❌ Error getting migration history: {str(e)}")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()
    
    if command == 'help' or command == '--help' or command == '-h':
        show_help()
    elif command == 'init':
        run_init()
    elif command == 'migrate':
        message = sys.argv[2] if len(sys.argv) > 2 else None
        run_migrate(message)
    elif command == 'upgrade':
        run_upgrade()
    elif command == 'downgrade':
        run_downgrade()
    elif command == 'current':
        run_current()
    elif command == 'history':
        run_history()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == '__main__':
    main()