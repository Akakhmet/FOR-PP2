# --- Code 1: sort by absolute value ---

numbers = [-10, 5, -3, 2]

sorted_numbers = sorted(numbers, key=lambda x: abs(x))

print(sorted_numbers)


# --- Code 2: sort by word length ---

words = ["apple", "hi", "banana", "cat"]

sorted_words = sorted(words, key=lambda w: len(w))

print(sorted_words)

# --- Code 3: sort by second element ---

students = [("Ali", 20), ("Dana", 18), ("Aruzhan", 19)]

sorted_students = sorted(students, key=lambda s: s[1])

print(sorted_students)
