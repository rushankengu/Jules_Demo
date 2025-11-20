import sqlite3
import os

DB_PATH = 'shop.db'

def list_categories():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT category FROM product")
        categories = cursor.fetchall()
        print("Categories in DB:")
        for c in categories:
            print(f"'{c[0]}'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_categories()
