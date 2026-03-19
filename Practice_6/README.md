# Practice6 🚀
## File Handling and Built-in Functions in Python

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Practice](https://img.shields.io/badge/Practice-6-orange)
![GitHub](https://img.shields.io/badge/Repo-Active-black?logo=github)

---

## 📌 Objective
This project demonstrates working with files, directories, and built-in functions in Python.

The main goals:
- Learn file handling (read, write, append)
- Work with directories and file paths
- Use built-in functions for data processing
- Practice real-world Python operations

---

## 📁 Project Structure

```text
Practice6/
│
├── sample.txt
│
├── file_handling/
│   ├── read_files.py
│   ├── write_files.py
│   └── copy_delete_files.py
│
├── directory_management/
│   ├── create_list_dirs.py
│   └── move_files.py
│
├── builtin_functions/
│   ├── map_filter_reduce.py
│   └── enumerate_zip_examples.py
```

---

## 📂 File Handling

### Supported Modes:
- `r` – read
- `w` – write (overwrite)
- `a` – append
- `x` – create new file

### Reading Methods:
- `read()` – full file
- `readline()` – one line
- `readlines()` – list of lines

### Example:
```python
with open("sample.txt", "r") as f:
    print(f.read())
```

---

## 📁 Directory Management

Functions used:
- `os.mkdir()` – create directory
- `os.makedirs()` – nested directories
- `os.listdir()` – list files
- `os.getcwd()` – current directory
- `os.chdir()` – change directory
- `os.rmdir()` – remove directory

---

## 📦 File Operations

Using `shutil` module:
- Copy files
- Move files
- Backup files

### Example:
```python
import shutil
shutil.copy("sample.txt", "backup.txt")
```

---

## 🔢 Built-in Functions

### Used functions:
- `len()`, `sum()`, `min()`, `max()`
- `map()`, `filter()`, `reduce()`
- `enumerate()`, `zip()`
- `sorted()`
- Type conversion: `int()`, `float()`, `str()`

### Example:
```python
from functools import reduce

nums = [1,2,3,4]

print(sum(nums))
print(list(map(lambda x: x*2, nums)))
print(reduce(lambda a,b: a+b, nums))
```

---

## 📊 Sample Data

File: `sample.txt`

```text
1 2 3 4 5
```

---

## 🚀 How to Run

1. Open project in VS Code  
2. Run any file:

```bash
python filename.py
```

---

## ✅ Conclusion

This project covers:
- File handling basics
- Directory operations
- Core Python built-in functions

It builds a strong foundation for real-world Python development.

---

## 💡 Author

Student Practice Work - Python Fundamentals