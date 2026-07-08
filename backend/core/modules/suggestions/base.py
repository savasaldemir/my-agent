"""Base suggestion class"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class FixLevel(str, Enum):
    """Fix difficulty/automation level"""
    AUTOMATIC = "automatic"  # Can be auto-fixed
    SAFE = "safe"  # Can be auto-fixed with high confidence
    RISKY = "risky"  # Auto-fix needs review
    MANUAL = "manual"  # Requires manual intervention

@dataclass
class FixSuggestion:
    """A fix suggestion for a code issue"""
    line: int
    column: int
    issue_rule: str
    current_code: str
    suggested_code: str
    explanation: str
    fix_level: FixLevel
    before_context: str = ""
    after_context: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "line": self.line,
            "column": self.column,
            "issue_rule": self.issue_rule,
            "current_code": self.current_code,
            "suggested_code": self.suggested_code,
            "explanation": self.explanation,
            "fix_level": self.fix_level.value,
            "before_context": self.before_context,
            "after_context": self.after_context,
        }

class BaseSuggestion:
    """Base class for suggestion generators"""
    
    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language
        self.lines = code.split('\n')
    
    def generate_suggestions(self) -> List[FixSuggestion]:
        """Generate fix suggestions"""
        return []
    
    def apply_fix(self, suggestion: FixSuggestion) -> str:
        """Apply a fix suggestion to code
        
        Args:
            suggestion: Fix suggestion to apply
            
        Returns:
            Modified code
        """
        lines = self.lines.copy()
        line_idx = suggestion.line - 1
        
        if line_idx >= len(lines):
            return self.code
        
        line = lines[line_idx]
        
        # Replace the suggested code
        if suggestion.current_code in line:
            lines[line_idx] = line.replace(
                suggestion.current_code,
                suggestion.suggested_code,
                1
            )
        
        return '\n'.join(lines)
    
    def apply_multiple_fixes(self, suggestions: List[FixSuggestion]) -> str:
        """Apply multiple fixes to code
        
        Args:
            suggestions: List of fix suggestions (sorted by line, descending)
            
        Returns:
            Modified code
        """
        # Sort by line number in descending order to avoid line shifting
        sorted_suggestions = sorted(suggestions, key=lambda s: s.line, reverse=True)
        
        result = self.code
        for suggestion in sorted_suggestions:
            result = self.apply_fix(suggestion)
        
        return result
