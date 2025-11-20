import sqlite3
import os

DB_PATH = 'shop.db'

# Mapping from app.py home route
# Ensure these filenames exist in static/img/
CATEGORY_IMAGES = {
    'Beauty, Hygiene': 'beauty2.jpg',
    'Kitchen, Garden, Pets': 'kitchen.png',
    'Bakery, Cakes, Dairy': 'bakery.png',
    'Snacks, Brandedfoods': 'snacks.jpeg',
    'Gourmet, Worldfood': 'Goumet.png',
    'Cleaning, Household': 'cleaning_image_url.jpg',
    'Beverages': 'beverages_image_url.jpg',
    'Foodgrains, Oil, Masala': 'Food.png',
    'Babycare': 'Baby.png'
}

def assign_images():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Updating product images...")
        for category, filename in CATEGORY_IMAGES.items():
            # Construct the path we want to store in DB
            # Assuming templates use src="{{ product.image_url }}"
            # We'll use an absolute path from root
            image_path = f"/static/img/{filename}"
            
            # Update products in this category
            cursor.execute("UPDATE product SET image_url = ? WHERE category = ?", (image_path, category))
            print(f"Updated category '{category}' to use '{image_path}'. Rows affected: {cursor.rowcount}")
            
        conn.commit()
        print("Update complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    assign_images()
