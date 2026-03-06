import re

text = "Hello 123 world!\nPython is FUN.\nEmail: test123@mail.com"

#Metacharacters

# . (any character except newline)
print("Dot (.):", re.findall(r"H.llo", text))

# * (0 or more)
print("Star (*):", re.findall(r"lo*", text))

# + (1 or more)
print("Plus (+):", re.findall(r"\d+", text))



# Special Sequences 

print(r"\d:", re.findall(r"\d", text))
print(r"\w:", re.findall(r"\w", text))
print(r"\s:", re.findall(r"\s", text))
print(r"\D:", re.findall(r"\D", text))
print(r"\W:", re.findall(r"\W", text))


# Function 

# re.search()
match = re.search(r"Python", text)
print("search():", match.group() if match else None)

# re.findall()
print("findall():", re.findall(r"\d+", text))

# re.split()
print("split():", re.split(r"\s", text))

# re.sub()
print("sub():", re.sub(r"FUN", "awesome", text))

# re.match() (matches only at beginning)
print("match():", re.match(r"Hello", text))

# Flags 

# IGNORECASE
print("IGNORECASE:", re.findall(r"python", text, re.IGNORECASE))

# MULTILINE
print("MULTILINE:", re.findall(r"^Python", text, re.MULTILINE))