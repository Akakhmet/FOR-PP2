# --- Code 1: return simple value ---

def add(a, b):
    return a + b

result = add(5, 3)

print("Result:", result)



# --- Code 2: return boolean value ---

def is_even(number):
    return number % 2 == 0

print(is_even(10))
print(is_even(7))


# --- Code 3: return multiple values ---

def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([4, 7, 1, 9, 3])

print("Min:", minimum)
print("Max:", maximum)
