#1
import math

deg = float(input())
rad = deg * math.pi/180
print(rad)

#2
h = float(input())
a =float(input())
b = float(input())

area = 0.5*(a+b)*h
print(area)

#3
import math
ns = int(input())
lofs = float(input())
area = (ns * lofs**2)/(4*math.tan(math.pi/ns))
print(round(area))

#4
a = float(input())
h = float(input())
area = a*h
print(area)