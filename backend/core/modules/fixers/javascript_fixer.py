"""JavaScript code fixer"""

import re
from typing import List, Dict, Any
from .base import BaseCodeFixer
from ..suggestions.javascript_suggestions import JavaScriptSuggestions

class JavaScriptCodeFixer(BaseCodeFixer):
    """JavaScript code auto-fixer"""
    
    def suggest_fixes(self) -> List[Dict[str, Any]]:
        """Generate fix suggestions"""
        suggester = JavaScriptSuggestions(self.code, self.language)
        suggestions = suggester.generate_suggestions()
        return [s.to_dict() for s in suggestions]
    
    def auto_fix(self) -> str:
        """Apply automatic fixes"""
        result = self.code
        
        result = self._fix_var_to_const(result)
        result = self._fix_semicolons(result)
        result = self._fix_trailing_whitespace(result)
        
        return result
    
    def auto_fix_rule(self, rule: str) -> str:
        """Apply fixes for specific rule"""
        fixers = {
            'var-to-const-let': self._fix_var_to_const,
            'missing-semicolon': self._fix_semicolons,
            'trailing-whitespace': self._fix_trailing_whitespace,
        }
        
        fixer = fixers.get(rule)
        if fixer:
            return fixer(self.code)
        
        return self.code
    
    def _fix_var_to_const(self, code: str) -> str:
        """Replace var with const/let"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Replace var with const (simple cases)
            if re.search(r'\bvar\s+(\w+)\s*=', line):
                fixed_line = re.sub(r'\bvar\b', 'const', line)
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_semicolons(self, code: str) -> str:
        """Add missing semicolons"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            stripped = line.rstrip()
            if stripped and not stripped.endswith((';', '{', '}', ',', '://', '/*')):
                if any(keyword in stripped for keyword in ['return', 'const', 'let', 'var']):
                    fixed_lines.append(stripped + ';')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_trailing_whitespace(self, code: str) -> str:
        """Remove trailing whitespace"""
        lines = code.split('\n')
        return '\n'.join(line.rstrip() for line in lines)
