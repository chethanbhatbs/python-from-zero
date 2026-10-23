"""Quiz questions, break-it challenges and modules for the Python course.

Plain data only. build.py runs every code question to find the real answer,
so no answer here is typed by hand except the multiple-choice ones.

Question types:
  mcq    - q, choices, answer (index), why
  output - code that must run; the learner types what it prints
  error  - code; the learner picks "Works" or the error it raises
"""

MODULES = [
    ("1", "Foundations", "Before any code: what programming is, what Python is, and how Python runs your file.", ["0", "1", "2"], 15),
    ("2", "First code", "Print, comment, import, store values in names, and do maths with them.", ["3", "4"], 20),
    ("3", "Text", "Work with strings: positions, slices, and every string method.", ["5"], 15),
    ("4", "Collections", "Hold many values: lists, tuples, dictionaries and sets.", ["6", "7"], 25),
]

QUIZ = {
    "0": [
        {"type": "mcq", "q": "What is a program?",
         "choices": ["A list of exact steps for a computer to follow", "A website", "A kind of computer", "A file of pictures"],
         "answer": 0, "why": "A program is exact steps, done in order, like a recipe."},
        {"type": "mcq", "q": "A recipe says \"2. Add sugar. 1. Boil water.\" What does a computer do with steps like these?",
         "choices": ["Runs them in the order written", "Fixes the order for you", "Refuses to start", "Skips the step it does not like"],
         "answer": 0, "why": "Computers never guess what you meant. They do exactly what is written, top to bottom."},
        {"type": "mcq", "q": "Why do we need a programming language at all?",
         "choices": ["Computers only understand machine code, and a language is something people can read that gets translated", "To make the computer faster", "Because English has too many words", "To draw the screen"],
         "answer": 0, "why": "You write readable code; Python translates it into instructions the machine runs."},
        {"type": "mcq", "q": "What is syntax?",
         "choices": ["The grammar rules of a language", "A type of error", "The output of a program", "A Python module"],
         "answer": 0, "why": "Break the grammar and Python cannot read the line, which is a SyntaxError."},
        {"type": "output", "code": 'print("Hi")'},
    ],
    "1": [
        {"type": "mcq", "q": "Who created Python?",
         "choices": ["Guido van Rossum", "Tim Berners-Lee", "Bill Gates", "Linus Torvalds"],
         "answer": 0, "why": "He started it at CWI in the Netherlands."},
        {"type": "mcq", "q": "Python is named after...",
         "choices": ["Monty Python's Flying Circus, a BBC comedy show", "The snake", "A Greek myth", "A computer company"],
         "answer": 0, "why": "From the official Python FAQ."},
        {"type": "mcq", "q": "What does \"interpreted\" mean for Python?",
         "choices": ["You run your .py file directly; no separate app is built first", "It translates English into Python", "It only runs on the internet", "It needs a compiler you run by hand"],
         "answer": 0, "why": "You type python3 file.py and it runs."},
        {"type": "mcq", "q": "A tutorial writes print \"Hello\" with no brackets. Which Python is it for?",
         "choices": ["Python 2, which was retired on 1 Jan 2020", "Python 3", "Both", "Neither"],
         "answer": 0, "why": "In Python 3 print needs brackets."},
        {"type": "error", "code": 'print "Hello"'},
    ],
    "2": [
        {"type": "error", "code": 'print("a")\nprint("b"'},
        {"type": "error", "code": 'print("line 1")\nprint(score)'},
        {"type": "error", "code": '  print("hi")'},
        {"type": "mcq", "q": "In an error message (traceback), which line do you read first?",
         "choices": ["The last line", "The first line", "The middle line", "None, just rerun it"],
         "answer": 0, "why": "The last line says the error type and the reason. Then look at the line number above it."},
        {"type": "mcq", "q": "print(\"line 1\") then a line with a missing bracket. How many lines print?",
         "choices": ["None: a SyntaxError stops the whole file before anything runs", "One", "Two", "It depends on the computer"],
         "answer": 0, "why": "Python checks the grammar of the whole file first."},
    ],
    "3": [
        {"type": "output", "code": 'print("a", "b", sep="-")'},
        {"type": "output", "code": 'print("x", end="")\nprint("y")'},
        {"type": "error", "code": 'print(hello)'},
        {"type": "error", "code": 'Print("hi")'},
        {"type": "output", "code": 'print("Price #1")  # a note'},
        {"type": "error", "code": "print('It's ok')"},
        {"type": "error", "code": 'import maths'},
        {"type": "error", "code": 'from math import sqrt\nprint(math.sqrt(4))'},
        {"type": "output", "code": 'print(1, 2, 3)'},
        {"type": "output", "code": 'print("one")\nprint()\nprint("two")'},
    ],
    "4": [
        {"type": "output", "code": 'print(7 // 2, 7 % 2)'},
        {"type": "output", "code": 'print(10 / 5)'},
        {"type": "error", "code": 'print("Age: " + 5)'},
        {"type": "error", "code": 'print(int("4.5"))'},
        {"type": "output", "code": 'x = 5\nx += 2\nprint(x)'},
        {"type": "output", "code": 'print(True and not False)'},
        {"type": "output", "code": 'a, b = 1, 2\na, b = b, a\nprint(a, b)'},
        {"type": "output", "code": 'print(f"{3 / 4:.2f}")'},
        {"type": "error", "code": '2nd = 5'},
        {"type": "output", "code": 'print(bool("0"))'},
        {"type": "error", "code": 'done = true'},
        {"type": "output", "code": 'print("5" + "5", 5 + 5)'},
    ],
    "5": [
        {"type": "output", "code": 'print("Python"[1:4])'},
        {"type": "output", "code": 'print("Python"[::-1])'},
        {"type": "output", "code": 'print("Python"[-2:])'},
        {"type": "error", "code": 's = "hi"\ns[0] = "H"'},
        {"type": "output", "code": 's = "hello"\ns.upper()\nprint(s)'},
        {"type": "output", "code": 'print("banana".find("z"))'},
        {"type": "error", "code": 'print("banana".index("z"))'},
        {"type": "output", "code": 'print("a,b,c".split(","))'},
        {"type": "error", "code": 'print(["a", "b"].join("-"))'},
        {"type": "output", "code": 'print("-".join(["a", "b"]))'},
        {"type": "output", "code": 'print("  hi  ".strip() + "!")'},
        {"type": "output", "code": 'print("12".isdigit(), "1.2".isdigit())'},
    ],
    "6": [
        {"type": "output", "code": 'l = [1, 2, 3]\nl[0] = 9\nprint(l)'},
        {"type": "error", "code": 'l = [1, 2, 3]\nprint(l[3])'},
        {"type": "output", "code": 'l = [3, 1, 2]\nprint(l.sort())'},
        {"type": "output", "code": 'l = [3, 1, 2]\nprint(sorted(l), l)'},
        {"type": "output", "code": 'a = [1]\nb = a\nb.append(2)\nprint(a)'},
        {"type": "output", "code": 'a = [1]\nb = a.copy()\nb.append(2)\nprint(a)'},
        {"type": "error", "code": 'l = [1, 2]\nl.remove(5)'},
        {"type": "error", "code": 'l = []\nl.pop()'},
        {"type": "error", "code": 't = (1, 2)\nt[0] = 5'},
        {"type": "output", "code": 't = (5)\nprint(type(t))'},
        {"type": "output", "code": 'print([1, 2] + [3])'},
        {"type": "error", "code": 'print([1, 2] + 3)'},
    ],
    "7": [
        {"type": "output", "code": 'd = {"a": 1}\nd["b"] = 2\nprint(d)'},
        {"type": "error", "code": 'd = {"a": 1}\nprint(d["b"])'},
        {"type": "output", "code": 'd = {"a": 1}\nprint(d.get("b", 0))'},
        {"type": "error", "code": 'd = {"a": 1}\nprint(d[0])'},
        {"type": "output", "code": 'print(len({1, 1, 2}))'},
        {"type": "output", "code": 'print(type({}))'},
        {"type": "error", "code": 's = {1, 2}\nprint(s[0])'},
        {"type": "error", "code": 'd = {[1]: "x"}'},
        {"type": "output", "code": 'print({1, 2, 3} & {2, 3, 4})'},
        {"type": "output", "code": 'd = {"a": 1}\nprint("a" in d, 1 in d)'},
        {"type": "output", "code": 'd = {"x": 1, "x": 2}\nprint(d)'},
    ],
}

