marks = {
    "Chethan": 97,
    "Arjun": 100,
    "Amrutha": 100,
    "list": [1, 3, 7]
}

# print(marks)
# print(marks.items())
# print(marks.key())
# print(marks.values())


marks.update({"Arjun":99})

print(marks["Arjun"])
print(marks.get("Arjun")) # useful if the key doesn't exists the funtion returns none but the above will give an error

print(marks["Arjun5"]) # error
print(marks.get("Arjun5")) #prints none 