import os

# Create directory
os.mkdir("test_dir")

# Create nested directories
os.makedirs("parent/child/grandchild", exist_ok=True)

# List files
print("Current directory contents:")
print(os.listdir())

# Current working directory
print("Current path:", os.getcwd())