name = "chethan"
print(len(name))
print(name.endswith("an"))
print(name.startswith("Che")) #case sensitive
print(name.capitalize()) #Capitalize first letter


# ===========================================================
# PYTHON STRING FUNCTIONS - COMPLETE BEGINNER GUIDE
# ===========================================================

# A string is a sequence of characters enclosed in quotes.
# Strings are IMMUTABLE, which means they cannot be changed
# after they are created.

text = "  Hello Python World  "

print("Original String:", repr(text))
# repr() shows the string exactly as it is, including spaces.


# ===========================================================
# 1. len() -> Returns the number of characters
# ===========================================================

print("\n1. Length of the string")
print(len(text))
# Output: 22
# Spaces are also counted.


# ===========================================================
# 2. lower() -> Converts every letter to lowercase
# ===========================================================

print("\n2. lower()")
print(text.lower())



# ===========================================================
# 3. upper() -> Converts every letter to uppercase
# ===========================================================

print("\n3. upper()")
print(text.upper())



# ===========================================================
# 4. title() -> Capitalizes the first letter of every word
# ===========================================================

print("\n4. title()")
print(text.title())



# ===========================================================
# 5. capitalize() -> Capitalizes only the first character
# ===========================================================

print("\n5. capitalize()")
print(text.capitalize())



# ===========================================================
# 6. strip() -> Removes spaces from both sides
# ===========================================================

print("\n6. strip()")
print(text.strip())



# ===========================================================
# 7. lstrip() -> Removes spaces only from the left
# ===========================================================

print("\n7. lstrip()")
print(text.lstrip())



# ===========================================================
# 8. rstrip() -> Removes spaces only from the right
# ===========================================================

print("\n8. rstrip()")
print(text.rstrip())



# ===========================================================
# 9. replace(old, new)
# Replaces one substring with another.
# ===========================================================

print("\n9. replace()")
print(text.replace("Python", "Java"))



# ===========================================================
# 10. split()
# Splits a string into a list.
# By default, it splits on spaces.
# ===========================================================

print("\n10. split()")

sentence = "Python is easy to learn"

words = sentence.split()

print(words)



# ===========================================================
# 11. join()
# Joins list elements into one string.
# ===========================================================

print("\n11. join()")

languages = ["Python", "Java", "C++"]

print("-".join(languages))
print(" ".join(languages))
print(",".join(languages))



# ===========================================================
# 12. find()
# Returns the first index of a substring.
# Returns -1 if not found.
# ===========================================================

print("\n12. find()")

print(sentence.find("easy"))
print(sentence.find("Java"))



# ===========================================================
# 13. index()
# Similar to find(), but gives an error if not found.
# ===========================================================

print("\n13. index()")

print(sentence.index("easy"))

# Uncomment to see the error
# print(sentence.index("Java"))



# ===========================================================
# 14. count()
# Counts how many times a substring appears.
# ===========================================================

print("\n14. count()")

fruit = "banana"

print(fruit.count("a"))
print(fruit.count("na"))



# ===========================================================
# 15. startswith()
# Checks whether a string starts with given text.
# ===========================================================

print("\n15. startswith()")

print(sentence.startswith("Python"))
print(sentence.startswith("Java"))



# ===========================================================
# 16. endswith()
# Checks whether a string ends with given text.
# ===========================================================

print("\n16. endswith()")

print(sentence.endswith("learn"))
print(sentence.endswith("easy"))



# ===========================================================
# 17. isalpha()
# Returns True if every character is a letter.
# No spaces, numbers, or symbols allowed.
# ===========================================================

print("\n17. isalpha()")

print("Hello".isalpha())
print("Hello123".isalpha())



# ===========================================================
# 18. isdigit()
# Returns True only if every character is a digit.
# ===========================================================

print("\n18. isdigit()")

print("12345".isdigit())
print("12A45".isdigit())



# ===========================================================
# 19. isalnum()
# Returns True if string contains only letters and numbers.
# ===========================================================

print("\n19. isalnum()")

print("Python3".isalnum())
print("Python 3".isalnum())



# ===========================================================
# 20. isspace()
# Returns True if every character is a whitespace.
# ===========================================================

print("\n20. isspace()")

print("     ".isspace())
print("  A  ".isspace())



# ===========================================================
# 21. islower()
# Checks if every letter is lowercase.
# ===========================================================

print("\n21. islower()")

print("python".islower())
print("Python".islower())



# ===========================================================
# 22. isupper()
# Checks if every letter is uppercase.
# ===========================================================

print("\n22. isupper()")

print("PYTHON".isupper())
print("Python".isupper())



# ===========================================================
# 23. swapcase()
# Converts uppercase to lowercase and vice versa.
# ===========================================================

print("\n23. swapcase()")

print("PyThOn".swapcase())



# ===========================================================
# 24. center(width)
# Places the string in the center by adding spaces.
# ===========================================================

print("\n24. center()")

print("Python".center(20, "*"))



# ===========================================================
# 25. zfill(width)
# Adds zeros at the beginning until the required width.
# Mostly used for IDs and numbers.
# ===========================================================

print("\n25. zfill()")

print("45".zfill(5))



# ===========================================================
# STRING SLICING
# One of the MOST IMPORTANT topics in Python.
# ===========================================================

print("\n========== STRING SLICING ==========")

word = "Python"

print(word[0])      # First character
print(word[1])      # Second character
print(word[-1])     # Last character
print(word[-2])     # Second last character

print(word[0:4])    # Characters from index 0 to 3
print(word[:3])     # Beginning to index 2
print(word[2:])     # Index 2 to end

print(word[::2])    # Every second character

print(word[::-1])   # Reverse the string



# ===========================================================
# MEMBERSHIP OPERATORS
# ===========================================================

print("\n========== MEMBERSHIP ==========")

print("Python" in sentence)
print("Java" in sentence)

print("Java" not in sentence)



# ===========================================================
# STRING FORMATTING
# ===========================================================

print("\n========== FORMATTING ==========")

name = "Alice"
age = 25

# Modern and recommended way
print(f"{name} is {age} years old.")

# Older method
print("{} is {} years old.".format(name, age))

# Very old method
print("%s is %d years old." % (name, age))



# ===========================================================
# PRACTICE PROGRAMS
# ===========================================================

print("\n========== PRACTICE ==========")

# Reverse a string
text = "Programming"

print("Reverse:", text[::-1])



# Count vowels
vowels = "aeiou"

count = 0

for ch in text.lower():
    if ch in vowels:
        count += 1

print("Vowel Count:", count)



# Check palindrome
word = "madam"

if word == word[::-1]:
    print(word, "is a palindrome")
else:
    print(word, "is not a palindrome")



# Remove spaces
sentence = "Python is fun"

print(sentence.replace(" ", ""))



# Count words
sentence = "Python is easy to learn"

print("Number of words:", len(sentence.split()))