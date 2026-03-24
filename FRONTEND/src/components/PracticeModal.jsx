import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL + '/api' : 'http://localhost:5000/api';

// ─── Concept Lessons (Learn phase) ───────────────────────────────────────────
const LESSONS = [
    {
        match: ['variable', 'variables', 'data type', 'data types', 'assignment'],
        title: 'Variables & Data Types',
        sections: [
            {
                heading: 'What is a variable?',
                body: 'A variable is like a labeled box that stores data. You give it a name and put a value inside.',
                code: 'name = "Alice"\nage = 25',
            },
            {
                heading: 'Python has several types',
                body: null,
                bullets: [
                    '**str** → text: `"hello"`',
                    '**int** → whole numbers: `42`',
                    '**float** → decimals: `3.14`',
                    '**bool** → True or False',
                ],
            },
            {
                heading: 'Check the type',
                body: 'Use `type()` to see what kind of data a variable holds.',
                code: 'print(type(name))  # <class \'str\'>\nprint(type(age))   # <class \'int\'>',
            },
        ],
        keyTakeaway: 'Variables store data. Python auto-detects the type — no need to declare it!',
    },
    {
        match: ['loop', 'loops', 'for loop', 'while loop', 'iteration', 'iterating'],
        title: 'Loops',
        sections: [
            {
                heading: 'Why loops?',
                body: 'Instead of writing the same code 10 times, use a loop to repeat it automatically.',
            },
            {
                heading: 'For Loop',
                body: 'Runs a fixed number of times. `range(1, 6)` gives you 1, 2, 3, 4, 5.',
                code: 'for i in range(1, 6):\n    print(i)  # prints 1 to 5',
            },
            {
                heading: 'While Loop',
                body: 'Keeps running as long as a condition is True. Don\'t forget to update the variable!',
                code: 'count = 3\nwhile count > 0:\n    print(count)\n    count -= 1  # countdown!',
            },
        ],
        keyTakeaway: 'Use `for` when you know how many times. Use `while` when you have a condition.',
    },
    {
        match: ['function', 'functions', 'def', 'return', 'parameter', 'argument'],
        title: 'Functions',
        sections: [
            {
                heading: 'What is a function?',
                body: 'A function is a reusable block of code. Define it once, call it anytime.',
                code: 'def greet(name):\n    return f"Hello, {name}!"',
            },
            {
                heading: 'Parameters & Return',
                body: null,
                bullets: [
                    '**Parameters** go inside the parentheses `(name)`',
                    '**return** sends a value back to whoever called the function',
                    'Without return, the function returns `None`',
                ],
            },
            {
                heading: 'Calling a function',
                body: 'Use the function name followed by parentheses with arguments.',
                code: 'result = greet("Alice")\nprint(result)  # Hello, Alice!',
            },
        ],
        keyTakeaway: 'Functions make code reusable. Define with `def`, pass data in, get results with `return`.',
    },
    {
        match: ['list', 'array', 'lists', 'arrays', 'indexing'],
        title: 'Lists',
        sections: [
            {
                heading: 'What is a list?',
                body: 'A list stores multiple items in order. Think of it as a numbered collection.',
                code: 'fruits = ["apple", "banana", "cherry"]',
            },
            {
                heading: 'Common operations',
                body: null,
                bullets: [
                    '**Access**: `fruits[0]` → `"apple"` (starts at 0!)',
                    '**Add**: `fruits.append("date")`',
                    '**Remove**: `fruits.remove("banana")`',
                    '**Length**: `len(fruits)` → how many items',
                ],
            },
            {
                heading: 'Loop through a list',
                body: 'Use a for loop to visit every item.',
                code: 'for fruit in fruits:\n    print(fruit)',
            },
        ],
        keyTakeaway: 'Lists hold ordered collections. Index starts at 0. Use append/remove to modify.',
    },
    {
        match: ['dictionary', 'dict', 'hash', 'key', 'value', 'mapping'],
        title: 'Dictionaries',
        sections: [
            {
                heading: 'What is a dictionary?',
                body: 'A dictionary maps keys to values — like a real dictionary maps words to definitions.',
                code: 'person = {"name": "Alice", "age": 25}',
            },
            {
                heading: 'Common operations',
                body: null,
                bullets: [
                    '**Access**: `person["name"]` → `"Alice"`',
                    '**Add**: `person["email"] = "alice@email.com"`',
                    '**Delete**: `del person["age"]`',
                    '**Check**: `"name" in person` → `True`',
                ],
            },
            {
                heading: 'Loop through items',
                code: 'for key, value in person.items():\n    print(f"{key}: {value}")',
            },
        ],
        keyTakeaway: 'Dictionaries store key-value pairs. Use `{}` to create, `[]` to access.',
    },
    {
        match: ['class', 'object', 'oop', 'inheritance', 'method', 'encapsulation', 'polymorphism'],
        title: 'Object-Oriented Programming',
        sections: [
            {
                heading: 'What is a class?',
                body: 'A class is a blueprint for creating objects. Objects hold both data and behavior.',
                code: 'class Dog:\n    def __init__(self, name):\n        self.name = name\n\n    def bark(self):\n        return f"{self.name} says Woof!"',
            },
            {
                heading: 'Key concepts',
                bullets: [
                    '**`__init__`** — the constructor, runs when you create an object',
                    '**`self`** — refers to the current object instance',
                    '**Inheritance** — a class can extend another class',
                ],
            },
            {
                heading: 'Creating & using objects',
                code: 'my_dog = Dog("Rex")\nprint(my_dog.bark())  # Rex says Woof!',
            },
        ],
        keyTakeaway: 'Classes = blueprints, Objects = instances. Use `self` to access instance data.',
    },
    {
        match: ['recursion', 'recursive'],
        title: 'Recursion',
        sections: [
            {
                heading: 'What is recursion?',
                body: 'A function that calls itself! It breaks big problems into smaller identical ones.',
            },
            {
                heading: 'Two key parts',
                bullets: [
                    '**Base case** — when to STOP (prevents infinite loops)',
                    '**Recursive case** — the function calls itself with a smaller input',
                ],
            },
            {
                heading: 'Example: Factorial',
                body: '5! = 5 × 4 × 3 × 2 × 1 = 120',
                code: 'def factorial(n):\n    if n <= 1:      # base case\n        return 1\n    return n * factorial(n - 1)  # recursive',
            },
        ],
        keyTakeaway: 'Recursion = function calls itself. Always have a base case to stop!',
    },
    {
        match: ['exception', 'error', 'try', 'except', 'error handling', 'raise'],
        title: 'Error Handling',
        sections: [
            {
                heading: 'Why handle errors?',
                body: 'Programs crash when unexpected things happen. Error handling lets you catch mistakes gracefully.',
            },
            {
                heading: 'try / except',
                body: 'Wrap risky code in `try`. If it fails, `except` catches the error.',
                code: 'try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print("Can\'t divide by zero!")',
            },
            {
                heading: 'finally',
                body: '`finally` runs no matter what — error or not. Great for cleanup.',
                code: 'try:\n    file = open("data.txt")\nexcept FileNotFoundError:\n    print("File missing!")\nfinally:\n    print("Done trying")',
            },
        ],
        keyTakeaway: 'Use try/except to catch errors. `finally` always runs. Never let your program crash!',
    },
    {
        match: ['sorting', 'sort', 'algorithm', 'search', 'binary search', 'bubble sort'],
        title: 'Sorting Algorithms',
        sections: [
            {
                heading: 'Why sorting matters',
                body: 'Sorted data is easier to search, display, and analyze. Sorting is a fundamental CS concept.',
            },
            {
                heading: 'Bubble Sort (simple)',
                body: 'Repeatedly swaps adjacent elements if they\'re in the wrong order. Simple but slow for large lists.',
                code: 'def bubble_sort(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr) - i - 1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]',
            },
            {
                heading: 'Python\'s built-in',
                body: 'Python has super-fast built-in sorting. Use it in practice!',
                code: 'numbers = [64, 34, 25, 12]\nprint(sorted(numbers))  # [12, 25, 34, 64]',
            },
        ],
        keyTakeaway: 'Understand the basics, but use `sorted()` or `.sort()` in real code — they\'re optimized!',
    },
    {
        match: ['string', 'strings', 'string manipulation', 'concatenation', 'slicing'],
        title: 'String Manipulation',
        sections: [
            {
                heading: 'What are strings?',
                body: 'Strings are sequences of characters. In Python, they\'re surrounded by quotes.',
                code: 'text = "Hello, World!"',
            },
            {
                heading: 'Useful operations',
                bullets: [
                    '**Slice**: `text[0:5]` → `"Hello"`',
                    '**Reverse**: `text[::-1]` → `"!dlroW ,olleH"`',
                    '**Upper/Lower**: `text.upper()`, `text.lower()`',
                    '**Split**: `"a,b,c".split(",")` → `["a","b","c"]`',
                ],
            },
            {
                heading: 'f-strings (formatted)',
                body: 'The easiest way to insert variables into text.',
                code: 'name = "Alice"\nprint(f"Hello, {name}!")  # Hello, Alice!',
            },
        ],
        keyTakeaway: 'Strings are immutable sequences. Use slicing, methods, and f-strings to work with them.',
    },
    {
        match: ['conditional', 'if', 'else', 'elif', 'boolean', 'comparison'],
        title: 'Conditionals',
        sections: [
            {
                heading: 'Making decisions in code',
                body: 'Conditionals let your program choose different paths based on conditions.',
                code: 'age = 18\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")',
            },
            {
                heading: 'elif for multiple checks',
                body: 'Use `elif` (else if) when you have more than two options.',
                code: 'score = 85\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelse:\n    grade = "C"',
            },
            {
                heading: 'Comparison operators',
                bullets: [
                    '`==` equals, `!=` not equals',
                    '`>` `<` `>=` `<=` comparisons',
                    '`and`, `or`, `not` for combining',
                ],
            },
        ],
        keyTakeaway: 'Use `if/elif/else` to branch logic. Conditions evaluate to True or False.',
    },
];

