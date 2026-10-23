# # # # # # # # word = "malayalam"
# # # # # # # # print(word == word[::-1])


# # # # # # # # sentence = "Python is fun"
# # # # # # # # print(sentence.replace(" ",""))

# # # # # # # # print(sentence.split())

# # # # # # # # print(len(sentence))

# # # # # # # raw = "2026-07-25"
# # # # # # # divide =  raw.split("-")
# # # # # # # divide.reverse()
# # # # # # # print("/".join(divide))

# # # # # # # sentence = "learn    python    the    easy    way"
# # # # # # # # print(sentence.replace("  ", " ")) replace("  ", " ") swaps two spaces for one, scanning left to right without overlapping. Between your words there are 4 spaces:


# # # # # # # words = sentence.split()
# # # # # # # print(" ".join(words))



# # # # # # csv = "apple,banana,cherry,mango"
# # # # # # words = csv.split(",")
# # # # # # # for word in words:
# # # # # # #     print(word)
# # # # # # print("\n".join(words))


# # # # # path = "home/chethan/documents/python"
# # # # # words = (path.split("/"))
# # # # # print(words[-1])

# # # # year = "2026"
# # # # month = "07"
# # # # day = "25"

# # # # date = [year, month, day]
# # # # print("-".join(date))

# # # # name = "chethan bhat"
# # # # word = name.split(" ")
# # # # print(".".join(word))


# # # sentence = "python is fun"
# # # words = sentence.split(" ")
# # # words.reverse()
# # # print(" ".join(words))
# # # # print(" ".join(test))
# # # # print(words[-1:])
# # # # print(words.reverse())

# # # email = "chethan@emergent.sh"
# # # word = email.split("@")
# # # print(word[1])



# # sentence = "learn python programming today"
# # words = sentence.split()
# # print(" ".join(words[0:2]))

# colors = ["red", "green", "blue"]
# print("Red" in colors)
# print("green" in colors)
# # colors.remove("yellow")
# print(colors)

nums = [10, 20, 30]
nums2 = nums
nums = nums + [40]
print(nums)
print(nums2)