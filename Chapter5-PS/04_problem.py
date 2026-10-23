s = set()
s.add(20)
s.add(20.0) #20.0 == 20 TRUE in python (if value is same then data type doesn't matter)
s.add('20') # length of s after these operations?

print(len(s))