const DEFAULT_LESSON = {
    title: 'Concept Overview',
    sections: [
        {
            heading: 'About this concept',
            body: 'This is a programming concept you\'ll encounter frequently. Read through the description, then try the practice exercise to reinforce your understanding.',
        },
        {
            heading: 'How to practice',
            bullets: [
                'Read the exercise prompt carefully',
                'Write code that demonstrates the concept',
                'Use comments to explain your approach',
                'Submit to track your mastery progress',
            ],
        },
    ],
    keyTakeaway: 'Understanding comes through practice. Write code, make mistakes, and learn from them!',
};

function getLesson(concept) {
    const nameLower = (concept.name || '').toLowerCase();
    const descLower = (concept.description || '').toLowerCase();
    const combined = `${nameLower} ${descLower}`;
    return (
        LESSONS.find(l => l.match.some(kw => combined.includes(kw))) ||
        { ...DEFAULT_LESSON, title: concept.name || 'Concept Overview' }
    );
}

// ─── Concept-specific exercises ───────────────────────────────────────────────
const EXERCISES = [
    {
        match: ['variable', 'variables', 'data type', 'data types', 'assignment'],
        prompt: 'Declare variables of different types (integer, float, string, boolean) and print their values and types.',
        starterCode: `# Variables Practice
name = "Alice"
age = 25
height = 5.6
is_student = True

print(f"Name: {name}, Type: {type(name)}")
# Add more variables below
`,
        checkKeywords: ['=', 'print'],
    },
    {
        match: ['loop', 'loops', 'for loop', 'while loop', 'iteration', 'iterating'],
        prompt: 'Write a for loop that prints the numbers 1–10, and a while loop that counts down from 5 to 1.',
        starterCode: `# Loops Practice
# For loop: print 1 to 10
for i in range(1, 11):
    print(i)

# While loop: countdown from 5
count = 5
while count > 0:
    print(count)
    count -= 1
`,
        checkKeywords: ['for', 'while', 'range'],
    },
    {
        match: ['function', 'functions', 'def', 'return', 'parameter', 'argument'],
        prompt: 'Write a function that takes two numbers and returns their sum, and another that checks if a number is even.',
        starterCode: `# Functions Practice
def add(a, b):
    return a + b

def is_even(n):
    return n % 2 == 0

print(add(3, 4))       # 7
print(is_even(6))      # True
`,
        checkKeywords: ['def', 'return'],
    },
    {
        match: ['list', 'array', 'lists', 'arrays', 'indexing'],
        prompt: 'Create a list, add items, remove an item, and iterate over it printing each element.',
        starterCode: `# Lists Practice
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
fruits.remove("banana")

for fruit in fruits:
    print(fruit)

print(f"Total: {len(fruits)} fruits")
`,
        checkKeywords: ['append', 'for', '['],
    },
    {
        match: ['dictionary', 'dict', 'hash', 'key', 'value', 'mapping'],
        prompt: 'Create a dictionary representing a person, add a key, delete a key, and loop over its items.',
        starterCode: `# Dictionaries Practice
person = {"name": "Alice", "age": 25, "city": "NYC"}
person["email"] = "alice@example.com"
del person["city"]

for key, value in person.items():
    print(f"{key}: {value}")
`,
        checkKeywords: ['{', 'for', '.items()'],
    },
    {
        match: ['class', 'object', 'oop', 'inheritance', 'method', 'encapsulation', 'polymorphism'],
        prompt: 'Create a class `Animal` with a `speak()` method, then create a subclass `Dog` that overrides it.',
        starterCode: `# OOP Practice
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

dog = Dog("Rex")
print(dog.speak())
`,
        checkKeywords: ['class', 'def', 'self'],
    },
    {
        match: ['recursion', 'recursive'],
        prompt: 'Write a recursive function to calculate the factorial of a number, and one for Fibonacci.',
        starterCode: `# Recursion Practice
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(factorial(5))  # 120
print(fibonacci(7))  # 13
`,
        checkKeywords: ['def', 'return', 'if'],
    },
    {
        match: ['exception', 'error', 'try', 'except', 'error handling', 'raise'],
        prompt: 'Write a function that divides two numbers and handles ZeroDivisionError and TypeError gracefully.',
        starterCode: `# Exception Handling Practice
def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        return "Error: Cannot divide by zero"
    except TypeError:
        return "Error: Invalid types"
    finally:
        print("Division attempted")

print(safe_divide(10, 2))
print(safe_divide(10, 0))
`,
        checkKeywords: ['try', 'except'],
    },
    {
        match: ['sorting', 'sort', 'algorithm', 'search', 'binary search', 'bubble sort'],
        prompt: 'Implement bubble sort on a list, then use Python\'s built-in sort for comparison.',
        starterCode: `# Sorting Practice
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
print("Bubble sort:", bubble_sort(numbers.copy()))
print("Built-in sort:", sorted(numbers))
`,
        checkKeywords: ['def', 'for', 'if'],
    },
    {
        match: ['string', 'strings', 'string manipulation', 'concatenation', 'slicing'],
        prompt: 'Perform string operations: reverse a string, count vowels, and convert to title case.',
        starterCode: `# String Manipulation Practice
text = "hello world from python"

# Reverse
reversed_text = text[::-1]

# Count vowels
vowels = sum(1 for c in text if c in 'aeiou')

# Title case
titled = text.title()

print(f"Original: {text}")
print(f"Reversed: {reversed_text}")
print(f"Vowels: {vowels}")
print(f"Title: {titled}")
`,
        checkKeywords: ['[::', 'for', '.title()'],
    },
    {
        match: ['conditional', 'if', 'else', 'elif', 'boolean', 'comparison'],
        prompt: 'Write a program that checks if a number is positive, negative, or zero, and if it\'s even or odd.',
        starterCode: `# Conditionals Practice
number = 7

if number > 0:
    print(f"{number} is positive")
elif number < 0:
    print(f"{number} is negative")
else:
    print("It's zero")

if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")
`,
        checkKeywords: ['if', 'elif', 'else'],
    },
];