# Break it: start from working code, change it so it raises the target error.
BREAKIT = {
    "2": [
        {"code": 'print("hello")', "target": "SyntaxError", "hint": "Remove one character.", "sol": 'print("hello"'},
        {"code": 'print("hello")', "target": "NameError", "hint": "What happens without quotes?", "sol": 'print(hello)'},
    ],
    "3": [
        {"code": 'import math\nprint(math.pi)', "target": "ModuleNotFoundError", "hint": "Misspell something on line 1.", "sol": 'import maths\nprint(math.pi)'},
        {"code": 'import math\nprint(math.pi)', "target": "NameError", "hint": "Capital letters matter.", "sol": 'import math\nprint(Math.pi)'},
    ],
    "4": [
        {"code": 'age = 30\nprint("Age:", age)', "target": "TypeError", "hint": "Join text and a number with +.", "sol": 'age = 30\nprint("Age: " + age)'},
        {"code": 'print(int("42"))', "target": "ValueError", "hint": "Give int() text that is not a whole number.", "sol": 'print(int("4.2"))'},
        {"code": 'print(10 / 2)', "target": "ZeroDivisionError", "hint": "Change one digit.", "sol": 'print(10 / 0)'},
    ],
    "5": [
        {"code": 'word = "Python"\nprint(word[0])', "target": "IndexError", "hint": "Ask for a position that does not exist.", "sol": 'word = "Python"\nprint(word[10])'},
        {"code": 'word = "Python"\nprint(word[0])', "target": "TypeError", "hint": "Try to change a letter.", "sol": 'word = "Python"\nword[0] = "J"'},
        {"code": 'print("a-b".split("-"))', "target": "ValueError", "hint": "Use an empty separator.", "sol": 'print("a-b".split(""))'},
    ],
    "6": [
        {"code": 'nums = [1, 2, 3]\nprint(nums[0])', "target": "IndexError", "hint": "Read past the end.", "sol": 'nums = [1, 2, 3]\nprint(nums[3])'},
        {"code": 'nums = [1, 2, 3]\nnums.remove(2)\nprint(nums)', "target": "ValueError", "hint": "Remove a value that is not there.", "sol": 'nums = [1, 2, 3]\nnums.remove(9)\nprint(nums)'},
        {"code": 'print(sorted([3, 1, 2]))', "target": "TypeError", "hint": "Mix numbers and text.", "sol": 'print(sorted([3, "a", 2]))'},
    ],
    "7": [
        {"code": 'd = {"a": 1}\nprint(d["a"])', "target": "KeyError", "hint": "Look up a key that is not there.", "sol": 'd = {"a": 1}\nprint(d["b"])'},
        {"code": 's = {1, 2}\nprint(1 in s)', "target": "TypeError", "hint": "Sets have no positions.", "sol": 's = {1, 2}\nprint(s[0])'},
        {"code": 'd = {"a": 1}\nprint(d)', "target": "TypeError", "hint": "Use a list as a key.", "sol": 'd = {["a"]: 1}\nprint(d)'},
    ],
}


