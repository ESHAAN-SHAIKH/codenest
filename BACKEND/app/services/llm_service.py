"""
Enhanced LLM Integration Service for Code Nest
Handles communication with Together API for code explanations and hints
Now supports both Python and Java
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered code explanations and educational content"""

    def __init__(self):
        self.api_key = os.environ.get('TOGETHER_API_KEY')
        self.base_url = 'https://api.together.xyz/v1'
        self.model = 'mistralai/Mixtral-8x7B-Instruct-v0.1'

        # Rate limiting
        self._request_history = []
        self.max_requests_per_minute = 30

        if not self.api_key:
            logger.warning("TOGETHER_API_KEY not found. LLM features will be disabled.")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)

        # Remove old requests
        self._request_history = [
            req_time for req_time in self._request_history
            if req_time > minute_ago
        ]

        return len(self._request_history) < self.max_requests_per_minute

    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = 500) -> Optional[Dict[str, Any]]:
        """Make a request to the Together API"""
        if not self.api_key:
            return None

        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded for LLM requests")
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': 0.3,
            'stop': ['</s>']
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            # Track request time
            self._request_history.append(datetime.utcnow())

            result = response.json()
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM API response: {str(e)}")
            return None

    def explain_code(self, code: str, context: str = 'general', question: str = 'Explain this code',
                     user_level: str = 'beginner', language: str = 'python') -> Dict[str, Any]:
        """
        Get an explanation for the provided code

        Args:
            code: Code to explain (Python or Java)
            context: Context (lesson, challenge, or general)
            question: Specific question about the code
            user_level: User's experience level (beginner, intermediate, advanced)
            language: Programming language ('python' or 'java')

        Returns:
            Dictionary with explanation and suggestions
        """
        # Enhanced fallback responses for both languages
        fallback_responses = {
            'python': {
                'beginner': {
                    'content': "This Python code uses blocks to create a program. Each block represents a Python command that tells the computer what to do. Try running the code to see what happens!",
                    'suggestions': [
                        "Experiment with different values in your blocks",
                        "Try adding more blocks to see what they do",
                        "Use the print block to display messages"
                    ],
                    'difficulty': 'beginner'
                },
                'intermediate': {
                    'content': "This Python code demonstrates programming concepts using Pythonic syntax. The blocks you've connected translate into Python commands that execute in sequence. Consider the logic flow and data types involved.",
                    'suggestions': [
                        "Think about the order of operations",
                        "Consider what data types you're working with",
                        "Try using list comprehensions or lambda functions"
                    ],
                    'difficulty': 'intermediate'
                },
                'advanced': {
                    'content': "This Python code implements algorithmic logic using Python constructs. Analyze the computational complexity and consider optimization opportunities with Python's built-in functions.",
                    'suggestions': [
                        "Consider using generators for memory efficiency",
                        "Think about edge cases and error handling",
                        "Evaluate performance with timeit module"
                    ],
                    'difficulty': 'advanced'
                }
            },
            'java': {
                'beginner': {
                    'content': "This Java code uses object-oriented programming concepts. Each block represents a Java statement that follows strict syntax rules. Java is strongly typed, so you need to declare variable types!",
                    'suggestions': [
                        "Remember to end statements with semicolons",
                        "Declare variable types (int, String, boolean)",
                        "Use System.out.println() to display output"
                    ],
                    'difficulty': 'beginner'
                },
                'intermediate': {
                    'content': "This Java code demonstrates object-oriented programming principles. Java's strong typing and class-based structure provide clear organization and error prevention at compile time.",
                    'suggestions': [
                        "Consider using appropriate data structures (ArrayList, HashMap)",
                        "Think about method overloading and inheritance",
                        "Use proper exception handling with try-catch blocks"
                    ],
                    'difficulty': 'intermediate'
                },
                'advanced': {
                    'content': "This Java code implements advanced programming concepts with Java's robust type system and OOP features. Consider design patterns, generics, and performance optimizations.",
                    'suggestions': [
                        "Consider using design patterns (Singleton, Factory, Observer)",
                        "Implement generics for type safety",
                        "Optimize with Java 8+ features (Streams, Lambda expressions)"
                    ],
                    'difficulty': 'advanced'
                }
            }
        }

        # Get language-specific fallback
        lang_fallback = fallback_responses.get(language, fallback_responses['python'])
        fallback_response = lang_fallback.get(user_level, lang_fallback['beginner'])

        if not self.api_key:
            return fallback_response

        # Prepare the prompt based on user level, context, and language
        system_prompt = self._get_system_prompt(user_level, context, language)
        user_prompt = self._format_user_prompt(code, question, context, language)

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self._make_request(messages, max_tokens=600)

        if not result or 'choices' not in result or not result['choices']:
            logger.warning("LLM request failed, using fallback response")
            return fallback_response

        try:
            response_content = result['choices'][0]['message']['content']
            return self._parse_explanation_response(response_content, user_level, language)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return fallback_response

    def _get_system_prompt(self, user_level: str, context: str, language: str) -> str:
        """Get system prompt based on user level, context, and language"""
        base_prompt = f"""You are Code Cat, a friendly coding tutor for kids learning {language.title()} through visual block programming. Your responses should be encouraging, educational, and age-appropriate."""

        level_prompts = {
            'beginner': f"""
            The user is just starting to learn {language.title()} programming. Use simple language, avoid jargon, and focus on basic concepts. Be very encouraging and patient. Explain things step by step. For Java, emphasize the importance of semicolons, braces, and data types. For Python, focus on indentation and simplicity.
            """,
            'intermediate': f"""
            The user has some {language.title()} programming experience. You can use more technical terms but still explain them clearly. For Java, discuss OOP concepts, classes, and methods. For Python, cover list comprehensions, modules, and Pythonic idioms. Focus on best practices and deeper understanding.
            """,
            'advanced': f"""
            The user is experienced with {language.title()} programming. For Java, you can discuss design patterns, generics, and advanced OOP concepts. For Python, cover decorators, generators, and advanced features. Challenge them to think critically about algorithms and optimization.
            """
        }

        context_prompts = {
            'lesson': f"This is part of a structured {language.title()} lesson. Focus on the specific learning objectives and provide clear, educational explanations.",
            'challenge': f"This is from a {language.title()} coding challenge. Provide hints and guidance without giving away the complete solution.",
            'general': f"This is a general question about {language.title()} code. Provide comprehensive explanations and suggestions for improvement."
        }

        language_specifics = {
            'python': "Remember that Python values readability and simplicity. Emphasize clean, Pythonic code.",
            'java': "Remember that Java is strongly typed and object-oriented. Emphasize proper syntax, type safety, and OOP principles."
        }

        return f"{base_prompt}\n{level_prompts.get(user_level, level_prompts['beginner'])}\n{context_prompts.get(context, context_prompts['general'])}\n{language_specifics.get(language, language_specifics['python'])}"

    def _format_user_prompt(self, code: str, question: str, context: str, language: str) -> str:
        """Format the user prompt with code and question"""
        language_examples = {
            'python': """
Example Python concepts to consider:
- Variables and data types (int, str, list, dict)
- Control structures (if/else, for/while loops)
- Functions and modules
- List comprehensions and generators
""",
            'java': """
Example Java concepts to consider:
- Data types (int, String, boolean, arrays)
- Classes and objects
- Methods and constructors
- Control structures (if/else, for/while loops)
- Exception handling
"""
        }

        prompt = f"""Here's some {language.title()} code created with visual blocks:

```{language}
{code}
```

Question: {question}

{language_examples.get(language, language_examples['python'])}

Please provide:
1. A clear explanation of what this code does
2. 2-3 helpful suggestions or tips specific to {language.title()}
3. The difficulty level (beginner/intermediate/advanced)

Format your response as a JSON object with keys: "content", "suggestions" (array), and "difficulty".
"""
        return prompt

    def _parse_explanation_response(self, response: str, user_level: str, language: str) -> Dict[str, Any]:
        """Parse the LLM response into structured format"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                parsed_response = json.loads(json_str)

                return {
                    'content': parsed_response.get('content', f'I can help explain this {language.title()} code!'),
                    'suggestions': parsed_response.get('suggestions', []),
                    'difficulty': parsed_response.get('difficulty', user_level),
                    'language': language
                }
            else:
                # If no JSON found, treat entire response as content
                default_suggestions = {
                    'python': ['Try running the code to see what happens!', 'Experiment with different values'],
                    'java': ['Compile and run to see the output!', 'Try changing variable values']
                }
                return {
                    'content': response.strip(),
                    'suggestions': default_suggestions.get(language, default_suggestions['python']),
                    'difficulty': user_level,
                    'language': language
                }

        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            language_suggestions = {
                'python': ['Keep experimenting with Python!', 'Try modifying the code'],
                'java': ['Keep practicing Java syntax!', 'Try different approaches']
            }
            return {
                'content': response.strip(),
                'suggestions': language_suggestions.get(language, language_suggestions['python']),
                'difficulty': user_level,
                'language': language
            }

    def generate_hint(self, lesson_id: int, user_code: str, expected_output: str, language: str = 'python') -> Dict[str, Any]:
        """
        Generate a helpful hint for a struggling user

        Args:
            lesson_id: ID of the current lesson
            user_code: User's current code attempt
            expected_output: What the code should output
            language: Programming language

        Returns:
            Dictionary with hint and encouragement
        """
        fallback_hints = {
            'python': {
                1: "Try using a print block and typing 'Hello World!' inside it.",
                2: "Use a math block to add 5 + 3, then connect it to a print block.",
                3: "Use a repeat block set to 3 times, and put a print block inside it.",
                4: "Try using an if block from the Logic section."
            },
            'java': {
                1: "Use System.out.println() and put 'Hello World!' in quotes inside the parentheses.",
                2: "Declare an int variable, assign it the sum of 10 + 5, then print it.",
                3: "Use a for loop to repeat printing numbers from 1 to 3.",
                4: "Use an if statement to check a condition and print different messages."
            }
        }

        language_hints = fallback_hints.get(language, fallback_hints['python'])

        if not self.api_key:
            return {
                'hint': language_hints.get(lesson_id, f"Keep trying with {language.title()}! You're doing great!"),
                'encouragement': f"Don't give up! Every {language.title()} programmer makes mistakes while learning. Try again!",
                'language': language
            }

        system_prompt = f"""You are Code Cat, a helpful {language.title()} coding tutor. The user is stuck on a lesson. Provide a gentle hint without giving away the complete solution. Be encouraging and supportive."""

        user_prompt = f"""
        The user is working on lesson {lesson_id} in {language.title()} and is having trouble.

        Their current code:
        ```{language}
        {user_code or 'No code yet'}
        ```

        Expected output:
        ```
        {expected_output}
        ```

        Please provide:
        1. A helpful hint that guides them toward the solution without giving it away
        2. Some encouraging words

        Format as JSON with keys "hint" and "encouragement".
        """

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self._make_request(messages, max_tokens=300)

        if not result or 'choices' not in result:
            return {
                'hint': language_hints.get(lesson_id, f"Keep trying! Look at the {language.title()} blocks available and think about what you need to do."),
                'encouragement': f"You're doing great with {language.title()}! Programming takes practice. Keep going!",
                'language': language
            }

        try:
            response = result['choices'][0]['message']['content']
            return self._parse_hint_response(response, lesson_id, language)
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing hint response: {str(e)}")
            return {
                'hint': language_hints.get(lesson_id, "Try breaking the problem into smaller steps."),
                'encouragement': f"Every expert {language.title()} programmer was once a beginner. Keep practicing!",
                'language': language
            }

    def _parse_hint_response(self, response: str, lesson_id: int, language: str) -> Dict[str, Any]:
        """Parse hint response from LLM"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                parsed = json.loads(json_str)

                return {
                    'hint': parsed.get('hint', f'Try thinking about what {language.title()} blocks you need.'),
                    'encouragement': parsed.get('encouragement', f'You can do this {language.title()} challenge! Keep trying!'),
                    'language': language
                }
            else:
                return {
                    'hint': response.strip(),
                    'encouragement': f'Great effort with {language.title()}! Keep going!',
                    'language': language
                }
        except json.JSONDecodeError:
            return {
                'hint': response.strip() if response.strip() else f'Think about what the {language.title()} problem is asking you to do.',
                'encouragement': f'Learning {language.title()} is a journey. Enjoy the process!',
                'language': language
            }

    def generate_challenge_feedback(self, user_code: str, expected_output: str, actual_output: str, language: str = 'python') -> Dict[str, Any]:
        """
        Generate feedback for challenge submissions

        Args:
            user_code: User's submitted code
            expected_output: Expected output
            actual_output: What the code actually produced
            language: Programming language

        Returns:
            Dictionary with feedback and suggestions
        """
        language_feedback = {
            'python': {
                'correct': 'Excellent Python work! Your solution is correct!',
                'incorrect': 'Not quite right, but keep trying with Python! Compare your output with the expected result.',
                'suggestions': ['Check your Python logic step by step', 'Make sure your output format matches exactly', 'Try using Python debugging techniques']
            },
            'java': {
                'correct': 'Excellent Java work! Your solution is correct!',
                'incorrect': 'Not quite right, but keep trying with Java! Compare your output with the expected result.',
                'suggestions': ['Check your Java logic step by step', 'Make sure your output format matches exactly', 'Verify your data types and method calls']
            }
        }

        lang_feedback = language_feedback.get(language, language_feedback['python'])

        if not self.api_key:
            if actual_output.strip() == expected_output.strip():
                return {
                    'feedback': lang_feedback['correct'],
                    'suggestions': ['Try optimizing your solution', 'Consider edge cases'],
                    'score': 100,
                    'language': language
                }
            else:
                return {
                    'feedback': lang_feedback['incorrect'],
                    'suggestions': lang_feedback['suggestions'][:2],
                    'score': 50,
                    'language': language
                }

        system_prompt = f"""You are Code Cat, providing feedback on a {language.title()} coding challenge submission. Be constructive and encouraging while pointing out what needs improvement."""

        user_prompt = f"""
        User's {language.title()} code:
        ```{language}
        {user_code}
        ```

        Expected output:
        ```
        {expected_output}
        ```

        Actual output:
        ```
        {actual_output}
        ```

        Please provide:
        1. Constructive feedback on the {language.title()} submission
        2. 2-3 specific suggestions for improvement
        3. A score out of 100

        Format as JSON with keys "feedback", "suggestions" (array), and "score".
        """

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self._make_request(messages, max_tokens=400)

        if not result or 'choices' not in result:
            # Fallback scoring
            if actual_output.strip() == expected_output.strip():
                score = 100
                feedback = f"Perfect! Your {language.title()} solution works correctly!"
            else:
                score = 25
                feedback = f"Good attempt with {language.title()}! Check the output format and try again."

            return {
                'feedback': feedback,
                'suggestions': [f'Review the {language.title()} problem requirements', 'Test with different inputs'],
                'score': score,
                'language': language
            }

        try:
            response = result['choices'][0]['message']['content']
            return self._parse_feedback_response(response, actual_output == expected_output, language)
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing feedback response: {str(e)}")
            return {
                'feedback': f'Good effort with {language.title()}! Keep working on it!',
                'suggestions': ['Break the problem into smaller parts', f'Check your {language.title()} logic carefully'],
                'score': 50,
                'language': language
            }

    def _parse_feedback_response(self, response: str, is_correct: bool, language: str) -> Dict[str, Any]:
        """Parse feedback response from LLM"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                parsed = json.loads(json_str)

                return {
                    'feedback': parsed.get('feedback', f'Good work with {language.title()}!'),
                    'suggestions': parsed.get('suggestions', []),
                    'score': min(max(parsed.get('score', 50), 0), 100),  # Clamp between 0-100
                    'language': language
                }
            else:
                return {
                    'feedback': response.strip(),
                    'suggestions': [f'Keep practicing {language.title()}!'],
                    'score': 90 if is_correct else 40,
                    'language': language
                }
        except (json.JSONDecodeError, ValueError):
            return {
                'feedback': response.strip() if response.strip() else f'Nice try with {language.title()}!',
                'suggestions': ['Review the requirements', 'Try a different approach'],
                'score': 80 if is_correct else 30,
                'language': language
            }

    def get_concept_explanation(self, concept: str, user_level: str = 'beginner', language: str = 'python') -> Dict[str, Any]:
        """
        Get explanation for a programming concept in specified language

        Args:
            concept: Programming concept to explain (e.g., 'loops', 'variables')
            user_level: User's experience level
            language: Programming language

        Returns:
            Dictionary with concept explanation and examples
        """
        concept_explanations = {
            'python': {
                'loops': {
                    'beginner': {
                        'explanation': 'Loops in Python help you repeat actions! Instead of writing the same code many times, you can use a loop to do it automatically.',
                        'examples': ['for i in range(5): print("Hello")', 'while count < 10: count += 1'],
                        'tips': ['Start with simple for loops', 'Remember Python uses indentation']
                    }
                },
                'variables': {
                    'beginner': {
                        'explanation': 'Variables in Python are like boxes that store information. Python automatically figures out the type!',
                        'examples': ['name = "Alice"', 'age = 25', 'scores = [85, 92, 78]'],
                        'tips': ['Choose meaningful names', 'Python variables are dynamically typed']
                    }
                },
                'functions': {
                    'beginner': {
                        'explanation': 'Functions in Python are like recipes! They contain instructions you can use over and over.',
                        'examples': ['def greet(name): return f"Hello {name}"', 'def add(a, b): return a + b'],
                        'tips': ['Use def to define functions', 'Remember to return values when needed']
                    }
                }
            },
            'java': {
                'loops': {
                    'beginner': {
                        'explanation': 'Loops in Java help you repeat actions! Java has for loops, while loops, and enhanced for loops.',
                        'examples': ['for(int i=0; i<5; i++) { System.out.println("Hello"); }', 'while(count < 10) { count++; }'],
                        'tips': ['Remember semicolons in for loops', 'Use curly braces for loop bodies']
                    }
                },
                'variables': {
                    'beginner': {
                        'explanation': 'Variables in Java must have declared types! Java is strongly typed for safety.',
                        'examples': ['String name = "Alice";', 'int age = 25;', 'boolean isStudent = true;'],
                        'tips': ['Declare the type first', 'Use camelCase naming convention']
                    }
                },
                'functions': {
                    'beginner': {
                        'explanation': 'Methods in Java are functions inside classes! They define what objects can do.',
                        'examples': ['public static void main(String[] args)', 'public int add(int a, int b) { return a + b; }'],
                        'tips': ['Methods need access modifiers (public, private)', 'Static methods belong to the class, not objects']
                    }
                }
            }
        }

        lang_concepts = concept_explanations.get(language, concept_explanations['python'])
        fallback = lang_concepts.get(concept, {}).get(user_level)

        if fallback:
            fallback['language'] = language
            return fallback

        if not self.api_key:
            return {
                'explanation': f'{concept.title()} is an important {language.title()} concept that helps you write better code!',
                'examples': [f'Try experimenting with {language.title()} {concept}', 'Practice makes perfect'],
                'tips': ['Take your time to understand', 'Ask for help when needed'],
                'language': language
            }

        system_prompt = f"""You are Code Cat, explaining {language.title()} programming concepts to a {user_level} programmer. Use age-appropriate language and provide clear examples."""

        user_prompt = f"""
        Explain the {language.title()} programming concept: {concept}

        Please provide:
        1. A clear explanation suitable for a {user_level} learning {language.title()}
        2. 2-3 practical {language.title()} code examples
        3. 2-3 helpful tips specific to {language.title()}

        Format as JSON with keys "explanation", "examples" (array), and "tips" (array).
        """

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self._make_request(messages, max_tokens=500)

        if not result or 'choices' not in result:
            return fallback or {
                'explanation': f'{concept.title()} is a fundamental {language.title()} programming concept.',
                'examples': [f'Practice with simple {language.title()} examples', 'Build up complexity gradually'],
                'tips': ['Take it step by step', 'Practice regularly'],
                'language': language
            }

        try:
            response = result['choices'][0]['message']['content']
            return self._parse_concept_response(response, concept, language)
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing concept response: {str(e)}")
            return fallback or {
                'explanation': f'Learning about {concept} in {language.title()} will help you become a better programmer!',
                'examples': ['Start with basics', 'Practice with real examples'],
                'tips': ['Be patient with yourself', 'Keep practicing'],
                'language': language
            }

    def _parse_concept_response(self, response: str, concept: str, language: str) -> Dict[str, Any]:
        """Parse concept explanation response"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                parsed = json.loads(json_str)

                return {
                    'explanation': parsed.get('explanation', f'{concept} is an important {language.title()} programming concept.'),
                    'examples': parsed.get('examples', []),
                    'tips': parsed.get('tips', []),
                    'language': language
                }
            else:
                return {
                    'explanation': response.strip(),
                    'examples': [f'Try it in your {language.title()} code!'],
                    'tips': ['Practice makes perfect!'],
                    'language': language
                }
        except json.JSONDecodeError:
            return {
                'explanation': response.strip() if response.strip() else f'Learning {concept} in {language.title()} takes practice!',
                'examples': ['Experiment with examples'],
                'tips': ['Keep trying', 'Ask questions'],
                'language': language
            }