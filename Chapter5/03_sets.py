s = {1, 5, 7, 7, 8, 8, "Chethan"} # the output would be 8, 1, 5, 7 (unordered)

#set is a collection of non-repitive objects /elements

e = set() #is an empty set Dont use s ={} as an empty set as it will create an empty dictionary 

s.add(566)
print(s, type(s))
print(len(s))

s.remove(7)
print(s)

s.pop()
print(s)

s.clear()
print(s)