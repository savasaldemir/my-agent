"""JavaScript code analyzer"""

import re
from typing import List
from .base import BaseAnalyzer, CodeIssue, Severity, IssueCategory, AnalysisMetrics

class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript code analyzer"""
    
    def analyze(self) -> List[CodeIssue]:
        """Analyze JavaScript code"""
        issues = []
        
        # Syntax-like issues
        issues.extend(self._check_syntax())
        
        # Style issues
        issues.extend(self._check_style())
        
        # Security issues
        issues.extend(self._check_security())
        
        # Best practices
        issues.extend(self._check_best_practices())
        
        self.issues = issues
        return issues
    
    def calculate_metrics(self) -> AnalysisMetrics:
        """Calculate JavaScript code metrics"""
        basic_metrics = self._calculate_basic_metrics()
        complexity_score = self._calculate_cyclomatic_complexity()
        
        severity_weights = {
            Severity.INFO: 1,
            Severity.WARNING: 5,
            Severity.ERROR: 15,
            Severity.CRITICAL: 25,
        }
        
        penalty = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)
        quality_score = max(0, 100 - penalty)
        
        maintainability_score = 100 - (complexity_score * 0.5)
        maintainability_score = max(0, min(100, maintainability_score))
        
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
        """Check for syntax issues"""
        issues = []
        
        # Check for missing semicolons (common JS issue)
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ',', ':', '//', '/*')):
                if any(keyword in stripped for keyword in ['return', 'const', 'let', 'var']):
                    issues.append(CodeIssue(
                        line=line_num,
                        column=len(line),
                        severity=Severity.WARNING,
                        category=IssueCategory.STYLE,
                        rule="missing-semicolon",
                        message="Missing semicolon",
                        suggestion="Add semicolon at end of statement",
                    ))
        
        # Check for unmatched braces
        open_braces = self.code.count('{') - self.code.count('}')
        if open_braces != 0:
            issues.append(CodeIssue(
                line=1,
                column=1,
                severity=Severity.ERROR,
                category=IssueCategory.SYNTAX,
                rule="unmatched-braces",
                message="Unmatched braces detected",
                suggestion="Check opening and closing braces",
            ))
        
        return issues
    
    def _check_style(self) -> List[CodeIssue]:
        """Check for style issues"""
        issues = []
        
        issues.extend(self._count_long_lines(100))
        issues.extend(self._count_indentation_issues())
        
        # Check for var usage (prefer const/let)
        for line_num, line in enumerate(self.lines, 1):
            if re.search(r'\bvar\s+\w+', line) and not line.strip().startswith('//'):
                issues.append(CodeIssue(
                    line=line_num,
                    column=line.find('var') + 1,
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="var-usage",
                    message="'var' is discouraged, use 'const' or 'let' instead",
                    suggestion="Replace 'var' with 'const' or 'let'",
                ))
        
        return issues
    
    def _check_security(self) -> List[CodeIssue]:
        """Check for security issues"""
        issues = []
        
        dangerous_patterns = {
            r'eval\s*\(': ('eval', 'Using eval() is dangerous'),
            r'innerHTML\s*=': ('innerHTML', 'innerHTML can cause XSS vulnerabilities'),
            r'document\.write\s*\(': ('document.write', 'document.write is dangerous'),
        }
        
        for line_num, line in enumerate(self.lines, 1):
            for pattern, (name, message) in dangerous_patterns.items():
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        line=line_num,
                        column=1,
                        severity=Severity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        rule=f"unsafe-{name}",
                        message=f"Security issue: {message}",
                        suggestion=f"Avoid using {name}",
                    ))
        
        return issues
    
    def _check_best_practices(self) -> List[CodeIssue]:
        """Check for JavaScript best practices"""
        issues = []
        
        # Check for console.log in production code
        for line_num, line in enumerate(self.lines, 1):
            if 'console.log' in line:
                issues.append(CodeIssue(
                    line=line_num,
                    column=line.find('console.log') + 1,
                    severity=Severity.INFO,
                    category=IssueCategory.STYLE,
                    rule="console-log",
                    message="console.log detected",
                    suggestion="Remove console.log before production",
                ))
        
        return issues
