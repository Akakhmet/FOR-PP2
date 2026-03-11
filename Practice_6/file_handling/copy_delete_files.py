import shutil
import os

# Copy file
shutil.copy("sample.txt", "backup_sample.txt")
print("File copied")

# Delete backup safely
if os.path.exists("backup_sample.txt"):
    os.remove("backup_sample.txt")
    print("Backup deleted")
else:
    print("File does not exist")