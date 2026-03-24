"""
Database seed script for CodeNest
Seeds concepts (taxonomy) and real lessons with coding content.
Does NOT seed any user data — users create their own data via registration + onboarding.

Run: venv\Scripts\python.exe seed.py
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()


def seed_concepts():
    """Seed the programming concepts taxonomy"""
    count = db.session.execute(text("SELECT COUNT(*) FROM concepts")).scalar()
    if count > 0:
        print(f"  ℹ️  Concepts already exist ({count} found)")
        return

    concepts = [
        # Fundamentals
        ('Variables', 'fundamentals', 'Variable declaration, assignment, and naming conventions', 1, '[]', '["basics", "python"]'),
        ('Data Types', 'fundamentals', 'Primitive and complex data types: int, float, str, bool', 2, '[]', '["basics", "python"]'),
        ('Type Conversion', 'fundamentals', 'Converting between data types using int(), str(), float()', 3, '["Variables", "Data Types"]', '["basics"]'),
        ('String Operations', 'fundamentals', 'String methods, formatting, slicing, and concatenation', 3, '["Variables", "Data Types"]', '["strings", "python"]'),
        ('Input/Output', 'fundamentals', 'Reading user input and printing output', 2, '["Variables"]', '["basics", "io"]'),

        # Control Flow
        ('Conditionals', 'control_flow', 'If-else statements and boolean logic', 2, '["Variables", "Data Types"]', '["logic", "branching"]'),
        ('Boolean Logic', 'control_flow', 'AND, OR, NOT operations and truth tables', 3, '["Conditionals"]', '["logic"]'),
        ('Loops - While', 'control_flow', 'While loops and loop conditions', 3, '["Conditionals"]', '["loops", "iteration"]'),
        ('Loops - For', 'control_flow', 'For loops and range-based iteration', 3, '["Conditionals"]', '["loops", "iteration"]'),
        ('Loop Control', 'control_flow', 'Break, continue, and loop flow control', 4, '["Loops - While", "Loops - For"]', '["loops"]'),
        ('Nested Loops', 'control_flow', 'Loops within loops for 2D patterns', 5, '["Loops - For"]', '["loops", "patterns"]'),

        # Functions
        ('Functions - Basics', 'functions', 'Function definition, parameters, and return values', 3, '["Variables", "Conditionals"]', '["functions", "modular"]'),
        ('Scope', 'functions', 'Local vs global scope, variable lifetime', 4, '["Functions - Basics"]', '["functions"]'),
        ('Recursion', 'functions', 'Recursive function calls and base cases', 6, '["Functions - Basics"]', '["functions", "advanced"]'),
        ('Higher-Order Functions', 'functions', 'Functions as parameters — map, filter, lambda', 7, '["Functions - Basics"]', '["functions", "advanced"]'),

        # Data Structures
        ('Lists', 'data_structures', 'List operations, indexing, slicing, and methods', 3, '["Variables", "Loops - For"]', '["collections"]'),
        ('List Comprehensions', 'data_structures', 'Concise list creation and filtering', 5, '["Lists", "Loops - For"]', '["collections", "pythonic"]'),
        ('Dictionaries', 'data_structures', 'Key-value pairs, hash maps, dict methods', 4, '["Variables", "Loops - For"]', '["collections"]'),
        ('Sets', 'data_structures', 'Unique collections and set operations', 4, '["Variables"]', '["collections"]'),
        ('Tuples', 'data_structures', 'Immutable sequences and tuple unpacking', 3, '["Variables"]', '["collections"]'),

        # Complexity & Algorithms
        ('Time Complexity', 'complexity', 'Big O notation and runtime analysis', 7, '["Functions - Basics", "Loops - For"]', '["algorithms"]'),
        ('Space Complexity', 'complexity', 'Memory usage analysis', 7, '["Time Complexity"]', '["algorithms"]'),
        ('Algorithm Optimization', 'complexity', 'Improving algorithm efficiency', 8, '["Time Complexity"]', '["algorithms", "advanced"]'),

        # Debugging
        ('Edge Case Handling', 'debugging', 'Identifying and handling edge cases', 5, '["Conditionals", "Functions - Basics"]', '["debugging", "quality"]'),
        ('Debugging Strategy', 'debugging', 'Systematic approaches: print debugging, bisection', 6, '["Functions - Basics"]', '["debugging"]'),
        ('Error Types', 'debugging', 'Syntax, logic, and runtime errors', 4, '["Variables", "Functions - Basics"]', '["debugging"]'),
        ('Exception Handling', 'debugging', 'Try-except blocks and error recovery', 6, '["Functions - Basics", "Error Types"]', '["debugging", "python"]'),

        # Code Quality
        ('Code Readability', 'quality', 'Writing clear, understandable code with comments', 4, '["Variables", "Functions - Basics"]', '["quality"]'),
        ('Naming Conventions', 'quality', 'Meaningful variable and function names', 3, '["Variables"]', '["quality", "style"]'),
        ('DRY Principle', 'quality', "Don't Repeat Yourself — code reusability", 6, '["Functions - Basics"]', '["quality", "design"]'),
    ]

    now_str = db.session.execute(text("SELECT datetime('now')")).scalar()
    for name, category, description, difficulty, prereqs, tags in concepts:
        db.session.execute(text("""
            INSERT INTO concepts (name, category, description, difficulty_level,
                                  prerequisite_concepts, tags, created_at)
            VALUES (:name, :cat, :desc, :diff, :prereqs, :tags, :now)
        """), {
            'name': name, 'cat': category, 'desc': description,
            'diff': difficulty, 'prereqs': prereqs, 'tags': tags, 'now': now_str
        })
    db.session.commit()
    print(f"  ✅ Seeded {len(concepts)} concepts")


def seed_lessons():
    """Seed real lessons with coding content"""
    count = db.session.execute(text("SELECT COUNT(*) FROM lessons")).scalar()
    if count > 0:
        print(f"  ℹ️  Lessons already exist ({count} found)")
        return

    import json
    lessons = [
        # --- FUNDAMENTALS ---
        {
            'title': 'Hello World — Your First Program',
            'description': 'Write your very first Python program and learn how print() works.',
            'difficulty': 'beginner',
            'order': 1,
            'content': json.dumps({
                'concept': 'Input/Output',
                'sections': [
                    {'type': 'intro', 'heading': 'Welcome to Coding!', 'text': 'Every programmer starts here. The print() function displays text on the screen.'},
                    {'type': 'explanation', 'heading': 'How print() works', 'text': 'print() takes a string (text in quotes) and displays it.\n\nExample:\n```python\nprint("Hello, World!")\n```\n\nYou can print numbers too:\n```python\nprint(42)\nprint(3.14)\n```'},
                    {'type': 'practice', 'task': 'Write a program that prints "Hello, CodeNest!" to the screen.', 'starter_code': '# Type your code below\n', 'expected_output': 'Hello, CodeNest!'},
                    {'type': 'quiz', 'question': 'What does print() do?', 'options': ['Reads input from user', 'Displays output on screen', 'Creates a variable', 'Runs a loop'], 'answer': 'Displays output on screen'}
                ]
            }),
            'prerequisite_lessons': json.dumps([])
        },
        {
            'title': 'Variables — Storing Data',
            'description': 'Learn to create variables and store different types of data.',
            'difficulty': 'beginner',
            'order': 2,
            'content': json.dumps({
                'concept': 'Variables',
                'sections': [
                    {'type': 'intro', 'heading': 'What are Variables?', 'text': 'Variables are like labeled boxes that store data. You can name them anything meaningful.'},
                    {'type': 'explanation', 'heading': 'Creating Variables', 'text': 'In Python, you create a variable by assigning a value:\n\n```python\nname = "Alice"\nage = 25\nheight = 5.6\nis_student = True\n```\n\nPython figures out the type automatically!'},
                    {'type': 'practice', 'task': 'Create a variable called "greeting" with the value "Welcome to CodeNest" and print it.', 'starter_code': '# Create your variable here\n\n# Print it\n', 'expected_output': 'Welcome to CodeNest'},
                    {'type': 'quiz', 'question': 'Which is a valid variable name in Python?', 'options': ['2name', 'my-var', 'my_name', 'class'], 'answer': 'my_name'}
                ]
            }),
            'prerequisite_lessons': json.dumps([])
        },
        {
            'title': 'Data Types — Numbers and Strings',
            'description': 'Understand the difference between integers, floats, strings, and booleans.',
            'difficulty': 'beginner',
            'order': 3,
            'content': json.dumps({
                'concept': 'Data Types',
                'sections': [
                    {'type': 'intro', 'heading': 'Types of Data', 'text': 'Every value in Python has a type. The main types are: int (whole numbers), float (decimals), str (text), and bool (True/False).'},
                    {'type': 'explanation', 'heading': 'Checking Types', 'text': '```python\nprint(type(42))        # <class \'int\'>\nprint(type(3.14))      # <class \'float\'>\nprint(type("hello"))   # <class \'str\'>\nprint(type(True))      # <class \'bool\'>\n```\n\nYou can convert between types:\n```python\nnum_str = "42"\nnum = int(num_str)  # converts string to integer\n```'},
                    {'type': 'practice', 'task': 'Create variables: age (integer 20), price (float 9.99), name (string "Python"). Print each one on a separate line.', 'starter_code': '# Create your variables\n\n# Print each one\n', 'expected_output': '20\n9.99\nPython'},
                    {'type': 'quiz', 'question': 'What is the type of 3.14?', 'options': ['int', 'str', 'float', 'bool'], 'answer': 'float'}
                ]
            }),
            'prerequisite_lessons': json.dumps([1, 2])
        },
        {
            'title': 'String Magic — Manipulating Text',
            'description': 'Learn to slice, format, and transform strings.',
            'difficulty': 'beginner',
            'order': 4,
            'content': json.dumps({
                'concept': 'String Operations',
                'sections': [
                    {'type': 'intro', 'heading': 'Strings are Powerful!', 'text': 'Strings in Python come with built-in superpowers — you can slice, search, replace, and format them.'},
                    {'type': 'explanation', 'heading': 'String Methods', 'text': '```python\ntext = "Hello, World!"\n\n# Methods\nprint(text.upper())       # HELLO, WORLD!\nprint(text.lower())       # hello, world!\nprint(text.replace("World", "Python"))  # Hello, Python!\nprint(len(text))          # 13\n\n# f-strings (formatting)\nname = "Alice"\nage = 25\nprint(f"My name is {name} and I am {age} years old")\n```'},
                    {'type': 'practice', 'task': 'Given name = "codenest", print it in uppercase.', 'starter_code': 'name = "codenest"\n# Print name in uppercase\n', 'expected_output': 'CODENEST'},
                    {'type': 'quiz', 'question': 'What does "hello".upper() return?', 'options': ['hello', 'Hello', 'HELLO', 'hELLO'], 'answer': 'HELLO'}
                ]
            }),
            'prerequisite_lessons': json.dumps([2, 3])
        },

        # --- CONTROL FLOW ---
        {
            'title': 'If-Else — Making Decisions',
            'description': 'Use conditionals to make your program choose between different paths.',
            'difficulty': 'beginner',
            'order': 5,
            'content': json.dumps({
                'concept': 'Conditionals',
                'sections': [
                    {'type': 'intro', 'heading': 'Decision Time!', 'text': 'Programs need to make decisions. The if-else statement lets your code choose what to do based on conditions.'},
                    {'type': 'explanation', 'heading': 'How If-Else Works', 'text': '```python\nage = 18\n\nif age >= 18:\n    print("You can vote!")\nelse:\n    print("Too young to vote.")\n\n# Multiple conditions with elif\nscore = 85\nif score >= 90:\n    print("Grade: A")\nelif score >= 80:\n    print("Grade: B")\nelif score >= 70:\n    print("Grade: C")\nelse:\n    print("Grade: F")\n```'},
                    {'type': 'practice', 'task': 'Write a program: if number = 15, print "Positive" if it\'s greater than 0, "Negative" if less than 0, "Zero" otherwise.', 'starter_code': 'number = 15\n# Write your if-elif-else here\n', 'expected_output': 'Positive'},
                    {'type': 'quiz', 'question': 'What keyword is used for additional conditions after if?', 'options': ['else if', 'elif', 'elseif', 'otherwise'], 'answer': 'elif'}
                ]
            }),
            'prerequisite_lessons': json.dumps([2, 3])
        },
        {
            'title': 'For Loops — Repeating with Style',
            'description': 'Use for loops to iterate over sequences and ranges.',
            'difficulty': 'beginner',
            'order': 6,
            'content': json.dumps({
                'concept': 'Loops - For',
                'sections': [
                    {'type': 'intro', 'heading': 'Stop Repeating Yourself!', 'text': 'Instead of writing the same code 10 times, loops let you repeat automatically.'},
                    {'type': 'explanation', 'heading': 'The for Loop', 'text': '```python\n# Loop with range\nfor i in range(5):\n    print(i)  # prints 0, 1, 2, 3, 4\n\n# Loop over a list\nfruits = ["apple", "banana", "cherry"]\nfor fruit in fruits:\n    print(fruit)\n\n# Sum numbers 1 to 10\ntotal = 0\nfor i in range(1, 11):\n    total += i\nprint(total)  # 55\n```'},
                    {'type': 'practice', 'task': 'Use a for loop to print numbers from 1 to 5, each on a new line.', 'starter_code': '# Write your for loop\n', 'expected_output': '1\n2\n3\n4\n5'},
                    {'type': 'quiz', 'question': 'What does range(3) produce?', 'options': ['1, 2, 3', '0, 1, 2', '0, 1, 2, 3', '1, 2'], 'answer': '0, 1, 2'}
                ]
            }),
            'prerequisite_lessons': json.dumps([5])
        },
        {
            'title': 'While Loops — Loop Until Done',
            'description': 'Use while loops when you don\'t know how many times to repeat.',
            'difficulty': 'intermediate',
            'order': 7,
            'content': json.dumps({
                'concept': 'Loops - While',
                'sections': [
                    {'type': 'intro', 'heading': 'Looping with Conditions', 'text': 'While loops keep going as long as a condition is True. Perfect when you don\'t know the exact number of iterations.'},
                    {'type': 'explanation', 'heading': 'While Loop Basics', 'text': '```python\n# Countdown\ncount = 5\nwhile count > 0:\n    print(count)\n    count -= 1\nprint("Blast off!")\n\n# Sum until threshold\ntotal = 0\nn = 1\nwhile total < 100:\n    total += n\n    n += 1\nprint(f"Sum reached {total} after {n-1} numbers")\n```\n\n⚠️ Always make sure the condition will eventually become False, or you\'ll create an infinite loop!'},
                    {'type': 'practice', 'task': 'Write a while loop that prints numbers from 1 to 5.', 'starter_code': '# Write your while loop\n', 'expected_output': '1\n2\n3\n4\n5'},
                    {'type': 'quiz', 'question': 'When does a while loop stop?', 'options': ['After a set number of iterations', 'When the condition becomes False', 'When it hits a return statement', 'Never'], 'answer': 'When the condition becomes False'}
                ]
            }),
            'prerequisite_lessons': json.dumps([5])
        },
        {
            'title': 'Nested Loops — Patterns and Grids',
            'description': 'Combine loops to create patterns and work with 2D data.',
            'difficulty': 'intermediate',
            'order': 8,
            'content': json.dumps({
                'concept': 'Nested Loops',
                'sections': [
                    {'type': 'intro', 'heading': 'Loops Inside Loops', 'text': 'When you put a loop inside another loop, the inner loop runs completely for each iteration of the outer loop.'},
                    {'type': 'explanation', 'heading': 'Building Patterns', 'text': '```python\n# Print a 3x3 grid of stars\nfor row in range(3):\n    for col in range(3):\n        print("*", end=" ")\n    print()  # new line after each row\n# Output:\n# * * *\n# * * *\n# * * *\n\n# Multiplication table\nfor i in range(1, 4):\n    for j in range(1, 4):\n        print(f"{i}x{j}={i*j}", end="  ")\n    print()\n```'},
                    {'type': 'practice', 'task': 'Print a right triangle of stars with 3 rows:\n*\n* *\n* * *', 'starter_code': '# Build the triangle\n', 'expected_output': '*\n* *\n* * *'},
                    {'type': 'quiz', 'question': 'How many times does the inner loop run in total for range(3) nested in range(4)?', 'options': ['3', '4', '7', '12'], 'answer': '12'}
                ]
            }),
            'prerequisite_lessons': json.dumps([6])
        },

        # --- FUNCTIONS ---
        {
            'title': 'Functions — Reusable Code Blocks',
            'description': 'Create your own functions to organize and reuse code.',
            'difficulty': 'intermediate',
            'order': 9,
            'content': json.dumps({
                'concept': 'Functions - Basics',
                'sections': [
                    {'type': 'intro', 'heading': 'Write Once, Use Many Times', 'text': 'Functions let you package code into reusable blocks. Define once, call anywhere!'},
                    {'type': 'explanation', 'heading': 'Defining Functions', 'text': '```python\n# Basic function\ndef greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("Alice"))  # Hello, Alice!\n\n# Function with default parameter\ndef power(base, exponent=2):\n    return base ** exponent\n\nprint(power(3))      # 9\nprint(power(2, 10))  # 1024\n\n# Multiple return values\ndef min_max(numbers):\n    return min(numbers), max(numbers)\n\nlo, hi = min_max([3, 1, 7, 2])\nprint(f"Min: {lo}, Max: {hi}")\n```'},
                    {'type': 'practice', 'task': 'Write a function called "add" that takes two numbers and returns their sum. Then print add(3, 5).', 'starter_code': '# Define your function\n\n# Call it\n', 'expected_output': '8'},
                    {'type': 'quiz', 'question': 'What keyword is used to send a value back from a function?', 'options': ['send', 'output', 'return', 'give'], 'answer': 'return'}
                ]
            }),
            'prerequisite_lessons': json.dumps([5, 6])
        },
        {
            'title': 'Recursion — Functions Calling Themselves',
            'description': 'Understand recursive thinking and solve problems by breaking them into smaller pieces.',
            'difficulty': 'advanced',
            'order': 10,
            'content': json.dumps({
                'concept': 'Recursion',
                'sections': [
                    {'type': 'intro', 'heading': 'The Power of Self-Reference', 'text': 'A recursive function calls itself with a simpler version of the problem until it reaches a base case.'},
                    {'type': 'explanation', 'heading': 'Recursion in Action', 'text': '```python\n# Factorial: n! = n * (n-1)!\ndef factorial(n):\n    if n <= 1:        # Base case\n        return 1\n    return n * factorial(n - 1)  # Recursive call\n\nprint(factorial(5))  # 120\n\n# Fibonacci\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(7):\n    print(fibonacci(i), end=" ")  # 0 1 1 2 3 5 8\n```\n\n⚠️ Every recursive function MUST have a base case, otherwise it will recurse forever!'},
                    {'type': 'practice', 'task': 'Write a recursive function "countdown" that prints numbers from n down to 1. Call it with countdown(5).', 'starter_code': '# Write your recursive function\n\n# Call it\ncountdown(5)\n', 'expected_output': '5\n4\n3\n2\n1'},
                    {'type': 'quiz', 'question': 'What is the base case in a recursive function?', 'options': ['The first call', 'The condition that stops recursion', 'The recursive call itself', 'The return value'], 'answer': 'The condition that stops recursion'}
                ]
            }),
            'prerequisite_lessons': json.dumps([9])
        },

        # --- DATA STRUCTURES ---
        {
            'title': 'Lists — Ordered Collections',
            'description': 'Store multiple values in a single variable and manipulate them.',
            'difficulty': 'beginner',
            'order': 11,
            'content': json.dumps({
                'concept': 'Lists',
                'sections': [
                    {'type': 'intro', 'heading': 'Collections of Data', 'text': 'Lists let you store multiple values in order. You can add, remove, sort, and search through them.'},
                    {'type': 'explanation', 'heading': 'Working with Lists', 'text': '```python\n# Creating lists\nfruits = ["apple", "banana", "cherry"]\nnumbers = [1, 2, 3, 4, 5]\n\n# Accessing elements (0-indexed)\nprint(fruits[0])    # apple\nprint(fruits[-1])   # cherry\n\n# Common methods\nfruits.append("date")     # Add to end\nfruits.insert(1, "avocado")  # Insert at index\nfruits.remove("banana")   # Remove by value\n\n# Slicing\nprint(numbers[1:4])  # [2, 3, 4]\nprint(numbers[:3])   # [1, 2, 3]\n```'},
                    {'type': 'practice', 'task': 'Create a list called "colors" with ["red", "green", "blue"]. Append "yellow" to it, then print the list.', 'starter_code': '# Create your list and modify it\n', 'expected_output': "['red', 'green', 'blue', 'yellow']"},
                    {'type': 'quiz', 'question': 'What index is the first element of a list in Python?', 'options': ['1', '0', '-1', 'first'], 'answer': '0'}
                ]
            }),
            'prerequisite_lessons': json.dumps([6])
        },
        {
            'title': 'Dictionaries — Key-Value Pairs',
            'description': 'Store data as key-value pairs for fast lookups.',
            'difficulty': 'intermediate',
            'order': 12,
            'content': json.dumps({
                'concept': 'Dictionaries',
                'sections': [
                    {'type': 'intro', 'heading': 'Data with Labels', 'text': 'Dictionaries store data as key-value pairs — like a real dictionary maps words to definitions.'},
                    {'type': 'explanation', 'heading': 'Dict Operations', 'text': '```python\n# Creating a dictionary\nstudent = {\n    "name": "Alice",\n    "age": 20,\n    "grade": "A"\n}\n\n# Accessing values\nprint(student["name"])     # Alice\nprint(student.get("age"))  # 20\n\n# Adding/updating\nstudent["email"] = "alice@school.com"\nstudent["age"] = 21\n\n# Looping\nfor key, value in student.items():\n    print(f"{key}: {value}")\n```'},
                    {'type': 'practice', 'task': 'Create a dictionary called "person" with keys "name" (value "Bob") and "age" (value 30). Print the name.', 'starter_code': '# Create your dictionary\n\n# Print the name\n', 'expected_output': 'Bob'},
                    {'type': 'quiz', 'question': 'How do you access the value for key "name" in a dict called d?', 'options': ['d.name', 'd("name")', 'd["name"]', 'd{name}'], 'answer': 'd["name"]'}
                ]
            }),
            'prerequisite_lessons': json.dumps([6, 11])
        },
        {
            'title': 'List Comprehensions — Pythonic Power',
            'description': 'Create lists in one elegant line using comprehensions.',
            'difficulty': 'intermediate',
            'order': 13,
            'content': json.dumps({
                'concept': 'List Comprehensions',
                'sections': [
                    {'type': 'intro', 'heading': 'Elegant List Creation', 'text': 'List comprehensions are a concise, Pythonic way to create lists from existing sequences.'},
                    {'type': 'explanation', 'heading': 'Comprehension Syntax', 'text': '```python\n# Traditional way\nsquares = []\nfor x in range(10):\n    squares.append(x ** 2)\n\n# Comprehension way — same result!\nsquares = [x ** 2 for x in range(10)]\n\n# With filtering\nevens = [x for x in range(20) if x % 2 == 0]\n\n# String processing\nwords = ["hello", "world", "python"]\nupper = [w.upper() for w in words]\nprint(upper)  # [\'HELLO\', \'WORLD\', \'PYTHON\']\n```'},
                    {'type': 'practice', 'task': 'Use a list comprehension to create a list of squares from 1 to 5: [1, 4, 9, 16, 25]. Print the list.', 'starter_code': '# Use a list comprehension\n', 'expected_output': '[1, 4, 9, 16, 25]'},
                    {'type': 'quiz', 'question': 'What does [x*2 for x in range(3)] produce?', 'options': ['[2, 4, 6]', '[0, 2, 4]', '[1, 2, 3]', '[0, 1, 2]'], 'answer': '[0, 2, 4]'}
                ]
            }),
            'prerequisite_lessons': json.dumps([6, 11])
        },

        # --- DEBUGGING ---
        {
            'title': 'Error Types — Understanding Bugs',
            'description': 'Learn to identify and fix syntax, runtime, and logic errors.',
            'difficulty': 'intermediate',
            'order': 14,
            'content': json.dumps({
                'concept': 'Error Types',
                'sections': [
                    {'type': 'intro', 'heading': 'Bugs Happen!', 'text': 'Every programmer encounters errors. The key is knowing what type of error you\'re dealing with.'},
                    {'type': 'explanation', 'heading': 'Three Types of Errors', 'text': '**Syntax Errors** — Code that Python can\'t understand:\n```python\n# Missing colon\nif True\n    print("oops")  # SyntaxError!\n```\n\n**Runtime Errors** — Code crashes while running:\n```python\nprint(10 / 0)  # ZeroDivisionError!\nprint(int("abc"))  # ValueError!\n```\n\n**Logic Errors** — Code runs but gives wrong results:\n```python\n# Meant to calculate average\ndef average(a, b):\n    return a + b / 2  # Bug! Should be (a + b) / 2\n```'},
                    {'type': 'practice', 'task': 'Fix this code so it correctly prints the average of 10 and 20:\n\ndef average(a, b):\n    return a + b / 2\n\nprint(average(10, 20))', 'starter_code': 'def average(a, b):\n    return a + b / 2\n\nprint(average(10, 20))\n', 'expected_output': '15.0'},
                    {'type': 'quiz', 'question': 'What type of error is: forgetting a colon after an if statement?', 'options': ['Logic Error', 'Runtime Error', 'Syntax Error', 'Type Error'], 'answer': 'Syntax Error'}
                ]
            }),
            'prerequisite_lessons': json.dumps([9])
        },
        {
            'title': 'Exception Handling — Try/Except',
            'description': 'Gracefully handle errors so your program doesn\'t crash.',
            'difficulty': 'advanced',
            'order': 15,
            'content': json.dumps({
                'concept': 'Exception Handling',
                'sections': [
                    {'type': 'intro', 'heading': 'Catch Errors Gracefully', 'text': 'Instead of crashing, you can catch errors with try/except and handle them.'},
                    {'type': 'explanation', 'heading': 'Try/Except Blocks', 'text': '```python\ntry:\n    number = int(input("Enter a number: "))\n    result = 100 / number\n    print(f"Result: {result}")\nexcept ValueError:\n    print("That\'s not a valid number!")\nexcept ZeroDivisionError:\n    print("Cannot divide by zero!")\nfinally:\n    print("This always runs.")\n```\n\nYou can also use `else` for code that runs only if no error occurred:\n```python\ntry:\n    value = int("42")\nexcept ValueError:\n    print("Error!")\nelse:\n    print(f"Success! Value = {value}")\n```'},
                    {'type': 'practice', 'task': 'Write a try/except that tries to convert "hello" to int, catches ValueError, and prints "Invalid number".', 'starter_code': '# Use try/except\n', 'expected_output': 'Invalid number'},
                    {'type': 'quiz', 'question': 'Which block runs regardless of whether an error occurred?', 'options': ['try', 'except', 'else', 'finally'], 'answer': 'finally'}
                ]
            }),
            'prerequisite_lessons': json.dumps([14])
        },
    ]

    for lesson in lessons:
        db.session.execute(text("""
            INSERT INTO lessons (title, description, difficulty, "order", content, prerequisite_lessons, created_at)
            VALUES (:title, :desc, :diff, :ord, :content, :prereqs, datetime('now'))
        """), {
            'title': lesson['title'],
            'desc': lesson['description'],
            'diff': lesson['difficulty'],
            'ord': lesson['order'],
            'content': lesson['content'],
            'prereqs': lesson['prerequisite_lessons']
        })
    db.session.commit()
    print(f"  ✅ Seeded {len(lessons)} lessons")


def seed_challenges():
    """Seed coding challenges with real test cases"""
    count = db.session.execute(text("SELECT COUNT(*) FROM challenges")).scalar()
    if count > 0:
        print(f"  ℹ️  Challenges already exist ({count} found)")
        return

    import json
    challenges = [
        {
            'title': 'FizzBuzz',
            'description': 'Print numbers 1-20. For multiples of 3 print "Fizz", multiples of 5 print "Buzz", both print "FizzBuzz".',
            'difficulty': 'easy',
            'category': 'control_flow',
            'points': 50,
            'min_level': 1,
            'test_cases': json.dumps([
                {'input': '', 'expected': '1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n16\n17\nFizz\n19\nBuzz'}
            ]),
            'hints': json.dumps(['Use the modulo operator (%) to check divisibility', 'Check for divisibility by 15 first (both 3 and 5)', 'Remember: order of checks matters!'])
        },
        {
            'title': 'Reverse a String',
            'description': 'Write a function that reverses a string without using the built-in reverse method or [::-1].',
            'difficulty': 'easy',
            'category': 'functions',
            'points': 40,
            'min_level': 1,
            'test_cases': json.dumps([
                {'input': 'hello', 'expected': 'olleh'},
                {'input': 'Python', 'expected': 'nohtyP'},
                {'input': '', 'expected': ''}
            ]),
            'hints': json.dumps(['Try building a new string character by character', 'You can loop through the string backwards using range(len(s)-1, -1, -1)'])
        },
        {
            'title': 'Count Vowels',
            'description': 'Write a function that counts the number of vowels (a, e, i, o, u) in a given string (case-insensitive).',
            'difficulty': 'easy',
            'category': 'functions',
            'points': 30,
            'min_level': 1,
            'test_cases': json.dumps([
                {'input': 'Hello World', 'expected': '3'},
                {'input': 'Python', 'expected': '1'},
                {'input': 'AEIOU', 'expected': '5'}
            ]),
            'hints': json.dumps(['Convert the string to lowercase first', 'Check if each character is in "aeiou"'])
        },
        {
            'title': 'Find the Maximum',
            'description': 'Write a function that finds the maximum value in a list WITHOUT using the built-in max() function.',
            'difficulty': 'easy',
            'category': 'data_structures',
            'points': 40,
            'min_level': 1,
            'test_cases': json.dumps([
                {'input': '[3, 1, 4, 1, 5, 9]', 'expected': '9'},
                {'input': '[-1, -5, -2]', 'expected': '-1'},
                {'input': '[42]', 'expected': '42'}
            ]),
            'hints': json.dumps(['Start by assuming the first element is the max', 'Loop through and update if you find something bigger'])
        },
        {
            'title': 'Palindrome Checker',
            'description': 'Write a function that checks if a string is a palindrome (reads the same forwards and backwards). Ignore case and spaces.',
            'difficulty': 'medium',
            'category': 'functions',
            'points': 60,
            'min_level': 2,
            'test_cases': json.dumps([
                {'input': 'racecar', 'expected': 'True'},
                {'input': 'hello', 'expected': 'False'},
                {'input': 'A man a plan a canal Panama', 'expected': 'True'}
            ]),
            'hints': json.dumps(['First clean the string: remove spaces, convert to lowercase', 'Compare the cleaned string with its reverse'])
        },
        {
            'title': 'Two Sum',
            'description': 'Given a list of numbers and a target, return the indices of the two numbers that add up to the target.',
            'difficulty': 'medium',
            'category': 'data_structures',
            'points': 80,
            'min_level': 3,
            'test_cases': json.dumps([
                {'input': '[2, 7, 11, 15], target=9', 'expected': '[0, 1]'},
                {'input': '[3, 2, 4], target=6', 'expected': '[1, 2]'}
            ]),
            'hints': json.dumps(['A brute-force approach uses two nested loops — O(n²)', 'For O(n), use a dictionary to store numbers you\'ve seen'])
        },
        {
            'title': 'Fibonacci Generator',
            'description': 'Write a function that returns the first n Fibonacci numbers as a list.',
            'difficulty': 'medium',
            'category': 'functions',
            'points': 70,
            'min_level': 2,
            'test_cases': json.dumps([
                {'input': '5', 'expected': '[0, 1, 1, 2, 3]'},
                {'input': '8', 'expected': '[0, 1, 1, 2, 3, 5, 8, 13]'},
                {'input': '1', 'expected': '[0]'}
            ]),
            'hints': json.dumps(['Each number is the sum of the previous two', 'Handle n=1 and n=2 as special cases', 'Build the list iteratively for better performance'])
        },
    ]

    for ch in challenges:
        db.session.execute(text("""
            INSERT INTO challenges (title, description, difficulty, category, points,
                                    min_level, test_cases, hints, created_at)
            VALUES (:title, :desc, :diff, :cat, :pts, :ml, :tc, :hints, datetime('now'))
        """), {
            'title': ch['title'], 'desc': ch['description'], 'diff': ch['difficulty'],
            'cat': ch['category'], 'pts': ch['points'], 'ml': ch['min_level'],
            'tc': ch['test_cases'], 'hints': ch['hints']
        })
    db.session.commit()
    print(f"  ✅ Seeded {len(challenges)} challenges")


def seed_scaffolded_challenges():
    """Seed scaffolded beginner challenges (fill_in_blank, predict_output, error_spotting)."""
    import json
    # Only seed if none exist yet
    count = db.session.execute(
        text("SELECT COUNT(*) FROM challenges WHERE challenge_mode != 'freeform'")
    ).scalar()
    if count > 0:
        print(f"  ℹ️  Scaffolded challenges already exist ({count} found)")
        return

    challenges = [
        # ── Fill-in-the-Blank ──────────────────────────────────────────────
        {
            'title': '[Scaffold] Print Numbers 1–5',
            'description': 'Fill in the blank so the loop prints numbers 1 through 5.',
            'difficulty': 'easy',
            'category': 'control_flow',
            'points': 10,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'fill_in_blank',
                'template': 'for i in range(___, ___):\n    print(i)',
                'blanks': ['1', '6'],
                'blank_labels': ['Start (inclusive)', 'Stop (exclusive)'],
                'explanation': (
                    'range(start, stop) generates numbers from start up to — '
                    'but not including — stop. To get 1 through 5, use range(1, 6).'
                ),
            },
            'expected_output': '1\n2\n3\n4\n5',
            'hints': json.dumps(['range(start, stop) — stop is not included.']),
        },
        {
            'title': '[Scaffold] Sum a List',
            'description': 'Fill in the blank to accumulate a running total of the list.',
            'difficulty': 'easy',
            'category': 'data_structures',
            'points': 10,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'fill_in_blank',
                'template': (
                    'numbers = [1, 2, 3, 4, 5]\n'
                    'total = ___\n'
                    'for n in numbers:\n'
                    '    total = total + n\n'
                    'print(total)'
                ),
                'blanks': ['0'],
                'blank_labels': ['What should total start at before summing?'],
                'explanation': (
                    'An accumulator variable starts at 0. '
                    'Each loop iteration adds one number to it. '
                    'Starting at any other value shifts the final result.'
                ),
            },
            'expected_output': '15',
            'hints': json.dumps(['An accumulator usually starts at 0.']),
        },

        # ── Predict-the-Output ─────────────────────────────────────────────
        {
            'title': '[Scaffold] What Does range() Print?',
            'description': 'Predict what this loop prints before running it.',
            'difficulty': 'easy',
            'category': 'control_flow',
            'points': 10,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'predict_output',
                'code': 'for i in range(5):\n    print(i)',
                'correct_output': '0\n1\n2\n3\n4',
                'explanation': (
                    'range(5) starts at 0 and stops before 5. '
                    'Many beginners expect it to print 1–5, '
                    'but Python lists start counting at 0.'
                ),
                'fault_keywords': ['range', 'zero', '0'],
            },
            'expected_output': '0\n1\n2\n3\n4',
            'hints': json.dumps(['range(n) starts at 0, not 1.']),
        },
        {
            'title': '[Scaffold] Variable Reassignment',
            'description': 'Trace this code and predict the final printed value.',
            'difficulty': 'easy',
            'category': 'fundamentals',
            'points': 10,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'predict_output',
                'code': 'x = 5\nx = x + 3\nx = x * 2\nprint(x)',
                'correct_output': '16',
                'explanation': (
                    'x starts at 5, becomes 8 after x + 3, '
                    'then becomes 16 after x * 2. '
                    'Each assignment overwrites the previous value.'
                ),
                'fault_keywords': ['overwrites', 'assignment', 'value'],
            },
            'expected_output': '16',
            'hints': json.dumps(['Each = replaces the previous value.']),
        },

        # ── Error Spotting ─────────────────────────────────────────────────
        {
            'title': '[Scaffold] Spot the NameError',
            'description': (
                'This code crashes with a NameError. '
                'Identify the faulty line number and explain why.'
            ),
            'difficulty': 'easy',
            'category': 'debugging',
            'points': 15,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'error_spotting',
                'buggy_code': (
                    'greeting = "Hello"\n'
                    'print(greting)'
                ),
                'fault_line': 2,
                'fault_keywords': ['typo', 'spelling', 'name', 'undefined', 'greting'],
                'explanation': (
                    'Line 2 references `greting` — a spelling mistake. '
                    'Python treats differently-spelled names as completely different variables. '
                    'Always match your variable names exactly.'
                ),
            },
            'expected_output': 'Hello',
            'hints': json.dumps(['Compare the variable name where it was created vs where it is used.']),
        },
        {
            'title': '[Scaffold] Spot the Off-By-One',
            'description': (
                'This loop should print 1 through 5 but prints the wrong numbers. '
                'Identify the line with the logic error.'
            ),
            'difficulty': 'easy',
            'category': 'control_flow',
            'points': 15,
            'min_level': 1,
            'challenge_mode': 'scaffolded',
            'scaffold_data': {
                'type': 'error_spotting',
                'buggy_code': 'for i in range(5):\n    print(i)',
                'fault_line': 1,
                'fault_keywords': ['range', 'zero', 'off-by-one', 'start', '0'],
                'explanation': (
                    'range(5) produces 0–4, not 1–5. '
                    'To start at 1 and include 5, use range(1, 6). '
                    'This is the classic off-by-one loop error in Python.'
                ),
            },
            'expected_output': '1\n2\n3\n4\n5',
            'hints': json.dumps(['range(n) starts at 0. Use range(1, 6) for 1 through 5.']),
        },
    ]

    for ch in challenges:
        db.session.execute(text("""
            INSERT INTO challenges
                (title, description, difficulty, category, points, min_level,
                 challenge_mode, scaffold_data, expected_output, hints, created_at)
            VALUES
                (:title, :desc, :diff, :cat, :pts, :ml,
                 :mode, :scaffold, :expected, :hints, datetime('now'))
        """), {
            'title': ch['title'],
            'desc': ch['description'],
            'diff': ch['difficulty'],
            'cat': ch['category'],
            'pts': ch['points'],
            'ml': ch['min_level'],
            'mode': ch['challenge_mode'],
            'scaffold': json.dumps(ch['scaffold_data']),
            'expected': ch.get('expected_output', ''),
            'hints': ch.get('hints', '[]'),
        })

    db.session.commit()
    print(f"  ✅ Seeded {len(challenges)} scaffolded challenges")


def seed_data():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created\n")

        print("📚 Seeding concepts...")
        seed_concepts()

        print("📖 Seeding lessons...")
        seed_lessons()

        print("🏆 Seeding challenges...")
        seed_challenges()

        print("🧩 Seeding scaffolded beginner challenges...")
        seed_scaffolded_challenges()

        print("\n🎉 Database seeded successfully!")
        print("   No user data seeded — users create their own via registration + onboarding.")


if __name__ == "__main__":
    seed_data()

