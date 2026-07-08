"""JavaScript code fix suggestions"""

import re
from typing import List
from .base import BaseSuggestion, FixSuggestion, FixLevel

class JavaScriptSuggestions(BaseSuggestion):
    """JavaScript code fix suggestions"""
    
    def generate_suggestions(self) -> List[FixSuggestion]:
        """Generate JavaScript fix suggestions"""
        suggestions = []
        
        suggestions.extend(self._suggest_var_fixes())
        suggestions.extend(self._suggest_semicolon_fixes())
        suggestions.extend(self._suggest_string_fixes())
        suggestions.extend(self._suggest_security_fixes())
        suggestions.extend(self._suggest_style_fixes())
        
        return suggestions
    
    def _suggest_var_fixes(self) -> List[FixSuggestion]:
        """Suggest var to const/let fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            match = re.search(r'\bvar\s+(\w+)', line)
            if match:
                var_name = match.group(1)
                
                # Check if variable is reassigned
                is_reassigned = False
                for other_line in self.lines:
                    if f'{var_name} =' in other_line and other_line != line:
                        is_reassigned = True
                        break
                
                fix_type = 'let' if is_reassigned else 'const'
                
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('var') + 1,
                    issue_rule="var-to-const-let",
                    current_code='var',
                    suggested_code=fix_type,
                    explanation=f"Replace 'var' with '{fix_type}' (modern JavaScript)",
                    fix_level=FixLevel.AUTOMATIC,
                    after_context=f'{fix_type} {var_name} = value',
                ))
        
        return suggestions
    
    def _suggest_semicolon_fixes(self) -> List[FixSuggestion]:
        """Suggest adding missing semicolons"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped and not stripped.endswith((';', '{', '}', ',', '://', '/*')):
                if any(keyword in stripped for keyword in ['return', 'const', 'let', 'var', 'break']):
                    suggestions.append(FixSuggestion(
                        line=line_num,
                        column=len(line),
                        issue_rule="missing-semicolon",
                        current_code=line.rstrip(),
                        suggested_code=line.rstrip() + ';',
                        explanation="Add semicolon at end of statement",
                        fix_level=FixLevel.AUTOMATIC,
                    ))
        
        return suggestions
    
    def _suggest_string_fixes(self) -> List[FixSuggestion]:
        """Suggest string-related fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest template literals over concatenation
            if '+' in line and ('"' in line or "'" in line):
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('+') + 1,
                    issue_rule="use-template-literal",
                    current_code='+',
                    suggested_code='`...${variable}...`',
                    explanation="Use template literals for string interpolation (modern JavaScript)",
                    fix_level=FixLevel.SAFE,
                    after_context='const msg = `Hello ${name}`',
                ))
        
        return suggestions
    
    def _suggest_security_fixes(self) -> List[FixSuggestion]:
        """Suggest security-related fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Suggest avoiding innerHTML
            if 'innerHTML' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('innerHTML') + 1,
                    issue_rule="avoid-innerHTML",
                    current_code='innerHTML',
                    suggested_code='textContent or createElement',
                    explanation="innerHTML can cause XSS vulnerabilities. Use textContent or createElement instead",
                    fix_level=FixLevel.RISKY,
                    after_context='element.textContent = text;',
                ))
            
            # Suggest avoiding eval
            if 'eval(' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('eval(') + 1,
                    issue_rule="avoid-eval",
                    current_code='eval(',
                    suggested_code='JSON.parse() or other safe methods',
                    explanation="Using eval() is dangerous. Use safer alternatives",
                    fix_level=FixLevel.MANUAL,
                ))
        
        return suggestions
    
    def _suggest_style_fixes(self) -> List[FixSuggestion]:
        """Suggest style fixes"""
        suggestions = []
        
        for line_num, line in enumerate(self.lines, 1):
            # Remove console.log
            if 'console.log' in line:
                suggestions.append(FixSuggestion(
                    line=line_num,
                    column=line.find('console.log') + 1,
                    issue_rule="remove-console-log",
                    current_code=line.strip(),
                    suggested_code="// Remove for production",
                    explanation="Remove console.log before production deployment",
                    fix_level=FixLevel.AUTOMATIC,
                ))
        
        return suggestions
