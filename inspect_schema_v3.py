import sqlite3

def check_structure():
    conn = sqlite3.connect("rentacar.db")
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    for table_name in [t[0] for t in tables]:
        print(f"\nSchema for {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        for col in cursor.fetchall():
            print(col)
            
    conn.close()

if __name__ == "__main__":
    check_structure()
