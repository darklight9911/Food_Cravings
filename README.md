# 🍽️ Food Cravings - Canteen Management System

A comprehensive web-based canteen management system built with Flask, featuring multi-language support, cart functionality, and order management for different meal shifts.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Internationalization](#-internationalization)
- [Admin Panel](#-admin-panel)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🛒 **Cart System**
- **Multi-item Cart**: Add multiple items from different meal shifts
- **Real-time Updates**: AJAX-powered cart operations
- **Meal Shift Grouping**: Automatic grouping by breakfast, lunch, dinner, supper
- **Quantity Management**: Increase/decrease item quantities
- **Cart Persistence**: Cart items saved per user session

### 🍽️ **Order Management**
- **Grouped Orders**: Orders automatically grouped by meal shift
- **Order Tracking**: Real-time order status updates
- **Order History**: Complete order history for users
- **Cancellation**: Cancel pending orders
- **Feedback System**: Rate and review completed orders

### 👨‍💼 **Admin Panel**
- **Menu Management**: Add, edit, delete menu items
- **Order Management**: View and update order statuses
- **User Management**: Manage user accounts
- **Notice System**: Post announcements and notices
- **Image Upload**: Upload and manage food images

### 🌐 **Multi-language Support**
- **Bilingual Interface**: English and Bengali (বাংলা)
- **Dynamic Translation**: Real-time language switching
- **Localized Content**: All UI elements translated

### 🔐 **Authentication & Security**
- **User Registration/Login**: Secure authentication system
- **Role-based Access**: Admin and user roles
- **Session Management**: Secure session handling
- **Password Hashing**: Werkzeug security integration

## 🛠️ Technology Stack

### Backend
- **Flask 2.0.1** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User session management
- **Flask-Babel** - Internationalization support
- **Werkzeug** - Security utilities

### Frontend
- **HTML5/CSS3** - Modern web standards
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Interactive functionality
- **Font Awesome** - Icon library

### Database
- **SQLite** - Lightweight database (development)
- **Supports PostgreSQL/MySQL** - Production ready

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/darklight9911/Food_Cravings.git
   cd Food_Cravings
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   
   # On Linux/Mac
   source env/bin/activate
   
   # On Windows
   env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Create admin user**
   ```bash
   python create_admin.py
   ```

6. **Compile translations**
   ```bash
   python -c "
   from babel.messages.mofile import write_mo
   from babel.messages.pofile import read_po
   with open('translations/en/LC_MESSAGES/messages.po', 'rb') as f:
       catalog = read_po(f)
   with open('translations/en/LC_MESSAGES/messages.mo', 'wb') as f:
       write_mo(f, catalog)
   with open('translations/bn/LC_MESSAGES/messages.po', 'rb') as f:
       catalog = read_po(f)
   with open('translations/bn/LC_MESSAGES/messages.mo', 'wb') as f:
       write_mo(f, catalog)
   print('Translations compiled successfully')
   "
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///canteen.db
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Database Configuration
```python
# For PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/canteen'

# For MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/canteen'
```

## 📖 Usage

### For Users

1. **Registration/Login**
   - Register a new account or login with existing credentials
   - Access personalized dashboard and order history

2. **Browse Menu**
   - View menu items organized by meal shifts
   - Filter by breakfast, lunch, dinner, or supper
   - Switch between English and Bengali languages

3. **Shopping Cart**
   - Add items to cart from any meal shift
   - Adjust quantities as needed
   - Review cart contents before checkout

4. **Place Orders**
   - Checkout creates grouped orders by meal shift
   - Track order status in real-time
   - Receive notifications on order updates

5. **Order Management**
   - View complete order history
   - Cancel pending orders
   - Provide feedback on completed orders

### For Administrators

1. **Menu Management**
   - Add new menu items with images
   - Update prices and descriptions
   - Enable/disable item availability

2. **Order Processing**
   - View all incoming orders
   - Update order statuses (pending → completed/cancelled)
   - Monitor order volumes and trends

3. **User Management**
   - View registered users
   - Manage user permissions
   - Handle user inquiries

4. **Content Management**
   - Post notices and announcements
   - Manage uploaded images
   - Update system configurations

## 📁 Project Structure

```
Food_Cravings/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── babel.cfg             # Babel configuration
├── create_admin.py       # Admin user creation script
├── create_translations.py # Translation setup script
├── canteen.db           # SQLite database
├── README.md            # Project documentation
├── static/              # Static assets
│   └── uploads/         # User uploaded images
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── menu.html       # Menu display
│   ├── cart.html       # Shopping cart
│   ├── orders.html     # User orders
│   ├── profile.html    # User profile
│   ├── notices.html    # Announcements
│   ├── admin_menu.html # Admin menu management
│   ├── admin_orders.html # Admin order management
│   └── admin_notices.html # Admin notice management
├── translations/        # Multi-language support
│   ├── en/             # English translations
│   └── bn/             # Bengali translations
└── env/                # Virtual environment
```

## 🗃️ Database Schema

### Core Models

#### User
```python
- id (Primary Key)
- username (Unique)
- password (Hashed)
- is_admin (Boolean)
```

#### MenuItem
```python
- id (Primary Key)
- name
- description
- price
- image_path
- shift (breakfast/lunch/dinner/supper)
- available (Boolean)
```

#### Order
```python
- id (Primary Key)
- user_id (Foreign Key)
- meal_shift
- timestamp
- status (pending/completed/cancelled)
- total_amount
```

#### OrderItem
```python
- id (Primary Key)
- order_id (Foreign Key)
- item_id (Foreign Key)
- quantity
- unit_price
```

#### Cart
```python
- id (Primary Key)
- user_id (Foreign Key)
- item_id (Foreign Key)
- quantity
```

#### Feedback
```python
- id (Primary Key)
- user_id (Foreign Key)
- item_id (Foreign Key)
- order_id (Foreign Key)
- rating (1-5)
- comment
- timestamp
```

## 🔗 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /register` - Registration page
- `POST /register` - Process registration
- `GET /logout` - Logout user

### Menu & Cart
- `GET /menu` - Display menu
- `POST /cart/add` - Add item to cart (AJAX)
- `GET /cart` - View cart
- `POST /cart/update` - Update cart quantities
- `POST /cart/remove` - Remove cart items
- `POST /cart/clear` - Clear entire cart
- `POST /cart/checkout` - Process checkout

### Orders
- `GET /orders` - View user orders
- `POST /orders/<id>/cancel` - Cancel order
- `POST /feedback/<item_id>` - Submit feedback

### Admin Routes
- `GET /admin/menu` - Menu management
- `POST /admin/menu/add` - Add menu item
- `GET /admin/orders` - Order management
- `POST /admin/orders/<id>/status` - Update order status
- `GET /admin/notices` - Notice management

## 🌍 Internationalization

The system supports multiple languages using Flask-Babel:

### Supported Languages
- **English** (en) - Default
- **Bengali** (বাংলা) (bn)

### Adding New Languages

1. **Extract translatable strings**
   ```bash
   pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
   ```

2. **Initialize new language**
   ```bash
   pybabel init -i messages.pot -d translations -l [language_code]
   ```

3. **Update existing translations**
   ```bash
   pybabel update -i messages.pot -d translations
   ```

4. **Compile translations**
   ```bash
   pybabel compile -d translations
   ```

## 👨‍💼 Admin Panel

### Default Admin Credentials
```
Username: admin
Password: admin123
```

### Admin Features
- **Dashboard**: Overview of orders and system status
- **Menu Management**: CRUD operations for menu items
- **Order Management**: Process and track orders
- **User Management**: View and manage user accounts
- **Notice System**: Post announcements
- **Image Management**: Upload and organize food images

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Tailwind CSS for beautiful styling utilities
- Font Awesome for comprehensive icon library
- SQLAlchemy for robust ORM capabilities
- Babel team for internationalization support

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/darklight9911/Food_Cravings/issues) page
2. Create a new issue with detailed description
3. Contact the maintainers

---

**Made with ❤️ by [darklight9911](https://github.com/darklight9911)**

*Happy Coding! 🚀*