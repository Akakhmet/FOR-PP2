# --- Code 1: Function with one argument ---

def greet(name):
    print("Hello,", name)

# function calls
greet("Ali")
greet("Dana")


# --- Code 2: Function with two arguments ---

def add(a, b):
    print("Sum:", a + b)

add(5, 3)
add(10, 7)

# --- Code 3: Function with default argument ---

def power(number, exponent=2):
    print(number ** exponent)

power(4)      # exponent = 2 (default)
power(4, 3)   # exponent = 3 (custom)


# --- Code 3: Function with default argument ---

def power(number, exponent=2):
    print(number ** exponent)

power(4)      # exponent = 2 (default)
power(4, 3)   # exponent = 3 (custom)
