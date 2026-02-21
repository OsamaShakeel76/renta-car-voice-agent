with open("test_output.txt", "rb") as f:
    content = f.read()
    try:
        text = content.decode('utf-16')
    except:
        text = content.decode('utf-8', errors='ignore')
    print(text)
