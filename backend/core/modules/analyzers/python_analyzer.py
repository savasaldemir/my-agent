"""Python code analyzer"""

import ast
import re
from typing import List, Dict, Any
from .base import BaseAnalyzer, CodeIssue, Severity, IssueCategory, AnalysisMetrics

class PythonAnalyzer(BaseAnalyzer):
    """Python code analyzer using AST"""
    
    def analyze(self) -> List[CodeIssue]:
        """Analyze Python code"""
        issues = []
        
        # Syntax errors
        issues.extend(self._check_syntax())
        
        # Style issues
        issues.extend(self._check_style())
        
        # Security issues
        issues.extend(self._check_security())
        
        # Performance issues
        issues.extend(self._check_performance())
        
        # Complexity issues
        issues.extend(self._check_complexity())
        
        self.issues = issues
        return issues
    
    def calculate_metrics(self) -> AnalysisMetrics:
        """Calculate Python code metrics"""
        basic_metrics = self._calculate_basic_metrics()
        complexity_score = self._calculate_cyclomatic_complexity()
        
        # Calculate quality score based on issues
        severity_weights = {
            Severity.INFO: 1,
            Severity.WARNING: 5,
            Severity.ERROR: 15,
            Severity.CRITICAL: 25,
        }
        
        penalty = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)
        quality_score = max(0, 100 - penalty)
        
        # Maintainability based on complexity and comments
        comment_ratio = basic_metrics["comment_lines"] / max(1, basic_metrics["code_lines"])
        maintainability_score = 100 - (complexity_score * 0.5) + (comment_ratio * 20)
        maintainability_score = max(0, min(100, maintainability_score))
        
        # Security score
        security_issues = [i for i in self.issues if i.category == IssueCategory.SECURITY]
        security_score = 100 - (len(security_issues) * 10)
        security_score = max(0, min(100, security_score))
        
        self.metrics = AnalysisMetrics(
            total_lines=basic_metrics["total_lines"],
            code_lines=basic_metrics["code_lines"],
            comment_lines=basic_metrics["comment_lines"],
            blank_lines=basic_metrics["blank_lines"],
            complexity_score=complexity_score,
            quality_score=quality_score,
            maintainability_score=maintainability_score,
            security_score=security_score,
        )
        
        return self.metrics
    
    def _check_syntax(self) -> List[CodeIssue]:
        """Check for syntax errors"""
        issues = []
        
        try:
            ast.parse(self.code)
        except SyntaxError as e:
            issues.append(CodeIssue(
                line=e.lineno or 1,
                column=e.offset or 1,
                severity=Severity.ERROR,
                category=IssueCategory.SYNTAX,
                rule="syntax-error",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix the syntax error",
            ))
        except Exception as e:
            issues.append(CodeIssue(
                line=1,
                column=1,
                severity=Severity.ERROR,
                category=IssueCategory.SYNTAX,
                rule="parse-error",
                message=f"Failed to parse code: {str(e)}",
                suggestion="Check code syntax",
            ))
        
        return issues
    
    def _check_style(self) -> List[CodeIssue]:
        """Check for style issues (PEP 8)"""
        issues = []
        
        # Check indentation
        issues.extend(self._count_indentation_issues())
        
        # Check line length
        issues.extend(self._count_long_lines(79))
        
        # Check trailing whitespace
        for line_num, line in enumerate(self.lines, 1):
            if line and line[-1] in ' \t':
                issues.append(CodeIssue(
                    line=line_num,
                    column=len(line),
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="trailing-whitespace",
                    message="Trailing whitespace",
                    suggestion="Remove trailing whitespace",
                ))
        
        # Check unused imports
        issues.extend(self._check_unused_imports())
        
        return issues
    
    def _check_unused_imports(self) -> List[CodeIssue]:
        """Check for unused imports"""
        issues = []
        
        try:
            tree = ast.parse(self.code)
        except:
            return issues
        
        # Find all imports
        imports = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports[name] = node.lineno
        
        # Check if imported names are used
        code_without_imports = '\n'.join(
            line for i, line in enumerate(self.lines)
            if not (ast.parse(line).body and isinstance(ast.parse(line).body[0], (ast.Import, ast.ImportFrom)))
        )
        
        for name, line_num in imports.items():
            if name not in code_without_imports and name != '*':
                issues.append(CodeIssue(
                    line=line_num,
                    column=1,
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="unused-import",
                    message=f"Unused import: {name}",
                    suggestion=f"Remove unused import '{name}'",
                ))
        
        return issues
    
    def _check_security(self) -> List[CodeIssue]:
        """Check for security issues"""
        issues = []
        
        dangerous_functions = {
            'eval': 'Using eval() is dangerous and allows code injection',
            'exec': 'Using exec() is dangerous and allows code injection',
            'pickle': 'pickle is unsafe, use json instead',
            '__import__': 'Dynamic imports with __import__ can be unsafe',
        }
        
        for line_num, line in enumerate(self.lines, 1):
            for func, message in dangerous_functions.items():
                if func in line and not line.strip().startswith('#'):
                    issues.append(CodeIssue(
                        line=line_num,
                        column=line.find(func) + 1,
                        severity=Severity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        rule=f"use-of-{func}",
                        message=f"Security issue: {message}",
                        suggestion=f"Avoid using {func}()",
                    ))
        
        # Check for hardcoded credentials
        if any(keyword in self.code for keyword in ['password', 'api_key', 'secret'] if '=' in self.code):
            for line_num, line in enumerate(self.lines, 1):
                if any(keyword in line.lower() for keyword in ['password', 'api_key', 'secret']):
                    if '=' in line and not line.strip().startswith('#'):
                        issues.append(CodeIssue(
                            line=line_num,
                            column=1,
                            severity=Severity.CRITICAL,
                            category=IssueCategory.SECURITY,
                            rule="hardcoded-credentials",
                            message="Potential hardcoded credentials detected",
                            suggestion="Use environment variables or config files",
                        ))
        
        return issues
    
    def _check_performance(self) -> List[CodeIssue]:
        """Check for performance issues"""
        issues = []
        
        # Check for string concatenation in loops
        in_loop = False
        for line_num, line in enumerate(self.lines, 1):
            if 'for ' in line or 'while ' in line:
                in_loop = True
            
            if in_loop and '+=' in line and '"' in line:
                issues.append(CodeIssue(
                    line=line_num,
                    column=line.find('+=') + 1,
                    severity=Severity.WARNING,
                    category=IssueCategory.PERFORMANCE,
                    rule="string-concat-in-loop",
                    message="String concatenation in loop is inefficient",
                    suggestion="Use list.join() instead",
                ))
        
        return issues
    
    def _check_complexity(self) -> List[CodeIssue]:
        """Check for complexity issues"""
        issues = []
        
        try:
            tree = ast.parse(self.code)
        except:
            return issues
        
        # Find functions with high cyclomatic complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = self._calculate_function_complexity(node)
                if complexity > 10:
                    issues.append(CodeIssue(
                        line=node.lineno,
                        column=1,
                        severity=Severity.WARNING,
                        category=IssueCategory.COMPLEXITY,
                        rule="high-complexity",
                        message=f"Function has high cyclomatic complexity: {complexity}",
                        suggestion="Consider breaking function into smaller parts",
                    ))
        
        return issues
    
    def _calculate_function_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
