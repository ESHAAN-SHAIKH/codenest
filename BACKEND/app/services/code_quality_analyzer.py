"""
Code Quality Analyzer Service
Analyzes code for quality metrics, complexity, and improvement suggestions
"""

import ast
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class CodeQualityAnalyzer:
    """Service for analyzing code quality and complexity"""
    
    @staticmethod
    def analyze_quality(code: str, language: str = 'python') -> Dict:
        """
        Comprehensive code quality analysis
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary with quality metrics
        """
        if language != 'python':
            return {'error': f'Quality analysis not supported for {language}'}
        
        metrics = {
            'quality_score': 0.0,
            'readability_score': 0.0,
            'complexity_score': 0,
            'issues': [],
            'strengths': [],
            'suggestions': []
        }
        
        # Readability checks
        readability = CodeQualityAnalyzer._check_readability(code)
        metrics['readability_score'] = readability['score']
        metrics['issues'].extend(readability['issues'])
        metrics['suggestions'].extend(readability['suggestions'])
        
        # Complexity analysis
        complexity = CodeQualityAnalyzer.detect_complexity(code)
        metrics['complexity_score'] = complexity['cyclomatic_complexity']
        metrics['time_complexity'] = complexity['time_complexity']
        metrics['space_complexity'] = complexity['space_complexity']
        
        # Naming conventions
        naming = CodeQualityAnalyzer._check_naming(code)
        metrics['issues'].extend(naming['issues'])
        if naming['good_names'] > 0:
            metrics['strengths'].append(f"Good naming conventions ({naming['good_names']} well-named identifiers)")
        
        # DRY principle
        duplication = CodeQualityAnalyzer._check_duplication(code)
        if duplication['score'] < 0.7:
            metrics['issues'].append("Code contains repetitive patterns (consider refactoring)")
            metrics['suggestions'].append("Extract repeated code into functions")
        
        # Calculate overall quality score
        quality_components = {
            'readability': readability['score'] * 0.4,
            'complexity': max(0, 1 - (complexity['cyclomatic_complexity'] /20)) * 0.3,
            'naming': naming['score'] * 0.2,
            'duplication': duplication['score'] * 0.1
        }
        
        metrics['quality_score'] = round(sum(quality_components.values()), 3)
        
        return metrics
    
    @staticmethod
    def _check_readability(code: str) -> Dict:
        """Check code readability factors"""
        score = 1.0
        issues = []
        suggestions = []
        
        lines = code.split('\n')
        
        # Check line length
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            score -= 0.1
            issues.append(f"Long lines detected (line {long_lines[0]})" + (f" and {len(long_lines)-1} more" if len(long_lines) > 1 else ""))
            suggestions.append("Keep lines under 80-100 characters for better readability")
        
        # Check for comments
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if comment_lines == 0 and len(lines) > 10:
            score -= 0.15
            issues.append("No comments found")
            suggestions.append("Add comments to explain complex logic")
        
        # Check for blank lines (good practice)
        blank_lines = sum(1 for line in lines if not line.strip())
        if len(lines) > 15 and blank_lines < 3:
            score -= 0.1
            issues.append("Dense code without blank lines")
            suggestions.append("Use blank lines to separate logical sections")
        
        # Check for consistent indentation
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if indents and len(set(i % 4 for i in indents if i > 0)) > 1:
            score -= 0.15
            issues.append("Inconsistent indentation")
        
        return {
            'score': round(max(0, score), 3),
            'issues': issues,
            'suggestions': suggestions
        }
    
    @staticmethod
    def _check_naming(code: str) -> Dict:
        """Check naming conventions"""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {'score': 0.5, 'issues': ['Cannot parse code'], 'good_names': 0}
        
        score = 1.0
        issues = []
        good_names = 0
        
        # Check function names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name
                if not re.match(r'^[a-z_][a-z0-9_]*$', name):
                    score -= 0.1
                    issues.append(f"Function '{name}' doesn't follow snake_case convention")
                elif len(name) > 2 and '_' in name:
                    good_names += 1
            
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                name = node.id
                # Check for single-letter variables (acceptable for loops)
                if len(name) == 1 and name not in ['i', 'j', 'k', 'n', 'x', 'y']:
                    score -= 0.05
                    issues.append(f"Single-letter variable '{name}' (use descriptive names)")
                elif len(name) > 2:
                    good_names += 1
        
        return {
            'score': round(max(0, min(1, score)), 3),
            'issues': issues,
            'good_names': good_names
        }
    
    @staticmethod
    def _check_duplication(code: str) -> Dict:
        """Check for code duplication"""
        lines = [line.strip() for line in code.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        if len(lines) < 5:
            return {'score': 1.0}
        
        # Simple duplication check: look for repeated line sequences
        duplicates = 0
        for i in range(len(lines) - 2):
            sequence = tuple(lines[i:i+3])
            if lines[i+3:].count(sequence[0]) > 0:
                # Found potential duplicate
                duplicates += 1
        
        score = max(0, 1 - (duplicates * 0.2))
        
        return {'score': round(score, 3)}
    
    @staticmethod
    def detect_complexity(code: str) -> Dict:
        """
        Detect time and space complexity
        
        Args:
            code: Source code
            
        Returns:
            Dictionary with complexity metrics
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {
                'cyclomatic_complexity': 0,
                'time_complexity': 'Unknown',
                'space_complexity': 'Unknown'
            }
        
        # Calculate cyclomatic complexity
        cyclomatic = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                cyclomatic += 1
            elif isinstance(node, ast.BoolOp):
                cyclomatic += len(node.values) - 1
        
        # Estimate time complexity (basic heuristic)
        max_loop_depth = CodeQualityAnalyzer._get_max_loop_depth(tree)
        
        if max_loop_depth == 0:
            time_complexity = 'O(1)'
        elif max_loop_depth == 1:
            # Check for list operations
            has_builtin = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) 
                            and n.func.id in ['sort', 'sorted'] for n in ast.walk(tree))
            time_complexity = 'O(n log n)' if has_builtin else 'O(n)'
        elif max_loop_depth == 2:
            time_complexity = 'O(n²)'
        else:
            time_complexity = f'O(n^{max_loop_depth})'
        
        # Check for recursion
        has_recursion = CodeQualityAnalyzer._has_recursion(tree)
        if has_recursion:
            time_complexity = 'O(2^n)' if 'recursive pattern' else 'O(n) or O(log n)'
        
        # Estimate space complexity (basic heuristic)
        creates_list = any(isinstance(n, ast.ListComp) for n in ast.walk(tree))
        creates_dict = any(isinstance(n, ast.DictComp) for n in ast.walk(tree))
        
        if has_recursion:
            space_complexity = 'O(n)'  # Stack frames
        elif creates_list or creates_dict:
            space_complexity = 'O(n)'
        else:
            space_complexity = 'O(1)'
        
        return {
            'cyclomatic_complexity': cyclomatic,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity
        }
    
    @staticmethod
    def _get_max_loop_depth(tree: ast.AST) -> int:
        """Calculate maximum loop nesting depth"""
        max_depth = 0
        
        def visit_depth(node, current_depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, current_depth)
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.For, ast.While)):
                    visit_depth(child, current_depth + 1)
                else:
                    visit_depth(child, current_depth)
        
        visit_depth(tree)
        return max_depth
    
    @staticmethod
    def _has_recursion(tree: ast.AST) -> bool:
        """Check if code contains recursion"""
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node
        
        # Check if any function calls itself
        for func_name, func_node in functions.items():
            for node in ast.walk(func_node):
                if isinstance(node,ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == func_name:
                        return True
        
        return False
    
    @staticmethod
    def calculate_improvement_delta(old_code: str, new_code: str) -> Dict:
        """
        Calculate improvement between two code versions
        
        Args:
            old_code: Previous code version
            new_code: New code version
            
        Returns:
            Dictionary with improvement metrics
        """
        old_metrics = CodeQualityAnalyzer.analyze_quality(old_code)
        new_metrics = CodeQualityAnalyzer.analyze_quality(new_code)
        
        quality_delta = new_metrics['quality_score'] - old_metrics['quality_score']
        complexity_delta = old_metrics['complexity_score'] - new_metrics['complexity_score']
        
        improvements = []
        regressions = []
        
        if quality_delta > 0.1:
            improvements.append(f"Code quality improved by {int(quality_delta * 100)}%")
        elif quality_delta < -0.1:
            regressions.append(f"Code quality decreased by {int(abs(quality_delta) * 100)}%")
        
        if complexity_delta > 0:
            improvements.append(f"Complexity reduced by {complexity_delta} points")
        elif complexity_delta < 0:
            regressions.append(f"Complexity increased by {abs(complexity_delta)} points")
        
        if old_metrics['time_complexity'] != new_metrics['time_complexity']:
            improvements.append(f"Time complexity changed from {old_metrics['time_complexity']} to {new_metrics['time_complexity']}")
        
        return {
            'quality_delta': round(quality_delta, 3),
            'complexity_delta': complexity_delta,
            'old_quality': old_metrics['quality_score'],
            'new_quality': new_metrics['quality_score'],
            'improvements': improvements,
            'regressions': regressions,
            'overall_improvement': quality_delta > 0 or complexity_delta > 0
        }
    
    @staticmethod
    def generate_refactoring_suggestions(code: str) -> List[str]:
        """
        Generate AI-powered refactoring suggestions
        
        Args:
            code: Source code
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        try:
            tree = ast.parse(code)
            
            # Check for long functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = len(ast.unparse(node).split('\n'))
                    if func_lines > 20:
                        suggestions.append(f"Function '{node.name}' is {func_lines} lines long. Consider breaking it into smaller functions.")
            
            # Check for nested loops
            max_depth = CodeQualityAnalyzer._get_max_loop_depth(tree)
            if max_depth > 2:
                suggestions.append(f"Deep loop nesting ({max_depth} levels) - consider refactoring for better complexity")
            
            # Check for magic numbers
            for node in ast.walk(tree):
                if isinstance(node, ast.Num) and not isinstance(node.n, bool):
                    if node.n not in [0, 1, -1] and node.n > 10:
                        suggestions.append(f"Magic number {node.n} found - consider using a named constant")
                        break
            
        except Exception as e:
            logger.error(f"Error generating refactoring suggestions: {e}")
        
        if not suggestions:
            suggestions.append("Code looks good! Consider adding more comments for clarity.")
        
        return suggestions
