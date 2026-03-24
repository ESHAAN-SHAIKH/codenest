"""
Enhanced Secure code execution sandbox for Code Nest - Python and Java support
"""

import ast
import sys
import time
import traceback
import threading
import subprocess
import tempfile
import os
import shutil
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional
import re

class TimeoutException(Exception):
    """Exception raised when code execution times out"""
    pass

class SecurityException(Exception):
    """Exception raised when potentially dangerous code is detected"""
    pass

class JavaSandbox:
    """Secure Java code execution environment"""

    def __init__(self, timeout: int = 15, max_memory_mb: int = 100):
        self.timeout = timeout
        self.max_memory = max_memory_mb

        # Check if Java is available
        self.java_available = self._check_java_availability()

        # Forbidden patterns for Java security
        self.forbidden_java_patterns = [
            r'import\s+java\.io\.File',
            r'import\s+java\.nio\.file',
            r'import\s+java\.net',
            r'import\s+java\.lang\.Runtime',
            r'import\s+java\.lang\.ProcessBuilder',
            r'import\s+javax\.swing',
            r'import\s+java\.awt',
            r'System\.exit',
            r'Runtime\.getRuntime',
            r'ProcessBuilder',
            r'FileInputStream',
            r'FileOutputStream',
            r'Socket',
            r'ServerSocket',
            r'Thread\.sleep\s*\(\s*[0-9]{4,}', # Prevent long sleeps
        ]

    def _check_java_availability(self) -> bool:
        """Check if Java compiler and runtime are available"""
        try:
            # Check javac
            subprocess.run(['javac', '-version'], capture_output=True, check=True, timeout=5)
            # Check java
            subprocess.run(['java', '-version'], capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _validate_java_code(self, code: str) -> None:
        """Validate Java code for security issues"""
        # Check for forbidden patterns
        for pattern in self.forbidden_java_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityException(f"Forbidden pattern detected: {pattern}")

        # Check for infinite loops (basic heuristic)
        if re.search(r'while\s*\(\s*true\s*\)', code):
            raise SecurityException("Infinite while loops are not allowed")

        # Limit nested loops depth
        loop_depth = len(re.findall(r'\b(for|while)\b', code))
        if loop_depth > 5:
            raise SecurityException("Too many nested loops detected")

    def execute_java_code(self, code: str) -> Dict[str, Any]:
        """Execute Java code safely and return result"""
        start_time = time.time()

        if not self.java_available:
            return {
                'success': False,
                'error': 'Java compiler/runtime not available on this system',
                'output': '',
                'execution_time': 0
            }

        if not code or not code.strip():
            return {
                'success': True,
                'output': '',
                'execution_time': 0,
                'message': 'No code to execute'
            }

        try:
            self._validate_java_code(code)
        except SecurityException as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }

        # Create temporary directory for Java files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                return self._compile_and_run_java(code, temp_dir, start_time)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Java execution error: {str(e)}',
                    'output': '',
                    'execution_time': time.time() - start_time
                }

    def _compile_and_run_java(self, code: str, temp_dir: str, start_time: float) -> Dict[str, Any]:
        """Compile and run Java code in temporary directory"""

        # Extract class name or use default
        class_match = re.search(r'public\s+class\s+(\w+)', code)
        class_name = class_match.group(1) if class_match else 'Main'

        # If no public class found, wrap code in Main class
        if not class_match:
            wrapped_code = f"""
public class Main {{
    public static void main(String[] args) {{
        {code}
    }}
}}
"""
        else:
            # Ensure main method exists
            if 'public static void main' not in code:
                # Try to add main method to existing class
                class_body_match = re.search(r'public\s+class\s+\w+\s*\{(.*)\}', code, re.DOTALL)
                if class_body_match:
                    class_body = class_body_match.group(1).strip()
                    wrapped_code = code.replace(
                        class_body_match.group(0),
                        f"""public class {class_name} {{
    public static void main(String[] args) {{
        {class_body}
    }}
}}"""
                    )
                else:
                    wrapped_code = code
            else:
                wrapped_code = code

        java_file = os.path.join(temp_dir, f'{class_name}.java')
        class_file = os.path.join(temp_dir, f'{class_name}.class')

        # Write Java source file
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(wrapped_code)

        try:
            # Compile Java code
            compile_result = subprocess.run([
                'javac', java_file
            ], capture_output=True, text=True, timeout=self.timeout, cwd=temp_dir)

            if compile_result.returncode != 0:
                error_msg = compile_result.stderr.strip()
                # Make error messages more user-friendly
                if 'cannot find symbol' in error_msg:
                    error_msg = "Variable or method not found. Check your spelling and make sure everything is defined."
                elif 'expected' in error_msg:
                    error_msg = "Syntax error. Check your brackets, semicolons, and code structure."
                elif 'illegal start of expression' in error_msg:
                    error_msg = "Code structure error. Make sure your code is properly formatted."

                return {
                    'success': False,
                    'error': f'Compilation error: {error_msg}',
                    'output': '',
                    'execution_time': time.time() - start_time
                }

            # Run Java code with memory and time limits
            run_result = subprocess.run([
                'java',
                f'-Xmx{self.max_memory}m',  # Set max heap size
                '-Xms16m',  # Set initial heap size
                class_name
            ], capture_output=True, text=True, timeout=self.timeout, cwd=temp_dir)

            execution_time = time.time() - start_time

            if run_result.returncode != 0:
                error_output = run_result.stderr.strip()

                # Make runtime errors more user-friendly
                if 'OutOfMemoryError' in error_output:
                    error_msg = f"Program used too much memory (over {self.max_memory}MB). Try using smaller data structures."
                elif 'StackOverflowError' in error_output:
                    error_msg = "Stack overflow - this usually means infinite recursion. Check your loops and method calls."
                elif 'ArrayIndexOutOfBoundsException' in error_output:
                    error_msg = "Array index error. Make sure you're not accessing array elements outside the valid range."
                elif 'NullPointerException' in error_output:
                    error_msg = "Null pointer error. Make sure to initialize your objects before using them."
                elif 'NumberFormatException' in error_output:
                    error_msg = "Number format error. Check that you're using valid numbers."
                else:
                    error_msg = error_output

                return {
                    'success': False,
                    'error': error_msg,
                    'output': run_result.stdout,
                    'execution_time': execution_time
                }

            output = run_result.stdout

            # Check output size
            if len(output) > 10000:
                output = output[:10000] + "\n... (output truncated)"

            return {
                'success': True,
                'output': output,
                'execution_time': execution_time,
                'memory_usage': 0  # Java memory tracking would require JMX
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Code took too long to run (over {self.timeout} seconds). Try simplifying your code or reducing loop iterations.",
                'output': '',
                'execution_time': time.time() - start_time
            }

