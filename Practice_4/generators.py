mytuple = ("apple", "banana", "cherry")
myit = iter(mytuple)
print(next(myit))
print(next(myit))
print(next(myit))



mystr = "banana"
myit = iter(mystr)
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))
print(next(myit))

mytuple = ("apple", "banana", "cherry")
for x in mytuple:
  print(x)

mystr = "banana"
for x in mystr:
  print(x)



class MyNumbers:
  def __iter__(self):
    self.a = 1
    return self
  
  def __next__(self):
    x = self.a
    self.a += 1
    return x
  

myclass = MyNumbers()
myiter = iter(myclass)

print(next(myiter))
print(next(myiter))
print(next(myiter))

class MyNumbers:
  def __iter__(self):
    self.a =1
    return self
  
  def __next__(self):
    if self.a <= 20:
      x = self.a 
      self.a += 1
      return x
    else:
      raise StopIteration
    
myclass = MyNumbers()
myiter = iter(myclass)

for x in myiter:
  print(x)




def fun(max):
  cnt = 1
  while cnt <= max:
    yield cnt
    cnt += 1

n = int(input())
ctr = fun(n)

for n in ctr:
  print(n)

#1
n = int(input())
def sq(n):
    for x in range(1,n+1):
        yield x*x

for i in sq(n):
    print(i)

#2
n = int(input())
def evns(n):
    for x in range(0,n+1):
        if x % 2 == 0:
            yield x

print(",".join(str(i) for i in evns(n)))

#3
def fun(n):
    for x in range(0,n+1):
        if (x % 3 == 0 and x % 4 == 0):
            yield x
n = int(input())
for i in fun(n):
    print(i)

#4
a,b = map(int, input().split())
gen = (x*x for x in range(a,b+1))

for i in gen:
   print(i)


#5
def oncontr(n):
    for x in range(n,-1,-1):
        yield x
n = int(input())
for i in oncontr(n):
    print(i)