# Key takeaways at the end of each chapter. Each line restates a rule the
# chapter teaches with a working and a breaking example.
TAKEAWAYS = {
    "0": [
        "A program is a list of exact steps. The computer runs them in order, top to bottom, and never guesses what you meant.",
        "Computers only understand machine code (0s and 1s). A programming language is readable text that gets translated for the machine.",
        "Syntax is the grammar of a language. Break it, and the program does not run.",
        "A mistake in code is a bug. Finding and fixing it is debugging.",
    ],
    "1": [
        "Python was created by Guido van Rossum, started over Christmas 1989 and shared in February 1991. It is named after Monty Python, not the snake.",
        "Interpreted: you run your file with python3 file.py. No separate app file is built.",
        "Compiled languages (C, Go, Rust) build an app first; Java compiles to bytecode that the JVM runs.",
        "Python quietly turns your code into bytecode and caches it in __pycache__, but you never run a build step.",
        "Always use Python 3. Python 2 was retired on 1 January 2020.",
    ],
    "2": [
        "The >>> prompt runs Python. Terminal commands like ls or clear do not work there; type exit() to leave.",
        "A SyntaxError stops the whole file before anything runs, even the lines above it.",
        "Any other error stops at its own line. The lines above it have already run.",
        "Read an error from the bottom up: error type and reason, then the line number and the ^ marks.",
        "Spaces at the start of a line matter, and each line holds one instruction.",
    ],
    "3": [
        "print() shows things on screen and always needs brackets.",
        "Text goes in quotes. Numbers, True, False, None and names you created do not.",
        "Commas print several things with a space between; sep and end change what goes between and after.",
        "Everything after # is a comment. Each comment line needs its own #.",
        "import a module before you use it, spell it exactly, and never name your own file after a module.",
    ],
    "4": [
        "= works out the right side first, then puts the name on the left onto the result.",
        "Names: letters, digits and _ only, no digit first, no keywords, and capitals make a different name.",
        "/ always gives a float; // keeps the whole part; % gives the remainder; ** is power.",
        "Text and numbers do not mix with +: convert with str() or int(), or use an f-string like f\"{x:.2f}\".",
        "input() always returns text. Convert it before doing maths.",
        "and, or and not combine True and False.",
    ],
    "5": [
        "Positions start at 0, and -1 is the last character.",
        "A slice [start:stop:step] stops BEFORE stop. A negative step walks backwards.",
        "Strings never change. Methods like upper() return a new string, so store it: name = name.upper().",
        "find() gives -1 when text is missing; index() raises ValueError.",
        "split() turns text into a list; \"glue\".join(list) turns a list back into text.",
        "in checks whether text contains something, and capital letters matter.",
    ],
    "6": [
        "A list is written [a, b, c], keeps its order and can change.",
        "Reading a position that does not exist, at either end, is an IndexError.",
        "append and insert add; remove deletes by value; pop deletes by position and gives the item back.",
        "list.sort() changes the list and returns None; sorted(list) returns a new list.",
        "b = a gives the same list a second name. Use a.copy() for a real copy.",
        "A tuple (a, b) cannot change. A one-item tuple needs a comma: (5,).",
    ],
    "7": [
        "A dictionary stores key: value pairs. d[key] fails with KeyError if the key is missing; d.get(key) does not.",
        "Assigning to a key adds it or replaces it. Keys are unique, and a list cannot be a key.",
        "in on a dictionary checks the keys, not the values.",
        "A set keeps each value once and has no positions.",
        "{} is an empty dictionary. Use set() for an empty set.",
        "Combine sets with | (either), & (both), - (only the first) and ^ (exactly one).",
    ],
}

