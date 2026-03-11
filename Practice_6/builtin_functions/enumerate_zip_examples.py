names = ["Ali","John","Sara"]
scores = [90,85,88]

# enumerate
for i,name in enumerate(names):
    print(i, name)

# zip
for name,score in zip(names, scores):
    print(name, score)

# sorted
print(sorted(scores))

# type conversion
a = "123"
print(int(a))
print(float(a))
print(str(456))