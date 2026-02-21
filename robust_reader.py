import os

def read_logs():
    for filename in ["test_logs.txt", "test_logs_utf8.txt"]:
        if os.path.exists(filename):
            print(f"--- {filename} ---")
            with open(filename, "rb") as f:
                data = f.read()
                # Try multiple decodings
                for enc in ['utf-16', 'utf-8', 'latin-1']:
                    try:
                        print(data.decode(enc))
                        break
                    except:
                        continue

if __name__ == "__main__":
    read_logs()
