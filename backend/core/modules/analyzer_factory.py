"""Factory for creating appropriate analyzer"""

from typing import Union
from .analyzers.base import BaseAnalyzer
from .analyzers.python_analyzer import PythonAnalyzer
from .analyzers.javascript_analyzer import JavaScriptAnalyzer
from .analyzers.type_analyzer import TypeAnalyzer

def create_analyzer(code: str, language: str) -> BaseAnalyzer:
    """Create appropriate analyzer based on language
    
    Args:
        code: Source code to analyze
        language: Programming language
        
    Returns:
        Analyzer instance
        
    Raises:
        ValueError: If language is not supported
    """
    language = language.lower().strip()
    
    # Map language names to analyzers
    language_map = {
        'python': PythonAnalyzer,
        'py': PythonAnalyzer,
        'javascript': JavaScriptAnalyzer,
        'js': JavaScriptAnalyzer,
        'typescript': TypeAnalyzer,
        'ts': TypeAnalyzer,
    }
    
    analyzer_class = language_map.get(language)
    
    if not analyzer_class:
        supported = ', '.join(language_map.keys())
        raise ValueError(
            f"Language '{language}' is not supported. "
            f"Supported languages: {supported}"
        )
    
    return analyzer_class(code, language)

def get_supported_languages() -> list:
    """Get list of supported languages"""
    return [
        'python',
        'javascript',
        'typescript',
    ]
