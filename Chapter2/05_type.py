a = 25
result = type(a)
print(result)
b = 3.14
print(type(b))
c = "Hello, World!"
print(type(c))
d = True
print(type(d))
e = None
print(type(e))


a = "25.32"
b = str(a) # This will convert the string "25.32" to a string, which is redundant but valid
result = type(a) # This will return <class 'str'>, because a is already a string
print(result)

