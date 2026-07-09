"""Code fixing module"""

from typing import List, Dict, Any


class CodeFixer:
    """Base code fixer"""

    def __init__(self, code: str, language: str, issues: List[Dict[str, Any]]):
        self.code = code
        self.language = language
        self.issues = issues

    def fix(self) -> str:
        """Fix code issues"""
        raise NotImplementedError


class PythonFixer(CodeFixer):
    """Python code fixer"""

    def fix(self) -> str:
        """Fix Python code"""
        lines = self.code.split("\n")
        fixed_lines: List[str] = []

        for line in lines:
            normalized = line.rstrip()

            if normalized.startswith("\t"):
                normalized = normalized.replace("\t", "    ")

            if normalized.startswith("print ") and "(" not in normalized:
                normalized = normalized.replace("print ", "print(", 1) + ")"

            fixed_lines.append(normalized)

        return "\n".join(fixed_lines)


class JavaScriptFixer(CodeFixer):
    """JavaScript code fixer"""

    def fix(self) -> str:
        """Fix JavaScript code"""
        lines = self.code.split("\n")
        fixed_lines: List[str] = []

        for line in lines:
            normalized = line

            if "var " in normalized:
                normalized = normalized.replace("var ", "let ")

            stripped = normalized.strip()
            if stripped and not stripped.startswith("//") and stripped.endswith((")", "'", '"')):
                if any(
                    stripped.startswith(prefix)
                    for prefix in ["let ", "const ", "return ", "throw "]
                ):
                    normalized = normalized + ";"

            fixed_lines.append(normalized)

        return "\n".join(fixed_lines)
