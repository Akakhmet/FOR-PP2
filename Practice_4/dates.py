from datetime import datetime

now = datetime.now()
print("Current time:", now)

formatted = now.strftime("%Y-%m-%d %H:%M")
print("Formatted:", formatted)

birthday = datetime(2006, 5, 1)
difference = now - birthday
print("Days lived:", difference.days)