# --- Code 1: filter even numbers ---

numbers = [1, 2, 3, 4, 5, 6]

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print(even_numbers)

# --- Code 2: filter numbers > 10 ---

numbers = [5, 12, 8, 20, 3, 15]

result = list(filter(lambda x: x > 10, numbers))

print(result)


# --- Code 3: filter long words ---

words = ["hi", "python", "cat", "student"]

long_words = list(filter(lambda w: len(w) > 3, words))

print(long_words)