class PythonSandbox:
    """Secure Python code execution environment optimized for Windows"""

    def __init__(self, timeout: int = 10, max_memory_mb: int = 50):
        self.timeout = timeout
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes

        # Allowed built-in functions
        self.allowed_builtins = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance', 'issubclass',
            'iter', 'len', 'list', 'locals', 'map', 'max', 'min', 'next',
            'object', 'oct', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
            'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars',
            'zip', '__import__', 'help'
        }

        # Forbidden patterns
        self.forbidden_patterns = [
            r'__.*__',  # Dunder methods/attributes
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'from\s+os',
            r'from\s+sys',
            r'from\s+subprocess',
            r'exec\s*\(',
            r'eval\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
        ]

        # Allowed modules
        self.allowed_modules = {
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            'string': __import__('string'),
            're': __import__('re'),
            'itertools': __import__('itertools'),
            'collections': __import__('collections'),
            'functools': __import__('functools'),
            'operator': __import__('operator')
        }

    def _validate_code(self, code: str) -> None:
        """Validate code for security issues"""
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                raise SecurityException(f"Forbidden pattern detected: {pattern}")

        # Parse AST to check for dangerous operations
        try:
            tree = ast.parse(code)
            self._validate_ast(tree)
        except SyntaxError as e:
            raise SecurityException(f"Syntax error in code: {str(e)}")

    def _validate_ast(self, node: ast.AST) -> None:
        """Validate AST nodes for dangerous operations"""
        for child in ast.walk(node):
            # Check for dangerous function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in {'exec', 'eval', 'compile', '__import__', 'open', 'file', 'input'}:
                        raise SecurityException(f"Forbidden function call: {child.func.id}")

                # Check for attribute access on dangerous objects
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        if child.func.value.id in {'os', 'sys', 'subprocess'}:
                            raise SecurityException(f"Forbidden module access: {child.func.value.id}")

            # Check for dangerous imports
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                if isinstance(child, ast.Import):
                    for alias in child.names:
                        if alias.name not in self.allowed_modules:
                            raise SecurityException(f"Forbidden import: {alias.name}")
                elif isinstance(child, ast.ImportFrom):
                    if child.module and child.module not in self.allowed_modules:
                        raise SecurityException(f"Forbidden import from: {child.module}")

            # Check for dangerous attribute access
            elif isinstance(child, ast.Attribute):
                if child.attr.startswith('_'):
                    raise SecurityException(f"Private attribute access not allowed: {child.attr}")

    def _create_safe_builtins(self) -> Dict[str, Any]:
        """Create a safe builtins dictionary"""
        safe_builtins = {}

        # Get the actual builtins module
        import builtins

        # Add allowed built-in functions
        for name in self.allowed_builtins:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)

        # Add safe print function that captures output
        def safe_print(*args, **kwargs):
            # Remove file parameter to prevent file writing
            kwargs.pop('file', None)
            print(*args, **kwargs)

        safe_builtins['print'] = safe_print

        return safe_builtins

    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a safe globals dictionary"""
        safe_globals = {
            '__builtins__': self._create_safe_builtins(),
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None,
        }

        # Add allowed modules
        safe_globals.update(self.allowed_modules)

        return safe_globals

    def _execute_with_timeout(self, code: str, safe_globals: dict, safe_locals: dict, timeout: int):
        """Execute code with timeout using threading (Windows compatible)"""
        result = {'success': True, 'error': None, 'completed': False}

        def target():
            try:
                exec(code, safe_globals, safe_locals)
                result['completed'] = True
            except Exception as e:
                result['success'] = False
                result['error'] = e
                result['completed'] = True

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)

        if not result['completed']:
            # Thread is still running, it timed out
            result['success'] = False
            result['error'] = TimeoutException(f"Code took too long to run (over {timeout} seconds). Try simplifying your code or reducing loop iterations.")

        return result

    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely and return result

        Args:
            code: Python code to execute

        Returns:
            Dictionary containing execution result
        """
        start_time = time.time()

        # Basic input validation
        if not code or not code.strip():
            return {
                'success': True,
                'output': '',
                'execution_time': 0,
                'message': 'No code to execute'
            }

        # Validate code for security
        try:
            self._validate_code(code)
        except SecurityException as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0
            }

        # Prepare execution environment
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        try:
            # Execute code with captured output
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                safe_globals = self._create_safe_globals()
                safe_locals = {}

                # Use thread-based timeout for Windows compatibility
                result = self._execute_with_timeout(code, safe_globals, safe_locals, self.timeout)
                if not result['success']:
                    if isinstance(result['error'], TimeoutException):
                        raise result['error']
                    else:
                        raise result['error']

            # Get execution results
            output = stdout_capture.getvalue()
            error_output = stderr_capture.getvalue()

            execution_time = time.time() - start_time

            # Check output size
            if len(output) > 10000:  # 10KB limit
                output = output[:10000] + "\n... (output truncated)"

            if error_output:
                return {
                    'success': False,
                    'error': error_output.strip(),
                    'output': output,
                    'execution_time': execution_time
                }

            return {
                'success': True,
                'output': output,
                'execution_time': execution_time,
                'memory_usage': 0  # Memory tracking not available on Windows
            }

        except TimeoutException as e:
            return {
                'success': False,
                'error': str(e),
                'output': stdout_capture.getvalue(),
                'execution_time': time.time() - start_time
            }

        except MemoryError:
            return {
                'success': False,
                'error': f"Code used too much memory (over {self.max_memory // 1024 // 1024}MB). Try using smaller data structures.",
                'output': stdout_capture.getvalue(),
                'execution_time': time.time() - start_time
            }

        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__

            # Provide helpful error messages for beginners
            if error_type == 'NameError':
                error_msg = f"Variable not found: {error_msg}. Make sure you define variables before using them."
            elif error_type == 'SyntaxError':
                error_msg = f"Code structure error: {error_msg}. Check your blocks are connected properly."
            elif error_type == 'IndentationError':
                error_msg = f"Indentation error: {error_msg}. Make sure your blocks are properly nested."
            elif error_type == 'TypeError':
                error_msg = f"Type error: {error_msg}. Check that you're using the right types of data."
            elif "maximum recursion depth" in error_msg:
                error_msg = "Infinite loop or too much recursion detected. Check your loops and function calls."

            return {
                'success': False,
                'error': error_msg,
                'output': stdout_capture.getvalue(),
                'execution_time': time.time() - start_time
            }

    def validate_lesson_output(self, user_output: str, expected_output: str) -> Dict[str, Any]:
        """
        Validate if user output matches expected lesson output

        Args:
            user_output: Output from user's code
            expected_output: Expected output for the lesson

        Returns:
            Dictionary with validation result
        """
        user_output = user_output.strip()
        expected_output = expected_output.strip()

        # Exact match
        if user_output == expected_output:
            return {
                'passed': True,
                'score': 100,
                'feedback': 'Perfect! Your output matches exactly.',
                'stars': 3
            }

        # Fuzzy matching for slight differences
        user_lines = user_output.split('\n')
        expected_lines = expected_output.split('\n')

        if len(user_lines) != len(expected_lines):
            return {
                'passed': False,
                'score': 0,
                'feedback': f'Expected {len(expected_lines)} lines of output, got {len(user_lines)}.',
                'stars': 0
            }

        # Check line by line
        matching_lines = sum(1 for u, e in zip(user_lines, expected_lines) if u.strip() == e.strip())
        score = (matching_lines / len(expected_lines)) * 100

        if score >= 80:
            stars = 2 if score >= 90 else 1
            return {
                'passed': True,
                'score': score,
                'feedback': f'Good job! {matching_lines}/{len(expected_lines)} lines match.',
                'stars': stars
            }

        return {
            'passed': False,
            'score': score,
            'feedback': f'Only {matching_lines}/{len(expected_lines)} lines match. Check your output carefully.',
            'stars': 0
        }


class MultiLanguageSandbox:
    """Combined sandbox supporting both Python and Java"""

    def __init__(self, timeout: int = 15, max_memory_mb: int = 100):
        self.python_sandbox = PythonSandbox(timeout=min(timeout, 10), max_memory_mb=min(max_memory_mb, 50))
        self.java_sandbox = JavaSandbox(timeout=timeout, max_memory_mb=max_memory_mb)

    def execute_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Execute code in specified language

        Args:
            code: Code to execute
            language: Programming language ('python' or 'java')

        Returns:
            Dictionary containing execution result
        """
        if language.lower() == 'java':
            return self.java_sandbox.execute_java_code(code)
        else:
            return self.python_sandbox.execute_code(code)

    def validate_lesson_output(self, user_output: str, expected_output: str) -> Dict[str, Any]:
        """Validate lesson output (language agnostic)"""
        return self.python_sandbox.validate_lesson_output(user_output, expected_output)

    def get_supported_languages(self) -> Dict[str, bool]:
        """Get list of supported languages and their availability"""
        return {
            'python': True,
            'java': self.java_sandbox.java_available
        }


# For backwards compatibility, keep the original PythonSandbox as default
# but recommend using MultiLanguageSandbox for new implementations