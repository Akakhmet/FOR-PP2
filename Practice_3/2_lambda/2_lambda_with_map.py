# --- Code 1: square numbers ---

numbers = [1, 2, 3, 4]

squared = list(map(lambda x: x * x, numbers))

print(squared)


# --- Code 2: multiply by 10 ---

numbers = [5, 7, 9]

result = list(map(lambda x: x * 10, numbers))

print(result)


# --- Code 3: convert to uppercase ---

words = ["hello", "python", "student"]

upper_words = list(map(lambda word: word.upper(), words))

print(upper_words)
