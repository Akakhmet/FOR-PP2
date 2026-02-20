import json

data = {
    "name": "Ali",
    "age": 18
}

# Python → JSON
json_string = json.dumps(data)
print(json_string)

# JSON → Python
parsed = json.loads(json_string)
print(parsed["name"])

# Запись в файл
with open("output.json", "w") as f:
    json.dump(data, f)