# Python Basics - Revision Handbook

Revision hub for what you have learnt so far (Chapters 1 to 5).
Scope on purpose: this only covers topics you have already studied. Loops, if-statements, and functions are NOT here yet, because you have not learnt them. When you do, we add them.

Each topic follows the same flow: plain-English idea, then commented code, then the important methods/details within that topic. Some methods below are new to you but belong to a topic you already know, so learn those too (they are marked "learn this").

How to revise: read a chapter top to bottom, cover the code, predict the output, then reveal. Revise the "Gotcha" boxes hardest, they are the exact mistakes your own files hit.

---

## Table of Contents
- [[#Chapter 1 - Getting Started]]
- [[#Chapter 2 - Variables, Data Types, Operators]]
- [[#Chapter 3 - Strings]]
- [[#Chapter 4 - Lists and Tuples]]
- [[#Mutation - What Changes and What Does Not]]
- [[#Chapter 5 - Dictionaries and Sets]]
- [[#Quick Cheat Sheet]]

---

# Chapter 1 - Getting Started

## 1.1 print()
`print()` shows text on the screen. Text in quotes is a string and prints exactly as written.

```python
print("Hello, World!")   # -> Hello, World!
```

## 1.2 Multi-line text with triple quotes
Triple quotes `''' ... '''` let one string cover several lines, keeping the line breaks.

```python
print('''Swami Vivekananda was born in 1863 in Kolkata, India.
He introduced Vedanta and Yoga to the Western world.
His 1893 Chicago speech began with "Sisters and brothers of America".''')
```

## 1.3 Comments
Notes for humans. Python ignores them.

```python
# This is a single-line comment (starts with #)

"""
A triple-quoted string not assigned to a variable
is often used as a multi-line note / comment.
"""
```

## 1.4 Modules (import)
A module is ready-made code you reuse. `import` brings it in, then you use `module.function()`.

```python
import pyjokes                # bring in the pyjokes module
joke = pyjokes.get_joke()     # call a function that lives inside it
print(joke)
```

```python
import os                     # os = tools for talking to the operating system

path = "/Users/chethanbhatbs/Documents/Python_Basics/Chapter1-PS"
contents = os.listdir(path)   # returns a list of the file/folder names in that path
print(contents)
```

**Key takeaways**
- `print()` displays output.
- `'''triple quotes'''` = multi-line text.
- `#` = comment.
- `import module` reuses existing code via `module.function()`.

---

# Chapter 2 - Variables, Data Types, Operators

## 2.1 Variables
A variable is a labelled box holding a value. `=` means "assign" (put the value into the box), not "is equal to".

```python
a = 1                 # box 'a' now holds 1
b = 2                 # box 'b' now holds 2
print(a + b)          # -> 3

name = "Chethan Bhat"
print(name)           # -> Chethan Bhat
```

## 2.2 Data types
The five basic types you have used:

```python
a = 1          # int      -> whole number
b = 2.5        # float    -> number with a decimal point
c = "Hello"    # str      -> text
d = True       # bool     -> True or False
e = None       # NoneType -> "no value / nothing"

print(a + b)   # -> 3.5   (int + float gives a float)
```

## 2.3 Rules for naming variables
- Allowed: letters, digits, underscore `_`.
- Cannot START with a digit.
- No symbols like `@ # ! -`.
- Case sensitive: `name` and `Name` are two different variables.

```python
a = 23
aaa = 34
name = "Chethan"
_name = "Chethan Bhat"     # leading underscore is allowed

# 3a = 24       # ERROR: cannot start with a digit
# @name = "x"   # ERROR: cannot use symbols
```

## 2.4 Operators

### Arithmetic
```python
a = 10
b = 3
print(a + b)    # 13    addition
print(a - b)    # 7     subtraction
print(a * b)    # 30    multiplication
print(a / b)    # 3.333...   division ALWAYS gives a float
print(a % b)    # 1     modulus (remainder after division)
print(a ** b)   # 1000  exponent (10 to the power 3)
print(a // b)   # 3     floor division (division with the decimal dropped)
```

### Assignment shortcuts
```python
x = 5
x += 3    # same as x = x + 3   -> 8
x -= 2    # same as x = x - 2   -> 6
x *= 4    # same as x = x * 4   -> 24
```

### Comparison (result is always True or False)
```python
a = 10
b = 20
print(a == b)   # False   equal to        (note: == compares, = assigns)
print(a != b)   # True    not equal to
print(a > b)    # False   greater than
print(a < b)    # True    less than
print(a >= b)   # False   greater than or equal to
print(a <= b)   # True    less than or equal to
```

### Logical
```python
x = True
y = False
print(x and y)   # False   True only if BOTH are True
print(x or y)    # True    True if AT LEAST ONE is True
print(not x)     # False   flips the value
```

Truth-table shapes to remember:
```
and -> True only when both are True
or  -> True when at least one is True
not -> flips True to False and False to True
```

## 2.5 type() - checking a value's type
```python
print(type(25))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type("Hello"))   # <class 'str'>
print(type(True))      # <class 'bool'>
print(type(None))      # <class 'NoneType'>
```

## 2.6 input() and type conversion
This is the idea your files revisited the most, so revise it carefully.

`input()` ALWAYS returns a string, even when the user types digits.

```python
a = input("Enter a number: ")   # a is a STRING, e.g. "5"
print(type(a))                  # <class 'str'>
```

**Gotcha (from your input.py): adding two string inputs joins them, it does not add.**
```python
a = input("Enter a number: ")   # "5"
b = input("Enter another: ")    # "3"
print(a + b)                    # "53"  <- strings get joined, NOT added

# Fix: convert to numbers first
c = int(a)
d = int(b)
print(c + d)                    # 8   <- now it adds as numbers

# For decimals, use float():
x = float(input("Enter a number: "))
y = float(input("Enter another: "))
print(x + y)                    # correct decimal sum
```

Conversion functions: `int()`, `float()`, `str()`, `bool()`.

**Key takeaways**
- `=` assigns, `==` compares.
- `/` gives a float, `//` drops the decimal, `%` gives the remainder, `**` is power.
- `input()` is always a string, convert with `int()` / `float()` before doing maths.

---

# Chapter 3 - Strings

## 3.1 Creating strings
Single, double, and triple quotes all make strings.

```python
name = "Chethan"
name = 'Chethan'
name = '''Chethan'''   # triple quotes also allow multi-line text
```

Strings are **immutable**: they cannot be changed in place. A method that "changes" a string actually returns a NEW string.

```python
s = "hello world!"
s.replace("hello", "Hi")     # returns "Hi world!" but does NOT change s
print(s)                     # still "hello world!"

s = s.replace("hello", "Hi") # reassign to actually keep the new string
print(s)                     # "Hi world!"
```

## 3.2 Indexing
Every character has a position. Positive index counts from 0 on the left; negative index counts from -1 on the right.

```python
word = "Python"
#        P  y  t  h  o  n
# index  0  1  2  3  4  5
# neg   -6 -5 -4 -3 -2 -1

print(word[0])    # P   first character
print(word[-1])   # n   last character
print(word[-2])   # o   second last character
```

## 3.3 Slicing  [start : stop : step]
Takes a piece of the string. The `stop` position is EXCLUDED.

```python
name = "Chethan"
print(name[0:3])    # Che    index 0,1,2  (3 is excluded)
print(name[4:])     # han    from index 4 to the end
print(name[:6])     # Chetha from the start up to index 5
print(name[-4:-1])  # tha    negative slice
```

### Step / skip value (the third number)
```python
word = "amazing"
print(word[1:6:2])    # mzn   start at 1, then jump 2 each time

number = "123456789"
print(number[0:8:3])  # 147

print(word[::-1])     # gnizama   step of -1 reverses the string
```

## 3.4 Escape sequences
A backslash `\` creates special characters.

```python
# \n = new line, \t = tab, \" = a literal double quote
a = "Hi, I am Chethan \n I work at \"Emergent\" \n as a QA Engineer"
print(a)
# Hi, I am Chethan
#  I work at "Emergent"
#  as a QA Engineer
```
Common ones: `\n` newline, `\t` tab, `\\` backslash, `\"` double quote, `\'` apostrophe.

## 3.5 String formatting (putting variables inside text)
```python
name = "Alice"
age = 25

print(f"{name} is {age} years old.")             # f-string (modern, best)
print("{} is {} years old.".format(name, age))   # .format() (older)
print("%s is %d years old." % (name, age))        # % style (very old)
```
Use f-strings. They are the cleanest and easiest to read.

## 3.6 String methods
Grouped for easy revision. All of these return a NEW string or a value; none change the original.

**Case**
```python
"hello".upper()        # HELLO
"HELLO".lower()        # hello
"hello world".title()  # Hello World   (first letter of every word)
"hello".capitalize()   # Hello         (first letter of the string only)
"PyThOn".swapcase()    # pYtHoN        (swaps upper<->lower)
```

**Cleaning whitespace**
```python
"  hi  ".strip()    # "hi"     removes spaces from BOTH sides
"  hi  ".lstrip()   # "hi  "   left side only
"  hi  ".rstrip()   # "  hi"   right side only
```

**Searching**
```python
"Python is easy".find("easy")    # 10   index of first match, or -1 if missing
"Python is easy".index("easy")   # 10   like find, but ERRORS if missing
"banana".count("a")              # 3    how many times it appears
"Python".startswith("Py")        # True
"Python".endswith("on")          # True
```

**Changing / splitting / joining**
```python
"Java is fun".replace("Java", "Python")   # "Python is fun"
"a,b,c".split(",")                         # ['a', 'b', 'c']   string -> list
"-".join(["a", "b", "c"])                  # "a-b-c"           list -> string
```

**Checking content (each returns True or False)**  [learn these, you had only a few]
```python
"Hello".isalpha()    # True    letters only
"12345".isdigit()    # True    digits only
"Python3".isalnum()  # True    letters and/or digits only
"   ".isspace()      # True    whitespace only
"python".islower()   # True
"PYTHON".isupper()   # True
```

**Padding**  [learn these]
```python
"Python".center(20, "*")   # ****** Python ******
"45".zfill(5)              # "00045"   pad the front with zeros
```

**Membership**
```python
"Py" in "Python"        # True
"Java" not in "Python"  # True
```

## 3.7 Small worked snippets (using only what you know)
```python
# Reverse a string  (slicing only)
text = "Programming"
print(text[::-1])                 # gnimmargorP

# Palindrome check  (comparison returns True/False, no if needed)
word = "madam"
print(word == word[::-1])         # True  -> it reads the same reversed

# Remove all spaces  (replace)
sentence = "Python is fun"
print(sentence.replace(" ", ""))  # Pythonisfun

# Count words  (split then len)
sentence = "Python is easy to learn"
print(len(sentence.split()))      # 5
```

**Key takeaways**
- Strings are immutable, reassign to keep a change.
- Slicing is `[start:stop:step]`, stop is excluded, `[::-1]` reverses.
- `find()` returns -1 when missing; `index()` crashes when missing.
- Prefer f-strings for formatting.

---

# Chapter 4 - Lists and Tuples

## 4.1 Lists
An ordered, changeable (mutable) collection. Can hold mixed data types.

```python
friends = ["Rahul", 7, True]   # a string, an int, and a bool together

print(friends[0])              # Rahul   (index starts at 0, like strings)

friends[0] = "Arjun"           # lists are MUTABLE -> you can change an item
print(friends[0])              # Arjun
```

## 4.2 List methods
```python
friends = ["Rahul", 7, True]
friends.append("Rajdeep")      # add ONE item to the end
print(friends)                 # ['Rahul', 7, True, 'Rajdeep']

l1 = [131, 76, 23, 68, 1, 0, -1, 53]

l1.sort()          # sort in place, ascending (returns None)
l1.reverse()       # reverse the order in place
l1.insert(3, 256)  # insert 256 at index 3, pushing the rest right
l1.pop(3)          # remove AND return the item at index 3
l1.remove(131)     # remove the first item whose VALUE is 131
```

**Gotcha (from your marks problem): sorting number-strings sorts alphabetically.**
If marks are stored as strings, `"10"` comes before `"9"`. Convert with `int()` before sorting so they sort by value.

**More list methods to learn (within a topic you already know):**
```python
nums = [1, 2, 3, 2]
nums.extend([4, 5])   # add MANY items  (append would add [4,5] as ONE item)
nums.count(2)         # 2    how many times a value appears
nums.index(3)         # 2    index of the first occurrence
nums.clear()          # empties the list -> []
```

**Built-in functions that work on lists (learn these, very common):**
```python
print(len([1, 2, 3]))     # 3    number of items
print(sum([1, 2, 3]))     # 6    (you used this in a problem)
print(max([1, 2, 3]))     # 3
print(min([1, 2, 3]))     # 1
print(sorted([3, 1, 2]))  # [1, 2, 3]   returns a NEW sorted list
```

Important difference: `list.sort()` changes the list itself and returns None. `sorted(list)` leaves the original alone and returns a new list.

## 4.3 Tuples
An ordered collection that CANNOT be changed (immutable). Written with `( )`.

```python
a = (1,)     # a ONE-item tuple NEEDS the trailing comma
a = ()       # empty tuple
print(type(a))   # <class 'tuple'>
```

**Gotcha (from your problem03): tuples are immutable.**
```python
example = (1, "43", "Chethan", 23.5)
example[0] = 2    # TypeError: 'tuple' object does not support item assignment
```

## 4.4 Tuple methods
A tuple has only two methods, because it cannot change:
```python
a = ("Chethan", "ARJUN", 1, 1)
print(a.count("Chethan"))   # 1   how many times it appears
print(a.index(1))           # 2   index of the FIRST occurrence

# Built-ins still work:
print(1 in a)     # True    membership
print(len(a))     # 4
```

## 4.5 List vs Tuple

| Feature      | List `[ ]`             | Tuple `( )`             |
|--------------|------------------------|-------------------------|
| Changeable?  | Yes (mutable)          | No (immutable)          |
| Speed        | Slightly slower        | Slightly faster         |
| Use when     | data will change       | data is fixed/constant  |
| Methods      | many (append, sort...) | only count(), index()   |

**Key takeaways**
- Lists use `[ ]` and are mutable; tuples use `( )` and are immutable.
- `sort()` changes in place and returns None; `sorted()` returns a new list.
- A one-item tuple needs a comma: `(1,)`.
- Convert number inputs with `int()` before sorting.

---

# Mutation - What Changes and What Does Not

Covers strings, lists and tuples together. This is the single hardest idea in beginner Python, and almost every confusing output you will hit comes from here. Every output in this chapter was produced by actually running the code.

## M.1 The one idea behind all of it

**A variable is a label, not a box.**

Most people picture a variable as a box holding a value, so copying the box gives you a second value. Python does not work that way. A variable is a name stuck onto an object that lives somewhere in memory. `=` moves the name. It never copies the object.

From that, exactly two things can happen on any line of code:

| | what it does | do other names see it |
|---|---|---|
| **Mutation** | changes the object itself | **yes**, every name on that object |
| **Rebinding** | builds a NEW object, points the name at it | **no**, the old object is untouched |

Mutation is only possible if the object allows being changed. A list allows it. A string and a tuple do not.

**Three questions to ask of any line:**

1. Is the plain variable name alone on the left of `=`?  Then it is **rebinding**. Nothing was changed, a name just moved.
2. Is it a method call like `.append()`, or is there an index on the left like `name[0] = x`?  Then it is **mutation**. The object changed.
3. Is the object a str or a tuple?  Then mutation is impossible, so whatever happened was rebinding.

## M.2 Read vs write, the rule that decides everything

- **READ** means taking values OUT of the object. Nothing ever changes. Works on all three types.
- **WRITE** means putting values IN. Only a list allows it.

```python
# READS: all three allow these, and none of them change anything
o[0]        o[-1]        o[0:2]        o[::-1]
len(o)      o + o        o * 2         o.count(x)      o.index(x)      x in o

# WRITES: a list allows these, str and tuple refuse them
o[0] = 9    del o[0]     o.append(x)   o.insert(i, x)  o.remove(x)
o.pop()     o.sort()     o.reverse()   o.clear()       o.extend(other)
```

The tell is which side of the `=` the square brackets are on:

- `x = o[0]` , brackets on the **right**, you are **reading out** of `o`.
- `o[0] = x` , brackets on the **left**, you are **writing into** `o`.

## M.3 Does printing or slicing change the object? No.

This is the question worth being certain about. Slicing **reads**. It builds a separate result and leaves the original exactly as it was, for all three types.

```python
nums = [10, 20, 30]
tup  = (10, 20, 30)
txt  = "102030"

print(nums[0:2], tup[0:2], txt[0:2])      # [10, 20] (10, 20) 10
print(nums, tup, txt)                     # [10, 20, 30] (10, 20, 30) 102030   all unchanged

print(nums[::-1], tup[::-1], txt[::-1])   # [30, 20, 10] (30, 20, 10) 030201
print(nums, tup, txt)                     # [10, 20, 30] (10, 20, 30) 102030   still unchanged
```

Even `[::-1]`, which looks drastic, changes nothing. It reads the items in reverse order into a new object. The original list is still `[10, 20, 30]`.

**So: `print(l[1:3])` never touches `l`. Same for a tuple. Same for a string.** A slice is a question, not a command.

Slicing also keeps the type it came from: slice a list, get a list; slice a tuple, get a tuple; slice a str, get a str.

## M.4 str on its own: every "change" builds a new string

A string can never be changed. So every string method has to hand you a **new** string, and if you do not store it, it is thrown away.

```python
s = "hello"

print(s.upper())              # HELLO      a new string
print(s)                      # hello      the original, untouched

print(s[1:3])                 # el         reading
print(s)                      # hello      untouched

print(s.replace("l", "L"))    # heLLo      a new string
print(s)                      # hello      untouched

s2 = s.upper()                # to KEEP the result you must store it
print(s2)                     # HELLO
print(s)                      # hello      still untouched

# s[0] = "H"    ->  TypeError: 'str' object does not support item assignment
```

`s.upper()` on its own line is a wasted line. The new string is created and immediately discarded, because nothing was assigned.

## M.5 list on its own: the only one that changes in place

```python
l = [3, 1, 2]

print(l[0:2])     # [3, 1]         reading
print(l)          # [3, 1, 2]      unchanged

print(l.sort())   # None           sort returns NOTHING
print(l)          # [1, 2, 3]      but the list itself changed

l[0] = 99
print(l)          # [99, 2, 3]     REPLACED the slot at index 0
print(len(l))     # 3              length did not change

l.insert(0, 7)
print(l)          # [7, 99, 2, 3]  INSERTED, others pushed right
print(len(l))     # 4              length grew

x = l.pop()
print(x)          # 3              pop returns the removed item
print(l)          # [7, 99, 2]     and the list is shorter
```

**Gotcha: `l[0] = x` replaces, it does not insert.** The slot already exists, so nothing is pushed anywhere and the length stays the same. `insert` is the only one that adds at a position.

```python
a = ["Chethan", "Bhat"]
a[0] = "CB"              # a is ['CB', 'Bhat']                len 2
b = ["Chethan", "Bhat"]
b.insert(0, "CB")        # b is ['CB', 'Chethan', 'Bhat']     len 3
```

**Gotcha: mutating methods return `None`.** Never write `x = l.sort()`, you will get `None` and lose your list. Use `sorted(l)` when you want a new sorted list back and the original kept.

The reason is consistent: if a method changes the object, there is nothing new to hand back, so it returns `None`. If a method cannot change the object, returning a new one is the only way to give you a result. `pop` is the exception that returns something, because "which item was removed" is information you asked for.

## M.6 tuple on its own: reads work, writes are refused

```python
t = (3, 1, 2)

print(t[0:2])     # (3, 1)         reading a tuple gives a tuple
print(t)          # (3, 1, 2)      unchanged

print(sorted(t))  # [1, 2, 3]      note: a LIST, not a tuple
print(t)          # (3, 1, 2)      unchanged

# t[0] = 99   ->  TypeError: 'tuple' object does not support item assignment
# t.sort()    ->  AttributeError: 'tuple' object has no attribute 'sort'

t = t + (9,)
print(t)          # (3, 1, 2, 9)   allowed: a NEW tuple was built, the name moved
```

Notice the two different errors, they mean different things:

- `TypeError ... does not support item assignment` , the syntax exists, the type refuses it.
- `AttributeError ... has no attribute 'sort'` , the method does not exist on a tuple at all.

A tuple has exactly **two** methods, `count()` and `index()`, because those are the only two that read without changing. A list has 11. A str has 47, and all 47 return something new.

**And `t = t + (9,)` is not a contradiction of immutability.** No tuple was changed. A second tuple was built from the contents of the first, and the name `t` was pointed at it. Immutability stops you writing **into** an object. It never stops a name from moving.

## M.7 One example using all three together

```python
raw    = "banana,apple,cherry"     # str    immutable
items  = raw.split(",")            # list   mutable
frozen = tuple(items)              # tuple  immutable, a COPY of the items

# ---------- READ from each: nothing changes ----------
print(raw[0:6])       # banana
print(items[0:2])     # ['banana', 'apple']
print(frozen[0:2])    # ('banana', 'apple')

print(raw)            # banana,apple,cherry
print(items)          # ['banana', 'apple', 'cherry']
print(frozen)         # ('banana', 'apple', 'cherry')      all three untouched

# ---------- WRITE: only the list allows it ----------
items[0] = "BANANA"
items.append("date")
print(items)          # ['BANANA', 'apple', 'cherry', 'date']
print(raw)            # banana,apple,cherry                 untouched
print(frozen)         # ('banana', 'apple', 'cherry')        untouched

# ---------- "changing" a str = build new + store ----------
raw2 = raw.upper()
print(raw)            # banana,apple,cherry                 original survives
print(raw2)           # BANANA,APPLE,CHERRY                 the new one

# ---------- "changing" a tuple = build new + rebind ----------
frozen2 = frozen + ("date",)
print(frozen)         # ('banana', 'apple', 'cherry')
print(frozen2)        # ('banana', 'apple', 'cherry', 'date')

print(len(raw), len(items), len(frozen), len(frozen2))   # 19 4 3 4
```

Three things to take from this:

1. `raw` is never affected by anything done to `items`. `split` **read** the string and built a list of new strings.
2. `frozen` is never affected either. `tuple(items)` **copied** the items at that moment, so the later `items[0] = "BANANA"` and `items.append("date")` cannot reach it.
3. `len(raw)` is `19` because a string's length counts **characters**, including the commas. `len(items)` is `4` because a list's length counts **items**.

**Gotcha: `split` always produces strings, never numbers.**

```python
parts = "10,20,30".split(",")
print(parts)                        # ['10', '20', '30']    quotes: these are text
print(parts[0] + parts[1])          # 1020                  glued, not added
# parts[0] * parts[1]  ->  TypeError: can't multiply sequence by non-int of type 'str'
print(int(parts[0]) + int(parts[1]))  # 30                   now it is arithmetic
```

**Gotcha: quotes in output tell you the type.**

```python
data = "10,20,30"
print(data)          # 10,20,30              print of a str shows NO quotes
print([data])        # ['10,20,30']          inside a container, quotes appear
print(['10', 20])    # ['10', 20]            one is text, one is a number
```

`print` shows a string's **contents**. A container shows its items in the form you would type them, so you can tell text from numbers.

## M.8 The alias test, run on all three

```python
s = "hi";   s_b = s;   s = s + "!"      # rebind
print(s, s_b)          # hi! hi                s_b did NOT follow

l = [1];    l_b = l;   l.append(2)      # mutate
print(l, l_b)          # [1, 2] [1, 2]         l_b DID follow

t = (1,);   t_b = t;   t = t + (2,)     # rebind
print(t, t_b)          # (1, 2) (1,)           t_b did NOT follow

l2 = [1];   l2_b = l2; l2 = l2 + [2]    # rebind, even though it is a list
print(l2, l2_b)        # [1, 2] [1]            l2_b did NOT follow
```

Compare the second and fourth blocks. **Same type, same end value, opposite effect on the other name.** `append` mutates; `l2 = l2 + [2]` builds a new list and moves the name. That is the whole distinction, and the type is not what decides it, the operation is.

**Gotcha: `+=` behaves differently on a list.**

```python
p = [1, 2];  p_b = p;  p += [3]
print(p, p_b, p is p_b)     # [1, 2, 3] [1, 2, 3] True     mutated in place

q = (1, 2);  q_b = q;  q += (3,)
print(q, q_b, q is q_b)     # (1, 2, 3) (1, 2) False       rebuilt

r = "ab";    r_b = r;  r += "c"
print(r, r_b, r is r_b)     # abc ab False                 rebuilt
```

On a list, `+=` is a mutation, so other names see it. On a str or tuple it cannot be, so it quietly builds a new object instead. One operator, two behaviours, decided by the type.

## M.9 Two gotchas that look like exceptions but are not

**A mutable item inside a tuple.**

```python
tt = (1, [2, 3])
tt[1].append(4)
print(tt)              # (1, [2, 3, 4])
# tt[1] = [9]   ->  TypeError: 'tuple' object does not support item assignment
```

The tuple was never changed. It still holds the same two objects in the same two slots: the number `1`, and that one list. The **list** changed. A tuple guarantees its own slots, not the contents of whatever sits in them.

**A slice copies only the outer level (shallow copy).**

```python
inner = [1, 2]
a = [inner, "x"]
b = a[:]               # a copy of the OUTER list

b[0].append(99)
print(a)               # [[1, 2, 99], 'x']       a changed too
print(b)               # [[1, 2, 99], 'x']       because a[0] is b[0]

b[1] = "changed"
print(a)               # [[1, 2, 99], 'x']       a did NOT change
print(b)               # [[1, 2, 99], 'changed']
```

`b = a[:]` built a new outer list, but it filled it with the **same** item objects. So writing into `b` itself (`b[1] = ...`) does not touch `a`, but reaching through into a shared inner list (`b[0].append(...)`) does.

**How to copy a list properly:** `l[:]` , `l.copy()` , `list(l)` all give a new outer list. A str or tuple never needs copying, there is nothing you could change. For those, a full slice `t[:]` even hands back the very same object, which is safe precisely because it is immutable.

## M.10 Everything at one glance

**Identity**

| | syntax | mutable | ordered | items | methods |
|---|---|---|---|---|---|
| **str** | `"hi"` | no | yes | characters only | 47, all return new |
| **list** | `[1, 2]` | **yes** | yes | anything, mixed | 11, 8 of them mutate |
| **tuple** | `(1, 2)` | no | yes | anything, mixed | 2, `count` `index` |

Empty and one-item forms: `''` `[]` `()` and `'a'` `[1]` `(1,)`. The one-item tuple needs the comma; the comma makes the tuple, not the brackets, so `(5)` is just the number `5`.

**Reads, identical on all three, none of them change anything**

| operation | `"hello"` | `[1,2,3]` | `(1,2,3)` |
|---|---|---|---|
| `o[0]` | `'h'` | `1` | `1` |
| `o[-1]` | `'o'` | `3` | `3` |
| `o[0:2]` | `'he'` | `[1, 2]` | `(1, 2)` |
| `o[::-1]` | `'olleh'` | `[3, 2, 1]` | `(3, 2, 1)` |
| `len(o)` | `5` | `3` | `3` |
| `o + o` | `'hellohello'` | `[1,2,3,1,2,3]` | `(1,2,3,1,2,3)` |
| `o * 2` | `'hellohello'` | `[1,2,3,1,2,3]` | `(1,2,3,1,2,3)` |
| `o.count(x)` `o.index(x)` `x in o` | yes | yes | yes |

**Writes, the entire difference between the three**

| attempt | str | list | tuple |
|---|---|---|---|
| `o[0] = 9` | `TypeError` | `[9, 2, 3]` | `TypeError` |
| `del o[0]` | `TypeError` | `[2, 3]` | `TypeError` |
| `o.append(4)` | no such method | `[1, 2, 3, 4]` | `AttributeError` |
| `o.sort()` | no such method | sorts, returns `None` | `AttributeError` |

**Does this line change the object, or move the name**

| line | changes the object | other names see it |
|---|---|---|
| `b = a` | no, just a second label | yes, same object |
| `a[0] = 9` | **yes** | **yes** |
| `a.append(4)` | **yes** | **yes** |
| `a.sort()` `a.reverse()` `a.insert()` `a.remove()` `a.pop()` | **yes** | **yes** |
| `a += [4]` on a list | **yes** | **yes** |
| `a = a + [4]` | no, builds new | no |
| `a = a[1:3]` | no, builds new | no |
| `a = [9]` | no, builds new | no |
| `a.upper()` on a str | no, impossible | no |
| `print(a[1:3])` | **no** | no |

**Return value: new object, or `None`**

| call | returns | original after |
|---|---|---|
| `"hello".upper()` | `'HELLO'` | `'hello'` unchanged |
| `"hello".replace("l","L")` | `'heLLo'` | `'hello'` unchanged |
| `"a,b".split(",")` | `['a', 'b']` | `'a,b'` unchanged |
| `[3,1,2].sort()` | **`None`** | `[1, 2, 3]` changed |
| `[1,2].append(3)` | **`None`** | `[1, 2, 3]` changed |
| `[1,2,3].pop()` | `3` the item | `[1, 2]` changed |
| `sorted([3,1,2])` | `[1, 2, 3]` | `[3, 1, 2]` unchanged |
| `sorted("hello")` | `['e','h','l','l','o']` a LIST | `'hello'` unchanged |

**Converting between them**

```python
list("hello")           # ['h', 'e', 'l', 'l', 'o']
tuple([1, 2])           # (1, 2)
list((1, 2))            # [1, 2]
"".join(['a', 'b'])     # 'ab'          list of strings back to a str
str([1, 2])             # '[1, 2]'      NOT a join, it stringifies the brackets too
# "".join([1, 2])   ->  TypeError: sequence item 0: expected str instance, int found
```

**Key takeaways**

- A variable is a label, not a box. `=` moves a label and never copies an object.
- All three types **read** identically. Only a list can be **written into**, and that single fact explains everything else.
- Reading, slicing and printing never change anything, for any type.
- `l[0] = x` replaces and keeps the length. `l.insert(0, x)` adds and grows it.
- A method that changes the object returns `None`. A method that cannot change it returns a new object.
- `t = t + (9,)` does not break immutability. The tuple was not changed, the name moved.
- A mutation on one line is visible to every line after it, through every name on that object.
- `split` gives strings, never numbers. Convert with `int()` before doing maths.
- Quotes in printed output tell you the type. `print` of a str shows none; inside a container they appear.

---

# Chapter 5 - Dictionaries and Sets

## 5.1 Dictionaries
Stores data as `key : value` pairs. Keys are unique. You look up a value by its key, not by a position.

```python
marks = {
    "Chethan": 97,
    "Arjun": 100,
    "Amrutha": 100,
    "list": [1, 3, 7]      # a value can be any type, even a list
}

print(marks["Chethan"])    # 97   look up by KEY
# print(marks[0])          # ERROR: dictionaries have no index positions
d = {}                     # an empty dictionary
```

## 5.2 Dictionary methods
```python
marks = {"Chethan": 97, "Arjun": 100}

marks.items()    # every key-value pair: dict_items([('Chethan', 97), ('Arjun', 100)])
marks.keys()     # just the keys:   dict_keys(['Chethan', 'Arjun'])
marks.values()   # just the values: dict_values([97, 100])

marks.update({"Arjun": 99})   # change an existing key (or add if new)
print(marks["Arjun"])         # 99
```

**Gotcha (from your 02_dict_methods.py): `[ ]` vs `.get()`**
```python
print(marks["Missing"])            # ERROR (KeyError) if the key does not exist
print(marks.get("Missing"))        # None   -> safe, no crash
print(marks.get("Missing", "N/A")) # "N/A"  -> you can give a default instead of None
```
Use `.get()` when you are not sure the key exists.

**More dict operations to learn (within a topic you know):**
```python
person = {"name": "Chethan", "age": 25}
person["city"] = "Bengaluru"   # add a new pair just by assigning to a new key
person.pop("age")              # remove key "age" and return its value
print("name" in person)        # True   -> checks if a KEY exists
```

## 5.3 Sets
An unordered collection of UNIQUE items. Duplicates are dropped automatically.

```python
s = {1, 5, 7, 7, 8, 8, "Chethan"}   # duplicates removed
print(s)        # order not guaranteed, e.g. {1, 5, 7, 8, 'Chethan'}

e = set()       # the ONLY correct way to make an EMPTY set
```

**Gotcha (from your 05_problem.py): empty `{}` is a DICTIONARY, not a set.**
```python
s = {}
print(type(s))   # <class 'dict'>   <- NOT a set
# Use set() for an empty set.
```

## 5.4 Set methods
```python
s = {1, 5, 7, 8}
s.add(566)      # add one item
s.remove(7)     # remove 7  (ERRORS if 7 is not present)
s.discard(99)   # remove if present, no error if missing  (safer than remove)  [learn this]
s.pop()         # remove and return some item (unordered, so you cannot pick which)
s.clear()       # empty the set

print(len({1, 2, 3}))   # 3
print(2 in {1, 2, 3})   # True
```

## 5.5 Set operations
```python
s1 = {1, 5, 7, 6}
s2 = {2, 5, 8, 3}

print(s1.union(s2))         # everything from both  -> {1,2,3,5,6,7,8}
print(s1.intersection(s2))  # only the common items -> {5}
print(s1.difference(s2))    # in s1 but NOT in s2   -> {1, 6, 7}   [learn this]
print(s1.symmetric_difference(s2))  # in either but not both       [learn this]

# Shortcut operators do the same thing:
# s1 | s2 = union,  s1 & s2 = intersection,  s1 - s2 = difference
```

**Gotchas about set uniqueness (from your problems 03 and 04):**
```python
s = set()
s.add(18)
s.add("18")
print(s)          # {18, '18'}   int 18 and string "18" are DIFFERENT, both kept

s = set()
s.add(20)
s.add(20.0)       # 20 == 20.0 is True, so this counts as a DUPLICATE
s.add("20")       # different value, kept
print(len(s))     # 2   -> {20, '20'}  (20.0 did not add a new item)
```

## 5.6 Dictionary lookup program (your Hindi-words problem, made safe)
```python
words = {
    "madad": "Help",
    "kursi": "Chair",
    "billi": "Cat"
}

word = input("Enter the word you want the meaning of: ")
print(words.get(word, "Word not found"))   # .get avoids a crash on a typo
```

**Key takeaways**
- Dict = key:value, look up by key, use `.get()` to avoid crashes.
- Set = unique and unordered; the empty set is `set()`, NOT `{}`.
- In sets, `20 == 20.0` (duplicate) but `18 != "18"` (both kept).
- union = combine, intersection = common, difference = subtract.

---

# Quick Cheat Sheet

**Which collection do I use?**

| Type   | Syntax        | Ordered? | Changeable? | Duplicates? | Look up by |
|--------|---------------|----------|-------------|-------------|------------|
| List   | `[1, 2, 3]`   | Yes      | Yes         | Yes         | index      |
| Tuple  | `(1, 2, 3)`   | Yes      | No          | Yes         | index      |
| Dict   | `{"a": 1}`    | Yes*     | Yes         | Keys unique | key        |
| Set    | `{1, 2, 3}`   | No       | Yes         | No          | (none)     |

(*dictionaries keep insertion order in modern Python.)

**Crashes vs safe alternatives**
- `str.index(x)` / `list.index(x)` crash if missing; for strings `find()` returns -1.
- `dict[key]` crashes if missing; `dict.get(key)` returns None.
- `set.remove(x)` crashes if missing; `set.discard(x)` is safe.

**In place vs returns new**
- `list.sort()` changes the list, returns None. `sorted(list)` returns a NEW list.
- Every string method returns a NEW string (strings never change in place).

**input() rule**
- Always a string. Wrap in `int()` or `float()` before doing maths or numeric sorting.

**Empty containers**
```python
[]        # empty list
()        # empty tuple
{}        # empty DICTIONARY (not a set)
set()     # empty set
""        # empty string
```

---

Revision tip: revise one chapter a day, retype 2-3 snippets from memory, and run them.
When you learn a new topic (if-statements, loops, functions), tell me and I will add it in the correct sequence.
