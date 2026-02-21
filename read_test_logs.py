with open("test_logs.txt", "rb") as f:
    content = f.read()
    try:
        text = content.decode('utf-16')
    except:
        text = content.decode('utf-8', errors='ignore')
    print(text)
