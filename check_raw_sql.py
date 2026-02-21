import sqlite3

def check_raw_sql():
    conn = sqlite3.connect("rentacar.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"Raw Row: {row}")
            # Get column names
            cursor.execute("PRAGMA table_info(bookings)")
            cols = [c[1] for c in cursor.fetchall()]
            print(f"Columns: {cols}")
            for name, val in zip(cols, row):
                print(f"{name}: {val}")
        else:
            print("No rows found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_raw_sql()
