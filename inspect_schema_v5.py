import sqlite3

def check_structure():
    conn = sqlite3.connect("rentacar.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(bookings)")
    cols = cursor.fetchall()
    print("Columns in 'bookings':")
    for col in cols:
        print(f"{col[0]}: {col[1]} ({col[2]})")
    conn.close()

if __name__ == "__main__":
    check_structure()
