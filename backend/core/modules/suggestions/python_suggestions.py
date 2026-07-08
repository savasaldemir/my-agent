"""Python code fix suggestions"""

import re
from typing import List
from .base import BaseSuggestion, FixSuggestion, FixLevel

class PythonSuggestions(BaseSuggestion):
    """Python code fix suggestions"""
    
    def generate_suggestions(self) -> List[FixSuggestion]:
        """Generate Python fix suggestions"""
        suggestions = []
        
        suggestions.extend(self._suggest_var_fixes())
        suggestions.extend(self._suggest_import_fixes())
        suggestions.extend(self._suggest_string_fixes())
        suggestions.extend(self._suggest_indentation_fixes())
        suggestions.extend(self._suggest_security_fixes())
        suggestions.extend(self._suggest_style_fixes())
        suggestions.extend(self._suggest_performance_fixes())
        
        return suggestions
    
    def _suggest_var_fixes(self) -> List[FixSuggestion]:
        """Suggest variable naming fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Check for single letter variables (except common ones)
            matches = re.finditer(r'\b([a-z])\s*=\s*', line)
            for match in matches:
                var = match.group(1)
                if var not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    suggestions.append(FixSuggestion(
                        line=line_num,
                        column=match.start() + 1,
                        issue_rule="single-letter-variable",
                        current_code=f"{var} =",
                        suggested_code=f"variable_name =",
                        explanation=f"Single letter variable '{var}' is not descriptive. Use a meaningful name.",
                        fix_level=FixLevel.MANUAL,
                        after_context="Use descriptive variable names",
                    ))
        
        return suggestions
    
    def _suggest_import_fixes(self) -> List[FixSuggestion]:
        """Suggest import fixes"""
        suggestions = []
        
        # Suggest removing unused imports
        for line_num, line in enumerate(self.lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # Extract module name
                if 'import' in line:
                    parts = line.split('import')
                    if len(parts) > 1:
                        module = parts[-1].strip().split()[0]
                        
                        # Check if module is used
                        code_without_import = '\n'.join(
                            l for i, l in enumerate(self.lines)
                            if i != line_num - 1
                        )
                        
                        if module not in code_without_import:
                            suggestions.append(FixSuggestion(
                                line=line_num,
                                column=1,
                                issue_rule="unused-import",
                                current_code=line.strip(),
                                suggested_code="",
                                explanation=f"Module '{module}' is imported but never used",
                                fix_level=FixLevel.AUTOMATIC,
                                after_context="Remove this line",
                            ))
        
        return suggestions
    
    def _suggest_string_fixes(self) -> List[FixSuggestion]:
        """Suggest string-related fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest f-string over format()
            if '.format(' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('.format(') + 1,
                    issue_rule="use-fstring",
                    current_code='.format(',
                    suggested_code='f"..." or use f-string',
                    explanation="Use f-strings (Python 3.6+) for better readability and performance",
                    fix_level=FixLevel.SAFE,
                    after_context='name = f"Hello {world}"',
                ))
            
            # Suggest f-string over % formatting
            if '%s' in line and '%' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('%s') + 1,
                    issue_rule="use-fstring",
                    current_code='%s',
                    suggested_code='{}',
                    explanation="Replace % formatting with f-strings for better performance",
                    fix_level=FixLevel.SAFE,
                    after_context='name = f"Hello {world}"',
                ))
        
        return suggestions
    
    def _suggest_indentation_fixes(self) -> List[FixSuggestion]:
        """Suggest indentation fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            if not line:
                continue
            
            # Check for mixed tabs and spaces
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            if '\t' in leading_whitespace and ' ' in leading_whitespace:
                # Count spaces and replace with consistent indentation
                indent_level = len(leading_whitespace) // 4
                fixed_indent = '    ' * indent_level
                
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=1,
                    issue_rule="mixed-indentation",
                    current_code=line[:len(leading_whitespace)] + line[len(leading_whitespace):].lstrip(),
                    suggested_code=fixed_indent + line[len(leading_whitespace):].lstrip(),
                    explanation="Use spaces instead of tabs for consistent indentation",
                    fix_level=FixLevel.AUTOMATIC,
                ))
        
        return suggestions
    
    def _suggest_security_fixes(self) -> List[FixSuggestion]:
        """Suggest security-related fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest avoiding eval
            if 'eval(' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('eval(') + 1,
                    issue_rule="avoid-eval",
                    current_code='eval(',
                    suggested_code='ast.literal_eval(',
                    explanation="Using eval() is dangerous. Use ast.literal_eval() for safe evaluation of literals",
                    fix_level=FixLevel.RISKY,
                    before_context='import ast',
                    after_context='result = ast.literal_eval(expression)',
                ))
            
            # Suggest avoiding exec
            if 'exec(' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('exec(') + 1,
                    issue_rule="avoid-exec",
                    current_code='exec(',
                    suggested_code='# Refactor to use safer alternatives',
                    explanation="Using exec() is dangerous. Refactor to use safer alternatives",
                    fix_level=FixLevel.MANUAL,
                ))
            
            # Check for hardcoded credentials
            if any(keyword in line.lower() for keyword in ['password', 'api_key', 'secret']):
                if '=' in line and not line.strip().startswith('#'):
                    suggestions.append(FixSuggestion(
                        line=line_num,
                        column=1,
                        issue_rule="hardcoded-credentials",
                        current_code=line.strip(),
                        suggested_code='# Move to environment variables',
                        explanation="Hardcoded credentials are dangerous. Use environment variables instead",
                        fix_level=FixLevel.RISKY,
                        before_context='import os',
                        after_context='password = os.getenv("DB_PASSWORD")',
                    ))
        
        return suggestions
    
    def _suggest_style_fixes(self) -> List[FixSuggestion]:
        """Suggest style fixes (PEP 8)"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest removing trailing whitespace
            if line and line[-1] in ' \t':
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=len(line),
                    issue_rule="trailing-whitespace",
                    current_code=line,
                    suggested_code=line.rstrip(),
                    explanation="Remove trailing whitespace",
                    fix_level=FixLevel.AUTOMATIC,
                ))
            
            # Suggest space around operators
            if '==' in line and ' == ' not in line:
                fixed = line.replace('==', ' == ')
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('==') + 1,
                    issue_rule="whitespace-around-operator",
                    current_code='==',
                    suggested_code=' == ',
                    explanation="Add spaces around comparison operators (PEP 8)",
                    fix_level=FixLevel.AUTOMATIC,
                ))
        
        return suggestions
    
    def _suggest_performance_fixes(self) -> List[FixSuggestion]:
        """Suggest performance-related fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest list comprehension over append in loop
            if '+=' in line and ('"' in line or "'" in line):
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('+=') + 1,
                    issue_rule="string-concat-in-loop",
                    current_code='+=',
                    suggested_code='Use list.join() or list comprehension',
                    explanation="String concatenation in loops is inefficient. Use ''.join() instead",
                    fix_level=FixLevel.SAFE,
                    after_context='result = "".join(items)',
                ))
        
        return suggestions
