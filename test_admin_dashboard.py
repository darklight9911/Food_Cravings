#!/usr/bin/env python3
"""
Test script to verify the admin dashboard fix
"""

from app import app, db, Order, OrderItem, MenuItem, User
from sqlalchemy import func

def test_admin_dashboard_queries():
    """Test the updated admin dashboard queries"""
    with app.app_context():
        try:
            # Test total orders
            total_orders = Order.query.count()
            print(f"✅ Total orders: {total_orders}")
            
            # Test total revenue calculation
            total_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price)).scalar() or 0
            print(f"✅ Total revenue: ৳{total_revenue:.2f}")
            
            # Test total items
            total_items = MenuItem.query.count()
            print(f"✅ Total menu items: {total_items}")
            
            # Test recent orders query
            recent_orders = Order.query.options(
                db.joinedload('user'), 
                db.joinedload('order_items')
            ).order_by(Order.timestamp.desc()).limit(10).all()
            print(f"✅ Recent orders: {len(recent_orders)} found")
            
            # Test popular items query
            popular_items = db.session.query(
                MenuItem, 
                func.sum(OrderItem.quantity).label('total_quantity')
            ).join(OrderItem).group_by(MenuItem.id)\
             .order_by(func.sum(OrderItem.quantity).desc()).limit(5).all()
            print(f"✅ Popular items: {len(popular_items)} found")
            
            # Print details of recent orders if any exist
            if recent_orders:
                print("\n📋 Recent Orders Details:")
                for i, order in enumerate(recent_orders[:3], 1):
                    print(f"  {i}. Order #{order.id} - {order.user.username} - {order.meal_shift} - ৳{order.total_amount:.2f}")
                    for order_item in order.order_items:
                        print(f"     - {order_item.quantity}x {order_item.item.name}")
            
            # Print popular items if any exist
            if popular_items:
                print("\n🏆 Popular Items:")
                for i, (item, total_qty) in enumerate(popular_items, 1):
                    print(f"  {i}. {item.name} - {total_qty} sold - ৳{item.price:.2f}")
            
            print("\n🎉 All admin dashboard queries working correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Error in admin dashboard queries: {str(e)}")
            return False

if __name__ == '__main__':
    test_admin_dashboard_queries()