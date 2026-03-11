# Read file contents

with open("sample.txt", "r") as f:
    print("Full file content:")
    print(f.read())

with open("sample.txt", "r") as f:
    print("First line:")
    print(f.readline())

with open("sample.txt", "r") as f:
    print("All lines as list:")
    print(f.readlines())