# Part 1 cheat sheet: every result is produced by running the code at build time.
CHEAT = [
    ("Printing and text", [
        'print("Hi", 5, True)',
        'print("a", "b", sep="-")',
        'name = "Ravi"\nprint(f"Hi {name}")',
        'print(f"{3.14159:.2f}")',
        'print(type(5), type("5"))',
    ]),
    ("Maths and conversion", [
        'print(7 / 2, 7 // 2, 7 % 2, 2 ** 3)',
        'print(int("42") + 1, float("2.5"), str(7) + "!")',
        'print(round(3.14159, 2))',
        'x = 5\nx += 2\nprint(x)',
        'print(True and False, True or False, not True)',
    ]),
    ("Strings", [
        's = "Python"\nprint(s[0], s[-1], s[1:4], s[::-1])',
        'print("hi".upper(), "HI".lower(), "ravi kumar".title())',
        'print("  hi  ".strip(), "a-b".replace("-", "+"))',
        'print("banana".find("n"), "banana".count("a"))',
        'print("a,b,c".split(","), "-".join(["a", "b"]))',
        'print("fail" in "Login failed", "12".isdigit())',
    ]),
    ("Lists", [
        'l = [3, 1, 2]\nl.append(4)\nl.insert(0, 9)\nprint(l)',
        'l = [5, 7, 5]\nl.remove(5)\nprint(l.pop(), l)',
        'l = [3, 1, 2]\nprint(sorted(l), l)',
        'l = [4, 9, 1]\nprint(len(l), min(l), max(l), sum(l))',
        'a = [1, 2]\nb = a.copy()\nb.append(3)\nprint(a, b)',
    ]),
    ("Tuples", [
        't = (1, 2, 2)\nprint(t[0], t.count(2), t.index(2))',
        'x, y = (3, 7)\nprint(x, y)',
        'print(type((5,)), type((5)))',
    ]),
    ("Dictionaries", [
        'd = {"name": "Ravi"}\nd["age"] = 21\nprint(d)',
        'd = {"a": 1}\nprint(d.get("b", 0), "a" in d)',
        'd = {"a": 1, "b": 2}\nprint(list(d.keys()), list(d.values()))',
        'd = {"a": 1}\nprint(d.pop("a"), d)',
    ]),
    ("Sets", [
        's = {1, 2, 2, 3}\ns.add(4)\nprint(s, len(s))',
        'a = {1, 2, 3}\nb = {2, 3, 4}\nprint(a | b, a & b, a - b, a ^ b)',
        'print(type({}), type(set()))',
    ]),
    ("Errors you will meet", [
        'print("hi"',
        'print(hello)',
        'print("Age: " + 5)',
        'print(int("abc"))',
        'print([1, 2][5])',
        'print({"a": 1}["b"])',
        'print("hi".shout())',
        'print(10 / 0)',
        'import maths',
    ]),
]


