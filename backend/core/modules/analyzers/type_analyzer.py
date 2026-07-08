"""TypeScript/Type checking analyzer"""

import re
from typing import List
from .base import BaseAnalyzer, CodeIssue, Severity, IssueCategory, AnalysisMetrics
from .javascript_analyzer import JavaScriptAnalyzer

class TypeAnalyzer(JavaScriptAnalyzer):
    """TypeScript code analyzer"""
    
    def analyze(self) -> List[CodeIssue]:
        """Analyze TypeScript code"""
        issues = super().analyze()
        
        # Additional type-specific checks
        issues.extend(self._check_types())
        
        self.issues = issues
        return issues
    
    def _check_types(self) -> List[CodeIssue]:
        """Check for type-related issues"""
        issues = []
        
        # Check for 'any' type usage
        for line_num, line in enumerate(self.lines, 1):
            if ': any' in line:
                issues.append(CodeIssue(
                    line=line_num,
                    column=line.find('any') + 1,
                    severity=Severity.WARNING,
                    category=IssueCategory.STYLE,
                    rule="any-type",
                    message="Usage of 'any' type is discouraged",
                    suggestion="Use specific types instead of 'any'",
                ))
        
        # Check for missing type annotations
        for line_num, line in enumerate(self.lines, 1):
            if re.search(r'(function|const|let|var)\s+\w+\s*\(', line):
                if ':' not in line and not line.strip().startswith('//'):
                    issues.append(CodeIssue(
                        line=line_num,
                        column=1,
                        severity=Severity.INFO,
                        category=IssueCategory.STYLE,
                        rule="missing-type-annotation",
                        message="Missing type annotation",
                        suggestion="Add type annotation for better type safety",
                    ))
        
        return issues
