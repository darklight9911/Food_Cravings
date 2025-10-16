from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext, ngettext, lazy_gettext
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Babel configuration
app.config['LANGUAGES'] = {
    'en': 'English',
    'bn': 'বাংলা'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

db = SQLAlchemy(app)
babel = Babel(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    feedback = db.relationship('Feedback', backref='user', lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(200))
    shift = db.Column(db.String(20), nullable=False)  # breakfast, lunch, supper, dinner
    available = db.Column(db.Boolean, default=True)
    feedbacks = db.relationship('Feedback', backref='menu_item', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_shift = db.Column(db.String(20), nullable=False)  # breakfast, lunch, supper, dinner
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    # Relationships  
    item = db.relationship('MenuItem', backref='order_items', lazy=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cart_items', lazy=True)
    item = db.relationship('MenuItem', backref='cart_items', lazy=True)
    
    # Unique constraint to prevent duplicate items in cart
    __table_args__ = (db.UniqueConstraint('user_id', 'item_id', name='_user_item_cart'),)

with app.app_context():
    db.create_all()

# Babel locale selector
@babel.localeselector
def get_locale():
    # 1. Check if language is set in session
    if 'language' in session:
        return session['language']
    # 2. Check if language is provided in request args
    if request.args.get('lang'):
        session['language'] = request.args.get('lang')
        return session['language']
    # 3. Fall back to browser's preferred language
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']

# Language context processor
@app.context_processor
def inject_conf_vars():
    return {
        'LANGUAGES': app.config['LANGUAGES'],
        'CURRENT_LANGUAGE': session.get('language', get_locale()),
        '_': gettext
    }

# Cart context processor
@app.context_processor
def inject_cart_count():
    if 'user_id' in session:
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
        return {'cart_count': cart_count}
    return {'cart_count': 0}

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    notices = Notice.query.order_by(Notice.timestamp.desc()).limit(5).all()
    featured_items = MenuItem.query.filter_by(available=True).order_by(db.func.random()).limit(6).all()
    return render_template('index.html', notices=notices, featured_items=featured_items)

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    for item in menu_items:
        feedbacks = Feedback.query.filter_by(item_id=item.id).all()
        if feedbacks:
            item.average_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
            item.total_ratings = len(feedbacks)
        else:
            item.average_rating = 0
            item.total_ratings = 0
    return render_template('menu.html', menu_items=menu_items)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(MenuItem.price * Order.quantity))\
        .select_from(Order)\
        .join(MenuItem, MenuItem.id == Order.item_id)\
        .scalar() or 0
    total_items = MenuItem.query.count()
    recent_orders = Order.query.options(db.joinedload('item'), db.joinedload('user')).order_by(Order.timestamp.desc()).limit(10).all()
    popular_items = MenuItem.query.join(Order).group_by(MenuItem.id).order_by(db.func.count(Order.id).desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         total_items=total_items,
                         recent_orders=recent_orders,
                         popular_items=popular_items)

@app.route('/admin/menu')
@admin_required
def admin_menu():
    menu_items = MenuItem.query.all()
    return render_template('admin/menu.html', menu_items=menu_items)

@app.route('/admin/menu/add', methods=['POST'])
@admin_required
def admin_menu_add():
    try:
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        shift = request.form['shift']
        
        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join('static/uploads', filename)
            image.save(os.path.join(app.root_path, image_path))
        
        item = MenuItem(
            name=name,
            description=description,
            price=price,
            shift=shift,
            image_path=image_path
        )
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/menu/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def admin_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    if request.method == 'GET':
        return jsonify({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'shift': item.shift,
            'available': item.available
        })
    
    elif request.method == 'PUT':
        try:
            item.name = request.form['name']
            item.description = request.form['description']
            item.price = float(request.form['price'])
            item.shift = request.form['shift']
            
            image = request.files.get('image')
            if image and image.filename:
                if item.image_path and os.path.exists(os.path.join(app.root_path, item.image_path)):
                    os.remove(os.path.join(app.root_path, item.image_path))
                filename = secure_filename(image.filename)
                image_path = os.path.join('static/uploads', filename)
                image.save(os.path.join(app.root_path, image_path))
                item.image_path = image_path
            
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    elif request.method == 'DELETE':
        try:
            if item.image_path and os.path.exists(os.path.join(app.root_path, item.image_path)):
                os.remove(os.path.join(app.root_path, item.image_path))
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/menu/<int:item_id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.available = not item.available
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    order.status = data.get('status')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/orders/add', methods=['POST'])
@login_required
def add_to_order():
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        menu_item = MenuItem.query.get_or_404(item_id)
        if not menu_item.available:
            return jsonify({'success': False, 'error': 'Item is not available'})
        
        order = Order(
            user_id=session['user_id'],
            item_id=item_id,
            quantity=quantity
        )
        db.session.add(order)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/feedback/<int:item_id>', methods=['POST'])
@login_required
def add_feedback(item_id):
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            rating = data.get('rating')
            comment = data.get('comment')
        else:
            rating = request.form.get('rating')
            comment = request.form.get('comment')
        
        feedback = Feedback(
            user_id=session['user_id'],
            item_id=item_id,
            rating=int(rating),
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Thank you for your feedback!')
            return redirect(url_for('view_orders'))
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        else:
            flash('Error submitting feedback. Please try again.')
            return redirect(url_for('view_orders'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('Successfully logged in!')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out.')
    return redirect(url_for('index'))

@app.route('/set_language/<language>')
def set_language(language=None):
    if language in app.config['LANGUAGES'].keys():
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

# Notice Board Routes
@app.route('/admin/notices')
@admin_required
def admin_notices():
    notices = Notice.query.order_by(Notice.timestamp.desc()).all()
    return render_template('admin_notices.html', notices=notices)

@app.route('/admin/notices/add', methods=['POST'])
@admin_required
def add_notice():
    title = request.form.get('title')
    content = request.form.get('content')
    
    notice = Notice(title=title, content=content)
    db.session.add(notice)
    db.session.commit()
    
    flash('Notice added successfully!')
    return redirect(url_for('admin_notices'))

@app.route('/admin/notices/<int:notice_id>/delete', methods=['POST'])
@admin_required
def delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    
    flash('Notice deleted successfully!')
    return redirect(url_for('admin_notices'))

@app.route('/notices')
def view_notices():
    notices = Notice.query.order_by(Notice.timestamp.desc()).all()
    return render_template('notices.html', notices=notices)

# Order System Routes
@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))
    
    menu_item = MenuItem.query.get_or_404(item_id)
    if not menu_item.available:
        flash('Sorry, this item is currently unavailable.')
        return redirect(url_for('index'))
    
    order = Order(
        user_id=session['user_id'],
        item_id=item_id,
        quantity=quantity
    )
    db.session.add(order)
    db.session.commit()
    
    flash('Order placed successfully!')
    return redirect(url_for('view_orders'))

@app.route('/orders')
@login_required
def view_orders():
    orders = Order.query.options(db.joinedload('order_items')).filter_by(user_id=session['user_id']).order_by(Order.timestamp.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != session['user_id']:
        flash('You can only cancel your own orders.')
        return redirect(url_for('view_orders'))
    
    if order.status != 'pending':
        flash('You can only cancel pending orders.')
        return redirect(url_for('view_orders'))
    
    order.status = 'cancelled'
    db.session.commit()
    
    flash('Order cancelled successfully.')
    return redirect(url_for('view_orders'))

# Cart Management Routes
@app.route('/cart')
@login_required
def view_cart():
    cart_items = Cart.query.options(db.joinedload('item')).filter_by(user_id=session['user_id']).all()
    
    # Group items by meal shift
    cart_by_shift = {}
    total_amount = 0
    
    for cart_item in cart_items:
        shift = cart_item.item.shift
        if shift not in cart_by_shift:
            cart_by_shift[shift] = []
        cart_by_shift[shift].append(cart_item)
        total_amount += cart_item.item.price * cart_item.quantity
    
    return render_template('cart.html', cart_by_shift=cart_by_shift, total_amount=total_amount)

@app.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    
    # Check if item exists and is available
    menu_item = MenuItem.query.get_or_404(item_id)
    if not menu_item.available:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
        if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
            return jsonify({'success': False, 'message': 'Item is not available'})
        flash('Sorry, this item is currently unavailable.')
        return redirect(url_for('menu'))
    
    # Check if item already exists in cart
    existing_cart_item = Cart.query.filter_by(user_id=session['user_id'], item_id=item_id).first()
    
    if existing_cart_item:
        # Update quantity
        existing_cart_item.quantity += quantity
    else:
        # Add new item to cart
        cart_item = Cart(
            user_id=session['user_id'],
            item_id=item_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Always return JSON for API endpoints, or if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
        return jsonify({'success': True, 'cart_count': cart_count, 'message': f'{menu_item.name} added to cart'})
    
    flash(f'{menu_item.name} added to cart!')
    return redirect(url_for('menu'))

@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart_item(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    # Verify ownership
    if cart_item.user_id != session['user_id']:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
        if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
            return jsonify({'success': False, 'message': 'Unauthorized'})
        flash('Unauthorized action.')
        return redirect(url_for('view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
        return jsonify({'success': True, 'message': 'Cart updated'})
    
    flash('Cart updated successfully!')
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    # Verify ownership
    if cart_item.user_id != session['user_id']:
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
        if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
            return jsonify({'success': False, 'message': 'Unauthorized'})
        flash('Unauthorized action.')
        return redirect(url_for('view_cart'))
    
    item_name = cart_item.item.name
    db.session.delete(cart_item)
    db.session.commit()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
        return jsonify({'success': True, 'cart_count': cart_count, 'message': f'{item_name} removed from cart'})
    
    flash(f'{item_name} removed from cart!')
    return redirect(url_for('view_cart'))

@app.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    Cart.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    if is_ajax or request.headers.get('Accept', '').find('application/json') != -1:
        return jsonify({'success': True, 'message': 'Cart cleared'})
    
    flash('Cart cleared successfully!')
    return redirect(url_for('view_cart'))

@app.route('/cart/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('view_cart'))
    
    # Group cart items by meal shift
    meal_groups = {}
    for cart_item in cart_items:
        meal_shift = cart_item.item.meal_shift
        if meal_shift not in meal_groups:
            meal_groups[meal_shift] = []
        meal_groups[meal_shift].append(cart_item)
    
    # Create one order per meal shift
    orders_created = 0
    for meal_shift, items in meal_groups.items():
        total_amount = sum(item.quantity * item.item.price for item in items)
        
        # Create the order
        order = Order(
            user_id=session['user_id'],
            meal_shift=meal_shift,
            total_amount=total_amount
        )
        db.session.add(order)
        db.session.flush()  # To get the order ID
        
        # Create order items
        for cart_item in items:
            order_item = OrderItem(
                order_id=order.id,
                item_id=cart_item.item_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.item.price
            )
            db.session.add(order_item)
        
        orders_created += 1
    
    # Clear the cart after creating orders
    Cart.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    
    flash(f'Successfully placed {orders_created} orders!')
    return redirect(url_for('view_orders'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.options(db.joinedload('user'), db.joinedload('order_items')).order_by(Order.timestamp.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.form.get('status')
    if status in ['pending', 'completed', 'cancelled']:
        order.status = status
        db.session.commit()
        flash('Order status updated successfully.')
    return redirect(url_for('admin_orders'))

# Profile Routes
@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    
    # Get user's order statistics
    total_orders = Order.query.filter_by(user_id=user.id).count()
    completed_orders = Order.query.filter_by(user_id=user.id, status='completed').count()
    pending_orders = Order.query.filter_by(user_id=user.id, status='pending').count()
    
    # Get recent orders
    recent_orders = Order.query.filter_by(user_id=user.id)\
        .options(db.joinedload('item'))\
        .order_by(Order.timestamp.desc())\
        .limit(10).all()
    
    # Get user's feedback
    user_feedback = Feedback.query.filter_by(user_id=user.id)\
        .options(db.joinedload('menu_item'))\
        .order_by(Feedback.timestamp.desc())\
        .limit(5).all()
    
    # Calculate total spent
    total_spent = db.session.query(db.func.sum(MenuItem.price * Order.quantity))\
        .select_from(Order)\
        .join(MenuItem, MenuItem.id == Order.item_id)\
        .filter(Order.user_id == user.id, Order.status == 'completed')\
        .scalar() or 0
    
    return render_template('profile.html', 
                         user=user,
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders,
                         user_feedback=user_feedback,
                         total_spent=total_spent)

@app.route('/admin/profile')
@admin_required
def admin_profile():
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    
    # Get admin statistics
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(MenuItem.price * Order.quantity))\
        .select_from(Order)\
        .join(MenuItem, MenuItem.id == Order.item_id)\
        .filter(Order.status == 'completed')\
        .scalar() or 0
    total_items = MenuItem.query.count()
    total_users = User.query.count()
    total_feedback = Feedback.query.count()
    
    # Get recent activity
    recent_orders = Order.query.options(db.joinedload('item'), db.joinedload('user'))\
        .order_by(Order.timestamp.desc())\
        .limit(10).all()
    
    recent_feedback = Feedback.query.options(db.joinedload('menu_item'), db.joinedload('user'))\
        .order_by(Feedback.timestamp.desc())\
        .limit(5).all()
    
    # Get popular items
    popular_items = MenuItem.query.join(Order)\
        .group_by(MenuItem.id)\
        .order_by(db.func.count(Order.id).desc())\
        .limit(5).all()
    
    return render_template('admin/profile.html',
                         user=user,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         total_items=total_items,
                         total_users=total_users,
                         total_feedback=total_feedback,
                         recent_orders=recent_orders,
                         recent_feedback=recent_feedback,
                         popular_items=popular_items)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    
    new_username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Check if username is being changed and if it's available
    if new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            flash('Username already exists.')
            return redirect(url_for('profile'))
        user.username = new_username
    
    # Check if password is being changed
    if new_password:
        if not current_password or not check_password_hash(user.password, current_password):
            flash('Current password is incorrect.')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.')
            return redirect(url_for('profile'))
        
        user.password = generate_password_hash(new_password)
    
    db.session.commit()
    flash('Profile updated successfully!')
    return redirect(url_for('profile'))



if __name__ == '__main__':
    app.run(debug=True)