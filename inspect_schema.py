import sqlite3

def check_schema():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(bookings)")
    columns = cursor.fetchall()
    print("Columns in 'bookings' table:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