const DEFAULT_EXERCISE = {
    prompt: 'Write a solution demonstrating your understanding of this concept. Include comments explaining your approach.',
    starterCode: `# Practice: Apply the concept here
# Add your code below:

`,
    checkKeywords: [],
};

function getExercise(concept) {
    const nameLower = (concept.name || '').toLowerCase();
    const descLower = (concept.description || '').toLowerCase();
    const combined = `${nameLower} ${descLower}`;
    return (
        EXERCISES.find(ex => ex.match.some(kw => combined.includes(kw))) ||
        DEFAULT_EXERCISE
    );
}

function evaluateCode(code, keywords) {
    const codeLower = code.toLowerCase();
    if (keywords.length === 0) return code.trim().length > 30;
    const hits = keywords.filter(kw => codeLower.includes(kw.toLowerCase()));
    return hits.length >= Math.ceil(keywords.length * 0.6);
}

// Encouraging messages
const SUCCESS_MESSAGES = [
    { emoji: '🎉', title: 'Amazing!', sub: 'You nailed it!' },
    { emoji: '🔥', title: 'On fire!', sub: 'Keep this streak going!' },
    { emoji: '⭐', title: 'Brilliant!', sub: 'You\'re a natural!' },
    { emoji: '🚀', title: 'Awesome!', sub: 'Sky\'s the limit!' },
    { emoji: '💎', title: 'Perfect!', sub: 'You crushed it!' },
];
const RETRY_MESSAGES = [
    { emoji: '💪', title: 'Almost there!', sub: 'A small tweak and you\'ve got it.' },
    { emoji: '🧠', title: 'Good effort!', sub: 'Try re-reading the task.' },
    { emoji: '🌱', title: 'Keep growing!', sub: 'Every attempt makes you better.' },
];

