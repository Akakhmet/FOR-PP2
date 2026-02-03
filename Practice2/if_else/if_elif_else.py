
score = int(input("Score (0–100): "))

if score < 0 or score > 100:
    result = "Invalid score"
elif score >= 90:
    result = "Excellent"
elif score >= 75:
    result = "Good"
elif score >= 60:
    result = "Satisfactory"
else:
    result = "Fail"

print("Result:", result)
