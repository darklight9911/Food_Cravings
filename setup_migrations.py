#!/usr/bin/env python3
"""
Complete setup script for Flask-Migrate in Food Cravings canteen management system.
This script handles the entire migration setup process.
"""

import os
import sys
from app import app, db, User
from werkzeug.security import generate_password_hash

def setup_migrations():
    """Complete Flask-Migrate setup"""
    print("🚀 Setting up Flask-Migrate for Food Cravings...")
    
    try:
        # Import migration functions
        from flask_migrate import init, migrate, upgrade
        
        with app.app_context():
            # Step 1: Check if migrations directory exists
            if not os.path.exists('migrations'):
                print("📁 Initializing migration repository...")
                init()
                print("✅ Migration repository initialized!")
            else:
                print("✅ Migration repository already exists")
            
            # Step 2: Create initial migration if no database exists
            if not os.path.exists('canteen.db'):
                print("📝 Creating initial migration...")
                
                # Force create migration using alembic directly
                from alembic import command
                from alembic.config import Config
                
                migrations_dir = os.path.join(os.getcwd(), 'migrations')
                alembic_cfg = Config(os.path.join(migrations_dir, 'alembic.ini'))
                alembic_cfg.set_main_option('script_location', migrations_dir)
                
                try:
                    command.revision(alembic_cfg, message='Initial migration - all models', autogenerate=True)
                    print("✅ Initial migration created!")
                except Exception as e:
                    print(f"⚠️  Migration already exists or error: {str(e)}")
                
                # Apply migration
                print("🔄 Applying migrations to create database...")
                upgrade()
                print("✅ Database created successfully!")
                
                # Create admin user
                print("👤 Creating admin user...")
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin_user = User(
                        username='admin',
                        password=generate_password_hash('admin123'),
                        is_admin=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Admin user created!")
                    print("   👤 Username: admin")
                    print("   🔑 Password: admin123")
                else:
                    print("✅ Admin user already exists")
            else:
                print("✅ Database already exists")
            
            print("\n🎉 Flask-Migrate setup completed successfully!")
            print("\n📖 Available commands:")
            print("   python manage_db.py migrate 'description'  - Create new migration")
            print("   python manage_db.py upgrade                - Apply migrations")
            print("   python manage_db.py current                - Show current version")
            print("   python manage_db.py history                - Show migration history")
            print("\n📚 See FLASK_MIGRATE_GUIDE.md for detailed documentation")
            
    except ImportError:
        print("❌ Flask-Migrate not installed!")
        print("Please install it with: pip install Flask-Migrate==3.1.0")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    setup_migrations()