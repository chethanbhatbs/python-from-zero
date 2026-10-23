# 2. Write a program to accept marks of 6 students and display them in a sorted manner.
# 1. Write a program to store seven marks in a list entered by the user.
marks = []
f1 = int(input("Enter the marks: "))
marks.append(f1)
f2 = int(input("Enter the marks: "))
marks.append(f2)
f3 = int(input("Enter the marks: "))
marks.append(f3)
f4 = int(input("Enter the marks: "))
marks.append(f4)
f5 = int(input("Enter the marks: ")) #if int is not added then the result would be string and string is sorted alphabbetically
marks.append(f5)

marks.sort() 

print(marks)

