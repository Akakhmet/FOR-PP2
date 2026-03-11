# Create and write to a file

with open("sample.txt", "w") as f:
    f.write("Hello Python\n")
    f.write("File handling practice\n")

print("File created and written successfully")