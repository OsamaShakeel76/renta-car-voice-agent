with open("fresh_schema.txt", "rb") as f:
    content = f.read()
    # Detect if it's UTF-16
    try:
        text = content.decode('utf-16')
    except:
        text = content.decode('utf-8', errors='ignore')
    print(text)
