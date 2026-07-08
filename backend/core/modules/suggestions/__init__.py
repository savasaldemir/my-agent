"""Fix suggestion engine"""

from .base import BaseSuggestion, FixSuggestion
from .python_suggestions import PythonSuggestions
from .javascript_suggestions import JavaScriptSuggestions

__all__ = [
    "BaseSuggestion",
    "FixSuggestion",
    "PythonSuggestions",
    "JavaScriptSuggestions",
]
