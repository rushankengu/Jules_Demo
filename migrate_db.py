"""
Database migration script to update the Order table with new shipping fields
"""
import sqlite3
import os

# Path to the database
DB_PATH = 'shop.db'

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info('order')")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = [
            ('first_name', 'VARCHAR(100)'),
            ('last_name', 'VARCHAR(100)'),
            ('address', 'VARCHAR(300)'),
            ('country', 'VARCHAR(100)'),
            ('state', 'VARCHAR(100)'),
            ('zip_code', 'VARCHAR(20)'),
            ('payment_method', 'VARCHAR(50)')
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding column: {col_name}")
                cursor.execute(f"ALTER TABLE 'order' ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column {col_name} already exists, skipping...")
        
        conn.commit()
        print("\\nDatabase migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
