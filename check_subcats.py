import sqlite3
import os

DB_PATH = 'shop.db'

def count_subcategories():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(DISTINCT sub_category) FROM product")
        count = cursor.fetchone()[0]
        print(f"Total unique sub-categories: {count}")
        
        cursor.execute("SELECT DISTINCT sub_category FROM product LIMIT 10")
        samples = cursor.fetchall()
        print("Sample sub-categories:")
        for s in samples:
            print(f"- {s[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    count_subcategories()
