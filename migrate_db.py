import sqlite3
import os

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')
print(f"Connecting to {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if base_salary exists
    cursor.execute("PRAGMA table_info(faculty)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns in faculty: {columns}")
    
    if 'base_salary' not in columns:
        print("Adding base_salary column to faculty table...")
        cursor.execute("ALTER TABLE faculty ADD COLUMN base_salary FLOAT DEFAULT 50000.0")
        conn.commit()
    else:
        print("base_salary column already exists.")

    # Also check if new tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Current tables: {tables}")
    
    # For simplicity, if we are missing columns/tables, it's better to just ensure they are there
    # But since create_all doesn't update, we manually add others if needed
    
    required_tables = ['exam_schedules', 'staff_attendance', 'staff_salaries']
    for table in required_tables:
        if table not in tables:
            print(f"Warning: Table {table} is missing. You might need to restart the app or reset the DB.")

    conn.close()
    print("Migration check complete.")
except Exception as e:
    print(f"Error: {e}")