# Part 1 revision sheet: every topic, a plain definition and one small example.
# Examples are run at build time; the output shown is real. None = no code example.
REVISION = [
    ("0", [
        ("Program", "A list of exact steps for a computer, done in order, top to bottom.", 'print("Step 1")\nprint("Step 2")'),
        ("Code", "The written steps of a program.", None),
        ("Machine code", "The 0s and 1s a computer really understands. Python translates your code into it.", None),
        ("Syntax", "The grammar rules of a language. Broken syntax stops the program.", 'print("Hi")'),
        ("Bug and debugging", "A bug is a mistake in code. Debugging is finding and fixing it.", None),
        ("Input and output", "Input is what goes into a program; output is what comes out, like text on screen.", 'print("This is output")'),
    ]),
    ("1", [
        ("Python", "A programming language, and the program that reads and runs it. Made by Guido van Rossum.", 'print("Hello from Python")'),
        ("Interpreted", "You run the file directly with python3 file.py. No separate app is built.", None),
        ("Compiled", "The whole program is translated once into an app file, then the app is run (C, Go, Rust).", None),
        ("Bytecode", "A halfway form of your code. Python makes it automatically and caches it in __pycache__.", None),
        ("Python 3", "The version to use. Python 2 was retired on 1 January 2020.", 'import sys\nprint(sys.version_info.major)'),
    ]),
    ("2", [
        ("Running a file", "Save code in a .py file, then run python3 file.py in the terminal.", None),
        ("The >>> prompt", "Interactive Python: type one line, see the result at once. Type exit() to leave.", None),
        ("SyntaxError", "Broken grammar. Python finds it before running anything, so no line runs.", 'print("Hi"'),
        ("Runtime error", "An error that happens while running. Lines above it have already run.", 'print("line 1")\nprint(score)'),
        ("Traceback", "Python's error report. Read the last line first: the error type and reason.", None),
        ("Indentation", "Spaces at the start of a line. Python gives them meaning, so do not add them by accident.", '  print("Hi")'),
    ]),
    ("3", [
        ("print()", "Shows something on the screen.", 'print("Hello")'),
        ("Text in quotes", "Quotes mark text. Without them, Python reads a word as a name.", 'print("Goa")'),
        ("Several values", "Commas print values on one line with a space between.", 'print("Age:", 25)'),
        ("sep and end", "sep sets what goes between values; end sets what comes after the last one.", 'print("a", "b", sep="-")\nprint("x", end="!")'),
        ("Comment", "A note after # that Python ignores.", '# this is a note\nprint("ok")'),
        ("Triple quotes", "Text that spans several lines.", 'print("""one\ntwo""")'),
        ("Module and import", "A module is a file of ready-made tools; import loads it.", 'import math\nprint(math.sqrt(16))'),
        ("from ... import", "Takes one tool out of a module, used without the module name.", 'from math import pi\nprint(pi)'),
        ("pip", "Python's installer for modules from outside Python: python3 -m pip install name.", None),
    ]),
    ("4", [
        ("Variable", "A name that points at a value.", 'age = 25\nprint(age)'),
        ("= (assignment)", "Works out the right side, then puts the name on the left onto the result.", 'x = 2 + 3\nprint(x)'),
        ("Naming rules", "Letters, digits and _; no digit first; no keywords; capitals make a different name.", 'user_name = "Ravi"\nprint(user_name)'),
        ("int and float", "Whole numbers and numbers with a decimal point.", 'print(type(5), type(5.0))'),
        ("str", "Text.", 'print(type("hi"))'),
        ("bool", "True or False.", 'print(5 > 3)'),
        ("None", "No value yet.", 'x = None\nprint(x)'),
        ("type()", "Tells you what type a value is.", 'print(type([1, 2]))'),
        ("Arithmetic", "+ - * / plus // (whole part), % (remainder) and ** (power).", 'print(7 / 2, 7 // 2, 7 % 2, 2 ** 3)'),
        ("Comparison", "== != < > <= >= give True or False.", 'print(5 == 5, 5 != 5)'),
        ("and, or, not", "Combine True and False.", 'print(True and False, True or False, not True)'),
        ("+= and friends", "Update a name using its old value.", 'n = 10\nn += 5\nprint(n)'),
        ("Type conversion", "int(), float() and str() turn a value into another type.", 'print(int("42") + 1, str(7) + "!")'),
        ("input()", "Waits for the user to type, and always returns text.", 'age = input("Age: ")\nprint(int(age) + 1)'),
        ("f-string", "Puts values inside text: f\"...{value}...\". :.2f shows 2 decimals.", 'price = 49.5\nprint(f"Total: {price * 2:.2f}")'),
        ("TypeError vs ValueError", "TypeError: the wrong kind of value. ValueError: the right kind, bad content.", 'print(int("abc"))'),
    ]),
    ("5", [
        ("String", "A row of characters: text.", 'word = "Python"\nprint(len(word))'),
        ("Index", "A character's position, starting at 0. -1 is the last.", 'word = "Python"\nprint(word[0], word[-1])'),
        ("Slice", "[start:stop] takes a piece; stop is not included.", 'print("Python"[1:4])'),
        ("Step", "[start:stop:step] jumps; a negative step goes backwards.", 'print("Python"[::-1])'),
        ("Immutable", "A string can never be changed; you build a new one.", 'word = "Python"\nprint("J" + word[1:])'),
        ("Method", "A tool belonging to a value, used with a dot. String methods return a new string.", 'name = "ravi"\nprint(name.upper(), name)'),
        ("strip() and replace()", "strip removes spaces at the ends; replace swaps text.", 'print("  hi  ".strip(), "a-b".replace("-", "+"))'),
        ("find() and index()", "Both find a position; find gives -1 when missing, index raises an error.", 'print("banana".find("n"), "banana".find("z"))'),
        ("split() and join()", "split cuts text into a list; join glues a list into text.", 'print("a,b".split(","), "-".join(["a", "b"]))'),
        ("in", "Checks whether text contains something. Capitals matter.", 'print("fail" in "Login failed")'),
        ("Escape characters", "\\n new line, \\t tab.", 'print("one\\ntwo")'),
    ]),
    ("6", [
        ("List", "Many values in order, in [ ], that can change.", 'fruits = ["apple", "mango"]\nprint(fruits)'),
        ("Mutable", "Can be changed in place. Lists are; strings and tuples are not.", 'l = [1, 2]\nl[0] = 9\nprint(l)'),
        ("append() and insert()", "Add at the end, or at a position.", 'l = ["b"]\nl.append("c")\nl.insert(0, "a")\nprint(l)'),
        ("remove() and pop()", "remove deletes by value; pop deletes by position and gives the item back.", 'l = [5, 7, 9]\nl.remove(7)\nprint(l.pop(), l)'),
        ("sort() and sorted()", "sort changes the list and returns None; sorted returns a new list.", 'l = [3, 1, 2]\nprint(sorted(l), l)'),
        ("reverse()", "Flips the order; it does not sort.", 'l = [3, 1, 2]\nl.reverse()\nprint(l)'),
        ("count() and index()", "How many times, and the first position.", 'l = ["a", "b", "a"]\nprint(l.count("a"), l.index("b"))'),
        ("Alias and copy", "b = a gives the same list a second name; a.copy() makes a new list.", 'a = [1]\nb = a\nb.append(2)\nprint(a)'),
        ("Nested list", "A list inside a list; use two indexes.", 'grid = [[1, 2], [3, 4]]\nprint(grid[1][0])'),
        ("Tuple", "Values in order, in ( ), that cannot change.", 'size = (1920, 1080)\nprint(size[0])'),
        ("One-item tuple", "Needs a trailing comma.", 'print(type((5,)), type((5)))'),
        ("Unpacking", "Spreads values into names; the counts must match.", 'x, y = (3, 7)\nprint(x, y)'),
    ]),
    ("7", [
        ("Dictionary", "key: value pairs in { }. You look values up by key.", 'd = {"name": "Ravi", "age": 21}\nprint(d["name"])'),
        ("get()", "Reads a key without failing; gives None or your default if missing.", 'd = {"a": 1}\nprint(d.get("b", 0))'),
        ("Add or replace", "Assigning to a key adds it, or replaces its value.", 'd = {"a": 1}\nd["b"] = 2\nd["a"] = 9\nprint(d)'),
        ("del and pop()", "Remove a key; pop also gives the value back.", 'd = {"a": 1, "b": 2}\nprint(d.pop("a"), d)'),
        ("keys(), values(), items()", "All keys, all values, or each pair.", 'd = {"a": 1}\nprint(list(d.keys()), list(d.items()))'),
        ("Keys rules", "Keys are unique and unchangeable: a list cannot be a key.", 'd = {"x": 1, "x": 2}\nprint(d)'),
        ("Set", "Unique values in { }, with no order and no positions.", 's = {1, 2, 2, 3}\nprint(s)'),
        ("add() and discard()", "Put a value in; take one out without failing if it is missing.", 's = {1}\ns.add(2)\ns.discard(9)\nprint(s)'),
        ("Set operations", "| either, & both, - only the first, ^ exactly one.", 'a = {1, 2}\nb = {2, 3}\nprint(a | b, a & b, a - b, a ^ b)'),
        ("Empty dict vs empty set", "{} is an empty dictionary; set() is an empty set.", 'print(type({}), type(set()))'),
    ]),
]


