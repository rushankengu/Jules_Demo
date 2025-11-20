import sqlite3
import os

DB_PATH = 'shop.db'

def count_products():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM product")
        count = cursor.fetchone()[0]
        print(f"Total products: {count}")
        
        # Also get a few sample names to see what we are dealing with
        cursor.execute("SELECT name FROM product LIMIT 5")
        samples = cursor.fetchall()
        print("Sample products:")
        for s in samples:
            print(f"- {s[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    count_products()
