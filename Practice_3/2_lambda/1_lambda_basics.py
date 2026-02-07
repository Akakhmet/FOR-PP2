# --- Code 1: simple lambda ---

square = lambda x: x * x

print(square(5))
print(square(10))

# --- Code 2: lambda with two parameters ---

add = lambda a, b: a + b

print(add(3, 4))
print(add(10, 20))

# --- Code 3: lambda with if-else ---

maximum = lambda a, b: a if a > b else b

print(maximum(7, 3))
print(maximum(2, 9))
