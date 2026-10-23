# 2. Write a program to fill in a letter template given below with name and date.
# letter = '''
# Dear <|Name|>,
# You are selected!
# <|Date|>
# '''

# name = input("Enter your name")
# date = "02/07/2027"

# print(f'''
# Dear {name},
# You are selected!
# {date}
# ''')


# OR

letter = '''
Dear <|Name|>,
 You are selected!
 <|Date|>
'''


print(letter.replace('<|Name|>', 'Chethan Bhat').replace('<|Date|>','01/08/2027'))