import sqlite3
import pandas as pd
import os
from werkzeug.security import generate_password_hash
from app import app, db, User, Product

# Path to the data file
DATA_PATH = 'data_cleaned.csv'

def seed_database():
    print(f"Checking data file at {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print(f"Error: File not found at {DATA_PATH}. Please ensure the data file is present.")
        return

    with app.app_context():
        print("Creating tables...")
        db.create_all()

        if Product.query.first():
            print("Products already exist. Skipping seed.")
            return

        print("Loading data...")
        df = pd.read_csv(DATA_PATH)
        
        # Rename columns to match DB schema
        df.rename(columns={
            'product': 'name',
            'sale_price': 'price',
            'Stockquantity': 'stock',
            'category': 'category_raw', 
            'sub_category': 'sub_category_raw',
            'type': 'type_raw'
        }, inplace=True)

        def clean_list_string(s):
            if isinstance(s, str) and s.startswith('[') and s.endswith(']'):
                try:
                    import ast
                    val = ast.literal_eval(s)
                    if isinstance(val, list):
                        return ", ".join(val).title()
                except:
                    pass
            return s

        print("Processing data...")
        products_to_add = []
        
        # Iterating might be slow but safe for ORM. 
        # For bulk insert we could use db.session.bulk_insert_mappings but we need to process rows.
        # Let's use pandas to apply then to_dict
        
        df['category'] = df['category_raw'].apply(clean_list_string)
        df['sub_category'] = df['sub_category_raw'].apply(clean_list_string)
        df['type'] = df['type_raw'].apply(clean_list_string)
        
        # Fill NaN
        df = df.fillna({'market_price': 0, 'rating': 0, 'description': '', 'stock': 0})

        for _, row in df.iterrows():
            product = Product(
                name=row['name'],
                category=row['category'],
                sub_category=row['sub_category'],
                brand=row['brand'],
                price=row['price'],
                market_price=row['market_price'],
                type=row['type'],
                rating=row['rating'],
                description=row['description'],
                stock=row['stock'],
                image_url='https://via.placeholder.com/150', # Placeholder
                soup=row.get('soup', '')
            )
            products_to_add.append(product)
        
        print(f"Inserting {len(products_to_add)} products...")
        db.session.bulk_save_objects(products_to_add)
        
        # Create Admin User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin'), is_admin=True)
            db.session.add(admin)
            print("Admin user created (admin/admin).")

        db.session.commit()
        print("Database seeded successfully.")

if __name__ == '__main__':
    seed_database()
