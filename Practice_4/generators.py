def my_generator():
    for i in range(5):
        yield i

for value in my_generator():
    print(value)