function pickRandom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

// Simple markdown-ish bold rendering
function renderBold(text) {
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) =>
        i % 2 === 1
            ? <strong key={i} className="font-bold text-gray-900">{part}</strong>
            : <span key={i}>{part}</span>
    );
}

// Simple inline code rendering
function renderInlineCode(text) {
    const parts = text.split(/`(.*?)`/g);
    return parts.map((part, i) =>
        i % 2 === 1
            ? <code key={i} className="px-1.5 py-0.5 bg-gray-800 text-green-300 rounded text-xs font-mono">{part}</code>
            : <span key={i}>{renderBold(part)}</span>
    );
}

// ─── Duolingo-style PracticeModal with Learn → Practice flow ─────────────────
export default function PracticeModal({ concept, token, onClose, onMasteryUpdated }) {
    const exercise = getExercise(concept);
    const lesson = getLesson(concept);

    // Phase: 'learn' or 'practice'
    const [phase, setPhase] = useState('learn');
    const [lessonStep, setLessonStep] = useState(0);

    const [code, setCode] = useState(exercise.starterCode);
    const [submitting, setSubmitting] = useState(false);
    const [result, setResult] = useState(null);
    const [hintsUsed, setHintsUsed] = useState(0);
    const [hintText, setHintText] = useState(null);
    const [showConfetti, setShowConfetti] = useState(false);
    const [feedbackMsg, setFeedbackMsg] = useState(null);
    const startTimeRef = useRef(Date.now());

    useEffect(() => {
        setPhase('learn');
        setLessonStep(0);
        startTimeRef.current = Date.now();
        setCode(exercise.starterCode);
        setResult(null);
        setHintsUsed(0);
        setHintText(null);
        setShowConfetti(false);
        setFeedbackMsg(null);
    }, [concept.id]);

    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = ''; };
    }, []);

    const totalLessonSteps = lesson.sections.length + 1; // sections + key takeaway
    const lessonProgress = ((lessonStep + 1) / totalLessonSteps) * 50; // learn = 0-50%
    const practiceProgress = result?.success ? 100 : result ? 75 : 55; // practice = 50-100%
    const progress = phase === 'learn' ? lessonProgress : practiceProgress;

    const handleNextLesson = () => {
        if (lessonStep < lesson.sections.length) {
            setLessonStep(s => s + 1);
        } else {
            // Move to practice phase
            setPhase('practice');
            startTimeRef.current = Date.now();
        }
    };

    const handlePrevLesson = () => {
        if (lessonStep > 0) setLessonStep(s => s - 1);
    };

    const handleSubmit = async () => {
        if (!code.trim() || submitting) return;
        setSubmitting(true);

        const timeTaken = Math.max(1, Math.round((Date.now() - startTimeRef.current) / 1000));
        const success = evaluateCode(code, exercise.checkKeywords);

        try {
            if (!token) throw new Error('Not logged in');
            await axios.post(
                `${API_BASE}/cognitive/update`,
                {
                    concept_id: concept.id,
                    success,
                    time_taken: timeTaken,
                    hints_used: hintsUsed,
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            if (success) {
                setFeedbackMsg(pickRandom(SUCCESS_MESSAGES));
                setShowConfetti(true);
                setTimeout(() => setShowConfetti(false), 3000);
            } else {
                setFeedbackMsg(pickRandom(RETRY_MESSAGES));
            }

            setResult({ success, timeTaken });
            onMasteryUpdated?.();
        } catch (err) {
            if (err.message === 'Not logged in') {
                setResult({ error: 'You must be logged in to track mastery.' });
            } else {
                setResult({ error: 'Failed to submit. Check that the backend is running.' });
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleTryAgain = () => {
        setResult(null);
        setHintText(null);
        setFeedbackMsg(null);
        startTimeRef.current = Date.now();
    };

    const generateHint = () => {
        const level = hintsUsed;
        const kw = exercise.checkKeywords;
        let hint;
        if (level === 0 && kw.length > 0) {
            hint = `Try using: ${kw.slice(0, 2).map(k => '`' + k + '`').join(', ')}`;
        } else if (level === 1) {
            hint = `Read the task again carefully. Make sure your code addresses every part.`;
        } else if (level === 2 && kw.length > 2) {
            hint = `You may also need: ${kw.slice(2).map(k => '`' + k + '`').join(', ')}`;
        } else {
            hint = `Look at what you learned in the lesson and apply those patterns here.`;
        }
        setHintText(hint);
        setHintsUsed(h => h + 1);
    };

    const diffLabel = concept.difficulty_level <= 3
        ? { text: 'Beginner', bg: 'bg-green-500' }
        : concept.difficulty_level <= 6
            ? { text: 'Intermediate', bg: 'bg-yellow-500' }
            : { text: 'Advanced', bg: 'bg-red-500' };

    const xpEarned = result?.success
        ? Math.max(5, 15 - hintsUsed * 3 - Math.floor((result.timeTaken || 0) / 60))
        : 0;

    // ─── RENDER ──────────────────────────────────────────────────────────────
    return (
        <div className="fixed inset-0 z-50 flex flex-col" style={{ background: '#f7f7f7' }}>

            {/* Confetti */}
            {showConfetti && (
                <div className="fixed inset-0 z-[60] pointer-events-none overflow-hidden">
                    {Array.from({ length: 40 }).map((_, i) => (
                        <div
                            key={i}
                            className="absolute"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `-${Math.random() * 20 + 5}%`,
                                width: `${Math.random() * 10 + 6}px`,
                                height: `${Math.random() * 10 + 6}px`,
                                background: ['#58CC02', '#FF4B4B', '#1CB0F6', '#FF9600', '#CE82FF', '#FFD900'][i % 6],
                                borderRadius: Math.random() > 0.5 ? '50%' : '2px',
                                animation: `confettiFall ${1.5 + Math.random() * 2}s ease-in forwards`,
                                animationDelay: `${Math.random() * 0.5}s`,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* ═══════ Top Bar ═══════ */}
            <div className="flex items-center gap-4 px-6 py-3 bg-white border-b border-gray-200 flex-shrink-0">
                <button
                    onClick={onClose}
                    className="w-10 h-10 rounded-full flex items-center justify-center text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-all text-xl"
                >
                    ✕
                </button>

                {/* Progress bar */}
                <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full transition-all duration-700 ease-out"
                        style={{
                            width: `${progress}%`,
                            background: 'linear-gradient(90deg, #58CC02, #46a302)',
                        }}
                    />
                </div>

                {/* Phase indicator */}
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${phase === 'learn' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>
                        {phase === 'learn' ? '📖 LEARN' : '✍️ PRACTICE'}
                    </span>
                    <span className={`px-2 py-0.5 text-white text-xs font-bold rounded-full ${diffLabel.bg}`}>
                        {diffLabel.text}
                    </span>
                </div>
            </div>

            {/* ═══════ Main Content ═══════ */}
            <div className="flex-1 overflow-y-auto">
                <div className="max-w-2xl mx-auto px-6 py-6">

                    {/* ═══════════════════════════════════════════════════════
                        LEARN PHASE
                    ═══════════════════════════════════════════════════════ */}
                    {phase === 'learn' && (
                        <div>
                            {/* Lesson title */}
                            <div className="mb-6">
                                <div className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1">
                                    {concept.category?.replace(/_/g, ' ')}
                                </div>
                                <h1 className="text-2xl font-extrabold text-gray-900">
                                    {lesson.title}
                                </h1>
                                {concept.description && (
                                    <p className="text-gray-500 text-sm mt-1">{concept.description}</p>
                                )}
                            </div>

                            {/* Lesson step dots */}
                            <div className="flex items-center gap-2 mb-6">
                                {lesson.sections.map((_, i) => (
                                    <div
                                        key={i}
                                        className={`h-2 flex-1 rounded-full transition-all duration-300 ${i <= lessonStep ? 'bg-blue-500' : 'bg-gray-200'}`}
                                    />
                                ))}
                                <div className={`h-2 flex-1 rounded-full transition-all duration-300 ${lessonStep >= lesson.sections.length ? 'bg-green-500' : 'bg-gray-200'}`} />
                            </div>

                            {/* Current lesson card */}
                            {lessonStep < lesson.sections.length ? (
                                <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm overflow-hidden" style={{ animation: 'slideIn 0.3s ease-out' }}>
                                    <div className="px-6 py-5">
                                        {/* Section number */}
                                        <div className="flex items-center gap-3 mb-4">
                                            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-extrabold text-sm">
                                                {lessonStep + 1}
                                            </div>
                                            <h2 className="text-lg font-bold text-gray-900">
                                                {lesson.sections[lessonStep].heading}
                                            </h2>
                                        </div>

                                        {/* Body text */}
                                        {lesson.sections[lessonStep].body && (
                                            <p className="text-gray-600 text-sm leading-relaxed mb-4">
                                                {renderInlineCode(lesson.sections[lessonStep].body)}
                                            </p>
                                        )}

                                        {/* Bullet points */}
                                        {lesson.sections[lessonStep].bullets && (
                                            <ul className="space-y-2 mb-4">
                                                {lesson.sections[lessonStep].bullets.map((bullet, i) => (
                                                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                                                        <span className="text-blue-500 mt-0.5 flex-shrink-0">●</span>
                                                        <span>{renderInlineCode(bullet)}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        )}

                                        {/* Code example */}
                                        {lesson.sections[lessonStep].code && (
                                            <div className="rounded-xl overflow-hidden border border-gray-700">
                                                <div className="bg-gray-800 px-3 py-1.5 flex items-center gap-1.5">
                                                    <div className="w-3 h-3 rounded-full bg-red-400" />
                                                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                                                    <div className="w-3 h-3 rounded-full bg-green-400" />
                                                    <span className="ml-2 text-xs text-gray-400 font-mono">example.py</span>
                                                </div>
                                                <pre className="bg-gray-900 text-green-300 text-sm font-mono p-4 overflow-x-auto">
                                                    {lesson.sections[lessonStep].code}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                /* Key Takeaway card */
                                <div className="bg-white rounded-2xl border-2 border-green-200 shadow-sm overflow-hidden" style={{ animation: 'slideIn 0.3s ease-out' }}>
                                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 px-6 py-5">
                                        <div className="flex items-start gap-3">
                                            <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white text-xl flex-shrink-0">
                                                🎯
                                            </div>
                                            <div>
                                                <h2 className="text-lg font-bold text-green-800 mb-2">Key Takeaway</h2>
                                                <p className="text-green-700 text-sm leading-relaxed font-medium">
                                                    {lesson.keyTakeaway}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="px-6 py-4 bg-green-50/50 border-t border-green-100">
                                        <p className="text-sm text-green-600 text-center font-medium">
                                            ✨ Ready to practice? Click <strong>START PRACTICE</strong> to test what you've learned!
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* ═══════════════════════════════════════════════════════
                        PRACTICE PHASE
                    ═══════════════════════════════════════════════════════ */}
                    {phase === 'practice' && (
                        <div>
                            {/* Result Screen */}
                            {result && !result.error && feedbackMsg && (
                                <div className={`rounded-2xl p-8 text-center mb-6 ${result.success
                                    ? 'bg-gradient-to-b from-green-50 to-white border-2 border-green-200'
                                    : 'bg-gradient-to-b from-amber-50 to-white border-2 border-amber-200'
                                    }`}>
                                    <div className="text-6xl mb-3" style={{ animation: 'popIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)' }}>
                                        {feedbackMsg.emoji}
                                    </div>
                                    <h2 className={`text-3xl font-extrabold mb-1 ${result.success ? 'text-green-600' : 'text-amber-600'}`}>
                                        {feedbackMsg.title}
                                    </h2>
                                    <p className="text-gray-500 text-lg mb-4">{feedbackMsg.sub}</p>

                                    {result.success && (
                                        <div className="inline-flex items-center gap-2 bg-yellow-100 text-yellow-700 px-4 py-2 rounded-full font-bold text-sm">
                                            <span className="text-lg">⚡</span>
                                            +{xpEarned} XP earned
                                        </div>
                                    )}

                                    {result.success && (
                                        <div className="mt-5">
                                            <div className="text-xs text-gray-400 mb-1 font-semibold uppercase tracking-wide">Mastery Progress</div>
                                            <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full rounded-full"
                                                    style={{
                                                        width: `${Math.min(100, 25 + Math.random() * 20)}%`,
                                                        background: 'linear-gradient(90deg, #58CC02, #46a302)',
                                                        transition: 'width 1.5s ease-out',
                                                    }}
                                                />
                                            </div>
                                            <div className="text-xs text-gray-400 mt-1">
                                                Completed in {result.timeTaken}s · Keep practicing to reach 80%!
                                            </div>
                                        </div>
                                    )}

                                    {!result.success && (
                                        <div className="mt-4 text-sm text-gray-500">
                                            Revisit the lesson or click 💡 for hints!
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Error */}
                            {result?.error && (
                                <div className="rounded-2xl p-6 mb-6 bg-red-50 border-2 border-red-200 text-center">
                                    <div className="text-4xl mb-2">😅</div>
                                    <h3 className="font-bold text-red-700 text-lg">{result.error}</h3>
                                </div>
                            )}

                            {/* Exercise (when no result) */}
                            {!result && (
                                <>
                                    <div className="mb-4">
                                        <h1 className="text-2xl font-extrabold text-gray-900 mb-1">
                                            Now let's practice! ✍️
                                        </h1>
                                        <p className="text-gray-500 text-sm">
                                            Apply what you just learned about <strong>{lesson.title}</strong>.
                                        </p>
                                    </div>

                                    {/* Task Card */}
                                    <div className="bg-white rounded-2xl border-2 border-gray-200 shadow-sm overflow-hidden mb-4">
                                        <div className="px-5 py-4 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-indigo-50">
                                            <div className="flex items-start gap-3">
                                                <div className="w-8 h-8 rounded-xl bg-blue-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                                                    <span className="text-white text-sm font-bold">🎯</span>
                                                </div>
                                                <div>
                                                    <div className="text-xs font-bold text-blue-600 uppercase tracking-wide mb-0.5">Your Task</div>
                                                    <p className="text-sm text-gray-700 leading-relaxed font-medium">{exercise.prompt}</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-3 h-3 rounded-full bg-red-400" />
                                                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                                                    <div className="w-3 h-3 rounded-full bg-green-400" />
                                                    <span className="ml-2 text-xs text-gray-400 font-mono">python</span>
                                                </div>
                                                <button
                                                    onClick={() => { setCode(exercise.starterCode); setResult(null); }}
                                                    className="text-xs text-gray-400 hover:text-gray-600 transition-colors font-medium"
                                                >
                                                    ↺ Reset code
                                                </button>
                                            </div>
                                            <textarea
                                                className="w-full font-mono text-sm bg-gray-900 text-green-300 p-4 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-green-400"
                                                style={{ minHeight: '220px' }}
                                                value={code}
                                                onChange={e => { setCode(e.target.value); if (result) setResult(null); }}
                                                spellCheck={false}
                                                autoComplete="off"
                                                autoCorrect="off"
                                                placeholder="Write your code here..."
                                            />
                                        </div>
                                    </div>

                                    {/* Hint */}
                                    {hintText && (
                                        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-4 mb-4 flex items-start gap-3">
                                            <div className="w-8 h-8 rounded-full bg-yellow-400 flex items-center justify-center flex-shrink-0 text-sm">💡</div>
                                            <div>
                                                <div className="text-xs font-bold text-yellow-700 uppercase tracking-wide mb-0.5">Hint</div>
                                                <p className="text-sm text-yellow-800">{hintText}</p>
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* ═══════ Bottom Action Bar ═══════ */}
            <div className="flex-shrink-0 border-t-2 border-gray-200 bg-white px-6 py-4">
                <div className="max-w-2xl mx-auto">

                    {/* ── Learn phase bottom ── */}
                    {phase === 'learn' && (
                        <div className="flex items-center justify-between">
                            <button
                                onClick={handlePrevLesson}
                                disabled={lessonStep === 0}
                                className="px-5 py-3 rounded-xl border-2 border-gray-200 text-gray-400 hover:text-gray-600 hover:border-gray-300 transition-all font-bold text-sm disabled:opacity-30 disabled:cursor-not-allowed"
                            >
                                ← BACK
                            </button>

                            <div className="flex items-center gap-3">
                                {lessonStep < lesson.sections.length && (
                                    <button
                                        onClick={() => { setPhase('practice'); startTimeRef.current = Date.now(); }}
                                        className="px-5 py-3 rounded-xl border-2 border-gray-200 text-gray-400 hover:text-gray-600 transition-all font-bold text-sm"
                                    >
                                        SKIP TO PRACTICE
                                    </button>
                                )}
                                <button
                                    onClick={handleNextLesson}
                                    className="px-8 py-3 rounded-xl font-extrabold text-sm text-white transition-all"
                                    style={{
                                        background: lessonStep >= lesson.sections.length ? '#58CC02' : '#1CB0F6',
                                        boxShadow: `0 4px 0 ${lessonStep >= lesson.sections.length ? '#46a302' : '#1899d6'}`,
                                    }}
                                    onMouseDown={e => { e.currentTarget.style.transform = 'translateY(2px)'; e.currentTarget.style.boxShadow = `0 2px 0 ${lessonStep >= lesson.sections.length ? '#46a302' : '#1899d6'}`; }}
                                    onMouseUp={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 0 ${lessonStep >= lesson.sections.length ? '#46a302' : '#1899d6'}`; }}
                                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 0 ${lessonStep >= lesson.sections.length ? '#46a302' : '#1899d6'}`; }}
                                >
                                    {lessonStep >= lesson.sections.length ? 'START PRACTICE →' : 'CONTINUE'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ── Practice phase bottom (no result) ── */}
                    {phase === 'practice' && !result && (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={generateHint}
                                    className="flex items-center gap-2 px-4 py-3 rounded-xl border-2 border-gray-200 text-gray-500 hover:border-yellow-300 hover:bg-yellow-50 hover:text-yellow-700 transition-all font-bold text-sm"
                                >
                                    <span className="text-lg">💡</span>
                                    {hintsUsed === 0 ? 'Hint' : `Hint (${hintsUsed})`}
                                </button>
                                <button
                                    onClick={() => { setPhase('learn'); setLessonStep(0); }}
                                    className="flex items-center gap-2 px-4 py-3 rounded-xl border-2 border-gray-200 text-gray-500 hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 transition-all font-bold text-sm"
                                >
                                    <span className="text-lg">📖</span>
                                    Review Lesson
                                </button>
                            </div>
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={onClose}
                                    className="px-5 py-3 rounded-xl border-2 border-gray-200 text-gray-400 hover:text-gray-600 hover:border-gray-300 transition-all font-bold text-sm"
                                >
                                    SKIP
                                </button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={submitting || !code.trim()}
                                    className="px-8 py-3 rounded-xl font-extrabold text-sm text-white transition-all disabled:opacity-40"
                                    style={{
                                        background: submitting ? '#a0a0a0' : '#58CC02',
                                        boxShadow: submitting ? 'none' : '0 4px 0 #46a302',
                                    }}
                                    onMouseDown={e => { if (!submitting) { e.currentTarget.style.transform = 'translateY(2px)'; e.currentTarget.style.boxShadow = '0 2px 0 #46a302'; } }}
                                    onMouseUp={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 0 #46a302'; }}
                                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 0 #46a302'; }}
                                >
                                    {submitting ? (
                                        <span className="flex items-center gap-2">
                                            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            CHECKING...
                                        </span>
                                    ) : 'CHECK'}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* ── Practice phase bottom (with result) ── */}
                    {phase === 'practice' && result && (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                {result.success ? (
                                    <div className="flex items-center gap-2 text-green-600 font-bold">
                                        <span className="text-2xl">✅</span>
                                        <span>Correct!</span>
                                    </div>
                                ) : result.error ? (
                                    <div className="flex items-center gap-2 text-red-600 font-bold">
                                        <span className="text-2xl">❌</span>
                                        <span>Error</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 text-amber-600 font-bold">
                                        <span className="text-2xl">💪</span>
                                        <span>Almost!</span>
                                    </div>
                                )}
                            </div>
                            <div className="flex items-center gap-3">
                                {!result.success && !result.error && (
                                    <>
                                        <button
                                            onClick={() => { setPhase('learn'); setLessonStep(0); setResult(null); }}
                                            className="px-5 py-3 rounded-xl border-2 border-blue-200 text-blue-600 hover:bg-blue-50 transition-all font-bold text-sm"
                                        >
                                            📖 REVIEW LESSON
                                        </button>
                                        <button
                                            onClick={handleTryAgain}
                                            className="px-6 py-3 rounded-xl font-extrabold text-sm transition-all border-2 border-amber-300 text-amber-600 hover:bg-amber-50"
                                        >
                                            TRY AGAIN
                                        </button>
                                    </>
                                )}
                                <button
                                    onClick={result.success ? onClose : (result.error ? onClose : handleTryAgain)}
                                    className="px-8 py-3 rounded-xl font-extrabold text-sm text-white transition-all"
                                    style={{
                                        background: result.success ? '#58CC02' : result.error ? '#FF4B4B' : '#FFC800',
                                        boxShadow: `0 4px 0 ${result.success ? '#46a302' : result.error ? '#cc3c3c' : '#d4a600'}`,
                                    }}
                                    onMouseDown={e => { e.currentTarget.style.transform = 'translateY(2px)'; e.currentTarget.style.boxShadow = `0 2px 0 ${result.success ? '#46a302' : result.error ? '#cc3c3c' : '#d4a600'}`; }}
                                    onMouseUp={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 0 ${result.success ? '#46a302' : result.error ? '#cc3c3c' : '#d4a600'}`; }}
                                    onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 0 ${result.success ? '#46a302' : result.error ? '#cc3c3c' : '#d4a600'}`; }}
                                >
                                    {result.success ? 'CONTINUE' : result.error ? 'CLOSE' : 'GOT IT'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Animations */}
            <style>{`
                @keyframes confettiFall {
                    0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                    100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
                }
                @keyframes popIn {
                    0% { transform: scale(0); opacity: 0; }
                    60% { transform: scale(1.2); }
                    100% { transform: scale(1); opacity: 1; }
                }
                @keyframes slideIn {
                    0% { transform: translateX(30px); opacity: 0; }
                    100% { transform: translateX(0); opacity: 1; }
                }
            `}</style>
        </div>
    );
}
