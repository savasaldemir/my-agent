"""Code analysis module"""

import ast
from typing import List, Dict, Any
from enum import Enum


class Severity(str, Enum):
    """Issue severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Issue:
    """Code issue"""

    def __init__(
        self,
        line: int,
        column: int,
        severity: Severity,
        message: str,
        rule: str,
    ):
        self.line = line
        self.column = column
        self.severity = severity
        self.message = message
        self.rule = rule

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "message": self.message,
            "rule": self.rule,
        }


class CodeAnalyzer:
    """Base code analyzer"""

    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language
        self.issues: List[Issue] = []

    def analyze(self) -> List[Issue]:
        """Analyze code"""
        raise NotImplementedError


class PythonAnalyzer(CodeAnalyzer):
    """Python code analyzer"""

    def analyze(self) -> List[Issue]:
        """Analyze Python code"""
        try:
            ast.parse(self.code)
        except SyntaxError as e:
            self.issues.append(
                Issue(
                    line=e.lineno or 1,
                    column=e.offset or 0,
                    severity=Severity.ERROR,
                    message=f"Syntax error: {e.msg}",
                    rule="syntax-error",
                )
            )
        return self.issues


class JavaScriptAnalyzer(CodeAnalyzer):
    """JavaScript code analyzer"""

    def analyze(self) -> List[Issue]:
        """Analyze JavaScript code"""
        # TODO: Implement JavaScript analysis
        return self.issues


def create_analyzer(code: str, language: str) -> CodeAnalyzer:
    """Factory function to create appropriate analyzer"""
    language = language.lower()

    if language in ["python", "py"]:
        return PythonAnalyzer(code, language)
    elif language in ["javascript", "js", "typescript", "ts"]:
        return JavaScriptAnalyzer(code, language)
    else:
        raise ValueError(f"Unsupported language: {language}")
