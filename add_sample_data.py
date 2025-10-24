#!/usr/bin/env python3
"""
Add sample data for testing the admin dashboard
"""

from app import app, db, User, MenuItem, Order, OrderItem, Cart
from werkzeug.security import generate_password_hash

def add_sample_data():
    """Add sample data to the database"""
    with app.app_context():
        try:
            # Create users if they don't exist
            if User.query.count() == 0:
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    is_admin=True
                )
                user1 = User(
                    username='john_doe',
                    password=generate_password_hash('password123'),
                    is_admin=False
                )
                user2 = User(
                    username='jane_smith',
                    password=generate_password_hash('password123'),
                    is_admin=False
                )
                
                db.session.add_all([admin, user1, user2])
                db.session.commit()
                print("✅ Sample users created")
            
            # Create menu items if they don't exist
            if MenuItem.query.count() == 0:
                menu_items = [
                    MenuItem(name='Pancakes', description='Fluffy breakfast pancakes', price=5.99, shift='breakfast', available=True),
                    MenuItem(name='Scrambled Eggs', description='Fresh scrambled eggs', price=4.50, shift='breakfast', available=True),
                    MenuItem(name='Chicken Curry', description='Spicy chicken curry with rice', price=12.99, shift='lunch', available=True),
                    MenuItem(name='Grilled Fish', description='Fresh grilled fish with vegetables', price=15.99, shift='lunch', available=True),
                    MenuItem(name='Beef Steak', description='Premium beef steak', price=18.99, shift='dinner', available=True),
                    MenuItem(name='Pasta Carbonara', description='Creamy pasta with bacon', price=11.99, shift='dinner', available=True),
                ]
                
                db.session.add_all(menu_items)
                db.session.commit()
                print("✅ Sample menu items created")
            
            # Create sample orders if they don't exist
            if Order.query.count() == 0:
                users = User.query.filter(User.is_admin == False).all()
                menu_items = MenuItem.query.all()
                
                if users and menu_items:
                    # Breakfast order
                    breakfast_order = Order(
                        user_id=users[0].id,
                        meal_shift='breakfast',
                        total_amount=10.49,
                        status='completed'
                    )
                    db.session.add(breakfast_order)
                    db.session.flush()
                    
                    # Add order items for breakfast
                    breakfast_items = [
                        OrderItem(order_id=breakfast_order.id, item_id=menu_items[0].id, quantity=1, unit_price=5.99),  # Pancakes
                        OrderItem(order_id=breakfast_order.id, item_id=menu_items[1].id, quantity=1, unit_price=4.50),  # Scrambled Eggs
                    ]
                    db.session.add_all(breakfast_items)
                    
                    # Lunch order
                    lunch_order = Order(
                        user_id=users[1].id,
                        meal_shift='lunch',
                        total_amount=12.99,
                        status='pending'
                    )
                    db.session.add(lunch_order)
                    db.session.flush()
                    
                    # Add order items for lunch
                    lunch_items = [
                        OrderItem(order_id=lunch_order.id, item_id=menu_items[2].id, quantity=1, unit_price=12.99),  # Chicken Curry
                    ]
                    db.session.add_all(lunch_items)
                    
                    # Dinner order
                    dinner_order = Order(
                        user_id=users[0].id,
                        meal_shift='dinner',
                        total_amount=30.98,
                        status='completed'
                    )
                    db.session.add(dinner_order)
                    db.session.flush()
                    
                    # Add order items for dinner
                    dinner_items = [
                        OrderItem(order_id=dinner_order.id, item_id=menu_items[4].id, quantity=1, unit_price=18.99),  # Beef Steak
                        OrderItem(order_id=dinner_order.id, item_id=menu_items[5].id, quantity=1, unit_price=11.99),  # Pasta Carbonara
                    ]
                    db.session.add_all(dinner_items)
                    
                    db.session.commit()
                    print("✅ Sample orders created")
            
            print("\n🎉 Sample data added successfully!")
            print("📊 Dashboard now has meaningful data to display")
            print("🔑 Login credentials:")
            print("   Admin: admin / admin123")
            print("   User1: john_doe / password123")
            print("   User2: jane_smith / password123")
            
        except Exception as e:
            print(f"❌ Error adding sample data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_data()