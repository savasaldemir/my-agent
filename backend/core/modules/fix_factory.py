"""Factory for creating appropriate code fixer"""

from typing import Union
from .fixers.base import BaseCodeFixer
from .fixers.python_fixer import PythonCodeFixer
from .fixers.javascript_fixer import JavaScriptCodeFixer
from .suggestions.python_suggestions import PythonSuggestions
from .suggestions.javascript_suggestions import JavaScriptSuggestions

def create_fixer(code: str, language: str) -> BaseCodeFixer:
    """Create appropriate fixer based on language
    
    Args:
        code: Source code to fix
        language: Programming language
        
    Returns:
        Fixer instance
        
    Raises:
        ValueError: If language is not supported
    """
    language = language.lower().strip()
    
    language_map = {
        'python': PythonCodeFixer,
        'py': PythonCodeFixer,
        'javascript': JavaScriptCodeFixer,
        'js': JavaScriptCodeFixer,
        'typescript': JavaScriptCodeFixer,
        'ts': JavaScriptCodeFixer,
    }
    
    fixer_class = language_map.get(language)
    
    if not fixer_class:
        supported = ', '.join(language_map.keys())
        raise ValueError(
            f"Language '{language}' is not supported. "
            f"Supported languages: {supported}"
        )
    
    return fixer_class(code, language)

def create_suggester(code: str, language: str):
    """Create appropriate suggester based on language"""
    language = language.lower().strip()
    
    language_map = {
        'python': PythonSuggestions,
        'py': PythonSuggestions,
        'javascript': JavaScriptSuggestions,
        'js': JavaScriptSuggestions,
        'typescript': JavaScriptSuggestions,
        'ts': JavaScriptSuggestions,
    }
    
    suggester_class = language_map.get(language)
    
    if not suggester_class:
        supported = ', '.join(language_map.keys())
        raise ValueError(
            f"Language '{language}' is not supported. "
            f"Supported languages: {supported}"
        )
    
    return suggester_class(code, language)
