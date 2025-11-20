import sqlite3
import os

DB_PATH = 'shop.db'

def verify_images():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name, category, image_url FROM product LIMIT 5")
        samples = cursor.fetchall()
        print("Sample products after update:")
        for s in samples:
            print(f"Product: {s[0]}")
            print(f"Category: {s[1]}")
            print(f"Image URL: {s[2]}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_images()
