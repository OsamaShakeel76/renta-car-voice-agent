import sqlite3

def check_structure():
    conn = sqlite3.connect("rentacar.db")
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    for table_name in [t[0] for t in tables]:
        print(f"\n--- Schema for {table_name} ---")
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()
        for col in cols:
            # col is (id, name, type, notnull, default_value, pk)
            print(f"Col {col[0]}: {col[1]} ({col[2]})")
            
    conn.close()

if __name__ == "__main__":
    check_structure()
