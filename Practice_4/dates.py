import datetime

x = datetime.datetime.now()
print(x)
print(x.year)
print(x.strftime("%A"))
print(x.strftime("%a"))
print(x.strftime("%W"))

import datetime
x = datetime.datetime(2020, 5 , 17)
print(x)

#1
from datetime import datetime, timedelta

today = datetime.now()
new_date = today - timedelta(days = 5)
print(new_date)

#2
from datetime import datetime, timedelta
yesterday = today - timedelta(days = 1)
today = datetime.now()
tomorrow = today + timedelta(days =1)
print(yesterday)
print(today)
print(tomorrow)

#3
import datetime
now = datetime.datetime.now()
print(now.replace(microsecond=0))

#4
import datetime
d1 = datetime.datetime.strptime(input(),"%Y-%m-%d %H:%M:%S")
d2 = datetime.datetime.strptime(input(),"%Y-%m-%d %H:%M:%S")
print(int(abs(d2-d1).total_seconds()))