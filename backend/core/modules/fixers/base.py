"""Base code fixer"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCodeFixer(ABC):
    """Base class for code fixers"""
    
    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language
        self.lines = code.split('\n')
    
    @abstractmethod
    def suggest_fixes(self) -> List[Dict[str, Any]]:
        """Generate fix suggestions"""
        pass
    
    @abstractmethod
    def auto_fix(self) -> str:
        """Apply automatic fixes and return fixed code"""
        pass
    
    @abstractmethod
    def auto_fix_rule(self, rule: str) -> str:
        """Apply fixes for a specific rule"""
        pass
