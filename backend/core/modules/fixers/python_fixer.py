"""Python code fixer"""

import re
from typing import List, Dict, Any
from .base import BaseCodeFixer
from ..suggestions.python_suggestions import PythonSuggestions

class PythonCodeFixer(BaseCodeFixer):
    """Python code auto-fixer"""
    
    def suggest_fixes(self) -> List[Dict[str, Any]]:
        """Generate fix suggestions"""
        suggester = PythonSuggestions(self.code, self.language)
        suggestions = suggester.generate_suggestions()
        return [s.to_dict() for s in suggestions]
    
    def auto_fix(self) -> str:
        """Apply automatic fixes"""
        result = self.code
        
        # Apply automatic fixes in order
        result = self._fix_trailing_whitespace(result)
        result = self._fix_indentation(result)
        result = self._fix_operators(result)
        result = self._fix_imports(result)
        
        return result
    
    def auto_fix_rule(self, rule: str) -> str:
        """Apply fixes for specific rule"""
        fixers = {
            'trailing-whitespace': self._fix_trailing_whitespace,
            'mixed-indentation': self._fix_indentation,
            'whitespace-around-operator': self._fix_operators,
            'unused-import': self._fix_imports,
        }
        
        fixer = fixers.get(rule)
        if fixer:
            return fixer(self.code)
        
        return self.code
    
    def _fix_trailing_whitespace(self, code: str) -> str:
        """Remove trailing whitespace"""
        lines = code.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        return '\n'.join(fixed_lines)
    
    def _fix_indentation(self, code: str) -> str:
        """Fix mixed indentation"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if not line:
                fixed_lines.append(line)
                continue
            
            # Replace tabs with spaces
            leading = len(line) - len(line.lstrip())
            indent = line[:leading].replace('\t', '    ')
            fixed_lines.append(indent + line.lstrip())
        
        return '\n'.join(fixed_lines)
    
    def _fix_operators(self, code: str) -> str:
        """Add spaces around operators"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Add spaces around ==, !=, <=, >=
            fixed = re.sub(r'([^=!<>])==([^=])', r'\1 == \2', line)
            fixed = re.sub(r'([^=!<>])!=([^=])', r'\1 != \2', fixed)
            fixed = re.sub(r'([^<])<=([^=])', r'\1 <= \2', fixed)
            fixed = re.sub(r'([^>])>=([^=])', r'\1 >= \2', fixed)
            fixed_lines.append(fixed)
        
        return '\n'.join(fixed_lines)
    
    def _fix_imports(self, code: str) -> str:
        """Remove unused imports"""
        lines = code.split('\n')
        fixed_lines = []
        
        imports_to_keep = []
        
        # First pass: find all imports
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports_to_keep.append(line)
        
        # Second pass: check which imports are used
        code_without_imports = '\n'.join(
            line for line in lines
            if not (line.strip().startswith('import ') or line.strip().startswith('from '))
        )
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Extract module name
                if 'import' in line:
                    parts = line.split('import')
                    if len(parts) > 1:
                        module = parts[-1].strip().split()[0]
                        if module in code_without_imports:
                            fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