# Brain breaks between pages. Puzzle and bug answers are produced by running the code.
PUZZLES = [
    'print("2" + "2")',
    'print(len("hello world"))',
    'print(10 // 3, 10 % 3)',
    'print("ab" * 2 + "c")',
    'print([1, 2] * 2)',
    'print("Python"[-3:])',
    'print(3 * "-" + ">")',
    'print(type(6 / 3))',
    'print(bool(""), bool(" "))',
    'print("Hi" == "hi")',
    'print(max("banana"))',
    'print(len([[1, 2], [3]]))',
]

# (code, what to notice, fixed code). The bug either raises an error or does
# something you did not mean; the build runs both versions.
BUGS = [
    ('fruits = ["apple" "mango"]\nprint(len(fruits))',
     "A missing comma. Python glues two strings that sit side by side, so the list holds ONE item: \"applemango\". No error, just a wrong answer.",
     'fruits = ["apple", "mango"]\nprint(len(fruits))'),
    ('total = 5\nprint("Total: " + total)',
     "Text plus a number. Python will not guess, so it stops.",
     'total = 5\nprint("Total:", total)'),
    ('nums = [3, 1, 2]\nnums = nums.sort()\nprint(nums)',
     "sort() returns None, and the = put the name on that None. The list is gone.",
     'nums = [3, 1, 2]\nnums.sort()\nprint(nums)'),
    ('name = "ravi"\nname.upper()\nprint(name)',
     "upper() made a new string, but nothing stored it.",
     'name = "ravi"\nname = name.upper()\nprint(name)'),
    ('d = {"Name": "Ravi"}\nprint(d["name"])',
     "Keys are exact: capital N and small n are different keys.",
     'd = {"Name": "Ravi"}\nprint(d["Name"])'),
    ('price = "49"\nprint(price * 2)',
     "The price is text, so * repeats it instead of doubling the number.",
     'price = "49"\nprint(int(price) * 2)'),
]

JOKES = [
    ("Why do programmers mix up Halloween and Christmas?", "Because Oct 31 equals Dec 25. (31 in base 8 is the same number as 25 in base 10.)"),
    ("Why did the Python programmer not answer the phone?", "Because it was in a tuple: it could not be changed."),
    ("How many programmers does it take to change a light bulb?", "None. That is a hardware problem."),
    ("A programmer's partner says: \"Buy a loaf of bread, and if they have eggs, buy a dozen.\"", "The programmer comes home with 12 loaves of bread."),
]
