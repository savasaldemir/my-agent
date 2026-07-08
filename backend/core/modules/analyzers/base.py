"""Base analyzer class"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum
from dataclasses import dataclass

class Severity(str, Enum):
    """Issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class IssueCategory(str, Enum):
    """Issue categories"""
    SYNTAX = "syntax"
    STYLE = "style"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"

@dataclass
class CodeIssue:
    """Represents a code issue"""
    line: int
    column: int
    severity: Severity
    category: IssueCategory
    rule: str
    message: str
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "category": self.category.value,
            "rule": self.rule,
            "message": self.message,
            "suggestion": self.suggestion,
        }

@dataclass
class AnalysisMetrics:
    """Code analysis metrics"""
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    complexity_score: float  # 0-100
    quality_score: float  # 0-100
    maintainability_score: float  # 0-100
    security_score: float  # 0-100
    
    def average_score(self) -> float:
        """Calculate average score"""
        return (self.quality_score + self.maintainability_score + self.security_score) / 3

class BaseAnalyzer(ABC):
    """Base class for code analyzers"""
    
    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language
        self.lines = code.split('\n')
        self.issues: List[CodeIssue] = []
        self.metrics: AnalysisMetrics = None
    
    @abstractmethod
    def analyze(self) -> List[CodeIssue]:
        """Analyze code and return issues"""
        pass
    
    @abstractmethod
    def calculate_metrics(self) -> AnalysisMetrics:
        """Calculate code metrics"""
        pass
    
    def _calculate_basic_metrics(self) -> Dict[str, int]:
        """Calculate basic line metrics"""
        total_lines = len(self.lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        in_multiline_comment = False
        
        for line in self.lines:
            stripped = line.strip()
            
            if not stripped:
                blank_lines += 1
                continue
            
            # Check for comments (language agnostic)
            if stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
                continue
            
            if '"""' in stripped or "'''" in stripped:
                in_multiline_comment = not in_multiline_comment
                comment_lines += 1
                continue
            
            if in_multiline_comment:
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
        }
    
    def _calculate_cyclomatic_complexity(self) -> float:
        """Calculate cyclomatic complexity (simplified)"""
        complexity = 1
        keywords = ['if', 'elif', 'else', 'for', 'while', 'except', 'case', 'and', 'or']
        
        for line in self.lines:
            for keyword in keywords:
                # Simple keyword matching
                complexity += line.count(keyword)
        
        # Normalize to 0-100 scale
        return min(100, (complexity / max(1, len(self.lines))) * 100)
    
    def _count_indentation_issues(self) -> List[CodeIssue]:
        """Find indentation issues"""
        issues = []
        
        for line_num, line in enumerate(self.lines, 1):
            if not line or line[0] not in ' \t':
                continue
            
            # Check for mixed tabs and spaces
            leading_whitespace = len(line) - len(line.lstrip())
            if '\t' in line[:leading_whitespace] and ' ' in line[:leading_whitespace]:
                issues.append(CodeIssue(
                    line=line_num,
                    column=1,
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="mixed-indentation",
                    message="Mixed tabs and spaces in indentation",
                    suggestion="Use either tabs or spaces consistently",
                ))
        
        return issues
    
    def _count_long_lines(self, max_length: int = 100) -> List[CodeIssue]:
        """Find lines that are too long"""
        issues = []
        
        for line_num, line in enumerate(self.lines, 1):
            if len(line) > max_length:
                issues.append(CodeIssue(
                    line=line_num,
                    column=max_length,
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="line-too-long",
                    message=f"Line too long ({len(line)} > {max_length} characters)",
                    suggestion=f"Break line into multiple lines",
                ))
        
        return issues
    
    def _find_unused_variables(self) -> List[CodeIssue]:
        """Find potentially unused variables (simplified)"""
        issues = []
        # This is a simplified version - real implementation would need AST parsing
        return issues
