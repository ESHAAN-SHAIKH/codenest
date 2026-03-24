"""
Seed script to populate concept taxonomy
Run with: python -m scripts.seed_concepts
"""

from app import create_app
from app.extensions import db
from app.cognitive_models.cognitive import Concept

def seed_concepts():
    """Seed the database with programming concepts"""
    
    app = create_app()
    
    with app.app_context():
        print("Seeding concept taxonomy...")
        
        concepts = [
            # Variables & Data Types (1-5)
            {
                'name': 'Variables',
                'category': 'fundamentals',
                'description': 'Understanding variable declaration, assignment, and naming conventions',
                'difficulty_level': 1,
                'prerequisite_concepts': [],
                'tags': ['beginner', 'fundamentals']
            },
            {
                'name': 'Data Types',
                'category': 'fundamentals',
                'description': 'Understanding primitive and complex data types',
                'difficulty_level': 2,
                'prerequisite_concepts': [1],  # Variables
                'tags': ['beginner', 'types']
            },
            {
                'name': 'Type Conversion',
                'category': 'fundamentals',
                'description': 'Converting between different data types',
                'difficulty_level': 3,
                'prerequisite_concepts': [2],  # Data Types
                'tags': ['beginner', 'types']
            },
            
            # Control Flow (6-10)
            {
                'name': 'Conditionals',
                'category': 'control_flow',
                'description': 'If-else statements and boolean logic',
                'difficulty_level': 2,
                'prerequisite_concepts': [1, 2],  # Variables, Data Types
                'tags': ['beginner', 'control_flow']
            },
            {
                'name': 'Boolean Logic',
                'category': 'control_flow',
                'description': 'AND, OR, NOT operations and compound conditions',
                'difficulty_level': 3,
                'prerequisite_concepts': [4],  # Conditionals
                'tags': ['beginner', 'logic']
            },
            {
                'name': 'Loops - While',
                'category': 'control_flow',
                'description': 'While loops and loop conditions',
                'difficulty_level': 3,
                'prerequisite_concepts': [4],  # Conditionals
                'tags': ['beginner', 'loops']
            },
            {
                'name': 'Loops - For',
                'category': 'control_flow',
                'description': 'For loops and iteration',
                'difficulty_level': 3,
                'prerequisite_concepts': [6],  # While loops
                'tags': ['beginner', 'loops']
            },
            {
                'name': 'Loop Control',
                'category': 'control_flow',
                'description': 'Break, continue, and loop flow control',
                'difficulty_level': 4,
                'prerequisite_concepts': [7],  # For loops
                'tags': ['intermediate', 'loops']
            },
            {
                'name': 'Nested Loops',
                'category': 'control_flow',
                'description': 'Loops within loops and complexity analysis',
                'difficulty_level': 5,
                'prerequisite_concepts': [7, 8],  # For loops, Loop Control
                'tags': ['intermediate', 'loops', 'complexity']
            },
            {
                'name': 'Loop Invariants',
                'category': 'control_flow',
                'description': 'Understanding loop invariants and correctness',
                'difficulty_level': 6,
                'prerequisite_concepts': [9],  # Nested loops
                'tags': ['intermediate', 'theory']
            },
            
            # Functions (11-15)
            {
                'name': 'Functions - Basics',
                'category': 'functions',
                'description': 'Function definition, parameters, and return values',
                'difficulty_level': 3,
                'prerequisite_concepts': [1, 2],  # Variables, Data Types
                'tags': ['beginner', 'functions']
            },
            {
                'name': 'Scope',
                'category': 'functions',
                'description': 'Local vs global scope and variable visibility',
                'difficulty_level': 4,
                'prerequisite_concepts': [11],  # Functions
                'tags': ['intermediate', 'scope']
            },
            {
                'name': 'Recursion',
                'category': 'functions',
                'description': 'Recursive function calls and base cases',
                'difficulty_level': 6,
                'prerequisite_concepts': [11, 12],  # Functions, Scope
                'tags': ['intermediate', 'recursion']
            },
            {
                'name': 'Recursion Reasoning',
                'category': 'functions',
                'description': 'Stack behavior and recursive thinking',
                'difficulty_level': 7,
                'prerequisite_concepts': [13],  # Recursion
                'tags': ['intermediate', 'recursion', 'theory']
            },
            {
                'name': 'Higher-Order Functions',
                'category': 'functions',
                'description': 'Functions as parameters and return values',
                'difficulty_level': 7,
                'prerequisite_concepts': [11, 12],  # Functions, Scope
                'tags': ['advanced', 'functions']
            },
            
            # Data Structures (16-22)
            {
                'name': 'Lists',
                'category': 'data_structures',
                'description': 'List operations, indexing, and slicing',
                'difficulty_level': 3,
                'prerequisite_concepts': [2, 7],  # Data Types, For loops
                'tags': ['beginner', 'data_structures']
            },
            {
                'name': 'List Comprehensions',
                'category': 'data_structures',
                'description': 'Concise list creation and filtering',
                'difficulty_level': 5,
                'prerequisite_concepts': [16],  # Lists
                'tags': ['intermediate', 'data_structures']
            },
            {
                'name': 'Dictionaries',
                'category': 'data_structures',
                'description': 'Key-value pairs and hash maps',
                'difficulty_level': 4,
                'prerequisite_concepts': [16],  # Lists
                'tags': ['intermediate', 'data_structures']
            },
            {
                'name': 'Sets',
                'category': 'data_structures',
                'description': 'Unique collections and set operations',
                'difficulty_level': 4,
                'prerequisite_concepts': [16],  # Lists
                'tags': ['intermediate', 'data_structures']
            },
            {
                'name': 'Tuples',
                'category': 'data_structures',
                'description': 'Immutable sequences',
                'difficulty_level': 3,
                'prerequisite_concepts': [16],  # Lists
                'tags': ['beginner', 'data_structures']
            },
            {
                'name': 'Stack Behavior',
                'category': 'data_structures',
                'description': 'LIFO data structure and call stack',
                'difficulty_level': 6,
                'prerequisite_concepts': [16, 13],  # Lists, Recursion
                'tags': ['intermediate', 'data_structures', 'theory']
            },
            {
                'name': 'Queue Operations',
                'category': 'data_structures',
                'description': 'FIFO data structure',
                'difficulty_level': 5,
                'prerequisite_concepts': [16],  # Lists
                'tags': ['intermediate', 'data_structures']
            },
            
            # Complexity & Performance (23-26)
            {
                'name': 'Time Complexity',
                'category': 'complexity',
                'description': 'Big O notation and runtime analysis',
                'difficulty_level': 7,
                'prerequisite_concepts': [7, 9],  # For loops, Nested loops
                'tags': ['intermediate', 'complexity', 'performance']
            },
            {
                'name': 'Space Complexity',
                'category': 'complexity',
                'description': 'Memory usage analysis',
                'difficulty_level': 7,
                'prerequisite_concepts': [23],  # Time Complexity
                'tags': ['intermediate', 'complexity', 'performance']
            },
            {
                'name': 'Algorithm Optimization',
                'category': 'complexity',
                'description': 'Improving algorithm efficiency',
                'difficulty_level': 8,
                'prerequisite_concepts': [23, 24],  # Time/Space Complexity
                'tags': ['advanced', 'optimization']
            },
            {
                'name': 'Performance Profiling',
                'category': 'complexity',
                'description': 'Measuring and analyzing code performance',
                'difficulty_level': 8,
                'prerequisite_concepts': [25],  # Optimization
                'tags': ['advanced', 'performance']
            },
            
            # Error Handling & Debugging (27-30)
            {
                'name': 'Edge Case Handling',
                'category': 'debugging',
                'description': 'Identifying and handling edge cases',
                'difficulty_level': 5,
                'prerequisite_concepts': [4],  # Conditionals
                'tags': ['intermediate', 'debugging', 'quality']
            },
            {
                'name': 'Debugging Strategy',
                'category': 'debugging',
                'description': 'Systematic debugging approaches',
                'difficulty_level': 6,
                'prerequisite_concepts': [27],  # Edge cases
                'tags': ['intermediate', 'debugging']
            },
            {
                'name': 'Error Types',
                'category': 'debugging',
                'description': 'Syntax, logic, and runtime errors',
                'difficulty_level': 4,
                'prerequisite_concepts': [1],  # Variables
                'tags': ['beginner', 'debugging']
            },
            {
                'name': 'Exception Handling',
                'category': 'debugging',
                'description': 'Try-catch blocks and error recovery',
                'difficulty_level': 6,
                'prerequisite_concepts': [29],  # Error Types
                'tags': ['intermediate', 'debugging']
            },
            
            # Code Quality (31-35)
            {
                'name': 'Code Readability',
                'category': 'quality',
                'description': 'Writing clear, understandable code',
                'difficulty_level': 4,
                'prerequisite_concepts': [1, 11],  # Variables, Functions
                'tags': ['intermediate', 'quality']
            },
            {
                'name': 'Naming Conventions',
                'category': 'quality',
                'description': 'Meaningful variable and function names',
                'difficulty_level': 3,
                'prerequisite_concepts': [1],  # Variables
                'tags': ['beginner', 'quality']
            },
            {
                'name': 'Code Organization',
                'category': 'quality',
                'description': 'Structuring code logically',
                'difficulty_level': 5,
                'prerequisite_concepts': [11, 31],  # Functions, Readability
                'tags': ['intermediate', 'quality']
            },
            {
                'name': 'Refactoring Discipline',
                'category': 'quality',
                'description': 'Improving code without changing behavior',
                'difficulty_level': 7,
                'prerequisite_concepts': [31, 33],  # Readability, Organization
                'tags': ['advanced', 'quality', 'refactoring']
            },
            {
                'name': 'DRY Principle',
                'category': 'quality',
                'description': "Don't Repeat Yourself - code reusability",
                'difficulty_level': 6,
                'prerequisite_concepts': [11, 33],  # Functions, Organization
                'tags': ['intermediate', 'quality', 'principles']
            }
        ]
        
        # Clear existing concepts (for development)
        Concept.query.delete()
        db.session.commit()
        
        created_concepts = []
        for concept_data in concepts:
            concept = Concept(**concept_data)
            db.session.add(concept)
            created_concepts.append(concept)
        
        db.session.commit()
        
        print(f"✅ Successfully seeded {len(created_concepts)} concepts")
        
        # Print summary by category
        from collections import Counter
        categories = Counter([c.category for c in created_concepts])
        print("\n📊 Concepts by category:")
        for category, count in categories.items():
            print(f"  - {category}: {count} concepts")
        
        print("\n🎯 Concept hierarchy established with prerequisites")
        print("Ready for cognitive modeling!")

if __name__ == '__main__':
    seed_concepts()
