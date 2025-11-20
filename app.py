import os
import pickle
import sqlite3
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
import os
app.secret_key = 'supersecretkey' # Change this for production
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load ML Models
try:
    products_dict = pickle.load(open('products_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    # products_dict is a dict of columns, convert to something usable if needed
    # Actually, we only need it to look up indices for the similarity matrix.
    # We can also use the DB for product details.
    # The original code used a dataframe `products` (loaded from csv). 
    # We need a way to map product name -> index in the similarity matrix.
    # The `products_dict` likely contains the dataframe data.
    import pandas as pd
    products_df = pd.DataFrame(products_dict) 
except Exception as e:
    print(f"Error loading ML models: {e}")
    products_df = None
    similarity = None

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    price = db.Column(db.Float)
    market_price = db.Column(db.Float)
    type = db.Column(db.String(100))
    rating = db.Column(db.Float)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer)
    image_url = db.Column(db.String(300))
    soup = db.Column(db.Text)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship('Product')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer)
    price_at_purchase = db.Column(db.Float)
    product = db.relationship('Product')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Context Processor ---
@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        count = CartItem.query.filter_by(user_id=current_user.id).count()
        return {'cart_count': count}
    return {'cart_count': 0}

# --- Routes ---

@app.route('/')
def home():
    # Featured Categories
    categories = [
        {'name': 'Beauty & Hygiene', 'image': 'beauty2.jpg', 'query': 'Beauty, Hygiene'},
        {'name': 'Kitchen, Garden & Pets', 'image': 'kitchen.png', 'query': 'Kitchen, Garden, Pets'},
        {'name': 'Bakery, Cakes & Dairy', 'image': 'bakery.png', 'query': 'Bakery, Cakes, Dairy'},
        {'name': 'Snacks & Branded Foods', 'image': 'snacks.jpeg', 'query': 'Snacks, Branded Foods'},
        {'name': 'Gourmet & World Food', 'image': 'Goumet.png', 'query': 'Gourmet, World Food'},
        {'name': 'Cleaning & Household', 'image': 'cleaning_image_url.jpg', 'query': 'Cleaning, Household'},
        {'name': 'Beverages', 'image': 'beverages_image_url.jpg', 'query': 'Beverages'},
        {'name': 'Foodgrains, Oil & Masala', 'image': 'Food.png', 'query': 'Foodgrains, Oil Cakes, Dairy'}, # Adjusted based on provided images/names
        {'name': 'Baby Care', 'image': 'Baby.png', 'query': 'Baby Care'}
    ]
    return render_template('index.html', categories=categories)

@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search_query = request.args.get('search')
    sort_by = request.args.get('sort')
    
    query = Product.query

    if category:
        # Use ILIKE for case-insensitive matching or just check substring
        query = query.filter(Product.category.contains(category))
    
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    
    products_paginated = query.paginate(page=page, per_page=12)
    
    return render_template('products_list.html', products=products_paginated, category=category, search=search_query, sort=sort_by)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    substitutes = []
    
    # Check stock
    if product.stock <= 0:
        # Get substitutes logic
        if products_df is not None and similarity is not None:
            try:
                # Find index of product in dataframe
                # We need to match exact name from DB to DF
                # The setup_db used the same source, so names should match.
                product_idx_list = products_df.index[products_df['product'] == product.name].tolist()
                if product_idx_list:
                    product_index = product_idx_list[0]
                    distances = similarity[product_index]
                    # Get top 5 similar
                    similar_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
                    
                    for i, score in similar_indices:
                        # Get product name from DF
                        sim_product_name = products_df.iloc[i]['product']
                        # Fetch from DB
                        sim_product_db = Product.query.filter_by(name=sim_product_name).first()
                        if sim_product_db:
                            substitutes.append(sim_product_db)
            except Exception as e:
                print(f"Error fetching substitutes: {e}")

    return render_template('product_detail.html', product=product, substitutes=substitutes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
            
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'warning')
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please login.', 'success')
            return redirect(url_for('login'))
            
    return render_template('auth/signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('Product is out of stock.', 'danger')
        return redirect(request.referrer)
    
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += 1
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(item)
    
    db.session.commit()
    flash(f'Added {product.name} to cart.', 'success')
    return redirect(request.referrer)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return redirect(url_for('cart'))
    
    action = request.form.get('action')
    if action == 'increase':
        if item.quantity < item.product.stock:
            item.quantity += 1
        else:
            flash(f'Only {item.product.stock} items in stock.', 'warning')
    elif action == 'decrease':
        item.quantity -= 1
    
    if item.quantity <= 0:
        db.session.delete(item)
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('home'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # Create Order
        order = Order(user_id=current_user.id, total_price=total, status='Completed')
        db.session.add(order)
        db.session.flush() # Get ID
        
        for item in cart_items:
            # Check stock again
            if item.product.stock < item.quantity:
                flash(f'Not enough stock for {item.product.name}.', 'danger')
                db.session.rollback()
                return redirect(url_for('cart'))
            
            # Deduct Stock
            item.product.stock -= item.quantity
            
            # Create Order Item
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
            db.session.add(order_item)
            db.session.delete(item) # Remove from cart
            
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    
    products = Product.query.paginate(page=request.args.get('page', 1, type=int), per_page=20)
    return render_template('admin.html', products=products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
