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
        lines = self.code.split("\n")
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()

            if stripped.startswith("var "):
                self.issues.append(
                    Issue(
                        line=idx,
                        column=1,
                        severity=Severity.WARNING,
                        message="Prefer let/const over var",
                        rule="no-var",
                    )
                )

            if "console.log(" in stripped:
                self.issues.append(
                    Issue(
                        line=idx,
                        column=max(stripped.find("console.log(") + 1, 1),
                        severity=Severity.INFO,
                        message="Remove debug logging before production",
                        rule="no-console",
                    )
                )

            if stripped and not stripped.endswith((";", "{", "}", ")")) and not stripped.startswith("//"):
                if any(
                    stripped.startswith(keyword)
                    for keyword in ["const ", "let ", "var ", "return ", "throw ", "import ", "export "]
                ):
                    self.issues.append(
                        Issue(
                            line=idx,
                            column=len(stripped),
                            severity=Severity.INFO,
                            message="Consider adding a semicolon for consistency",
                            rule="semi",
                        )
                    )

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
