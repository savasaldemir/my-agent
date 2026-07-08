"""Code fix suggestion and application tests"""

import pytest
from ..modules.fix_factory import create_fixer, create_suggester
from ..modules.suggestions.base import FixLevel

def test_python_trailing_whitespace_suggestion():
    """Test trailing whitespace detection"""
    code = "x = 10    \nprint(x)  "
    suggester = create_suggester(code, "python")
    suggestions = suggester.generate_suggestions()
    
    assert any("trailing-whitespace" in s.issue_rule for s in suggestions)

def test_python_auto_fix_trailing_whitespace():
    """Test automatic trailing whitespace fix"""
    code = "x = 10    \nprint(x)  "
    fixer = create_fixer(code, "python")
    fixed = fixer.auto_fix()
    
    assert not fixed.endswith("   ")
    assert "x = 10" in fixed

def test_python_var_suggest():
    """Test var suggestion detection"""
    code = """
password = "secret123"
if password:
    print("ok")
"""
    suggester = create_suggester(code, "python")
    suggestions = suggester.generate_suggestions()
    
    assert any("hardcoded-credentials" in s.issue_rule for s in suggestions)

def test_javascript_var_to_const():
    """Test var to const conversion"""
    code = "var x = 10;"
    suggester = create_suggester(code, "javascript")
    suggestions = suggester.generate_suggestions()
    
    assert any("var-to-const-let" in s.issue_rule for s in suggestions)

def test_javascript_auto_fix_semicolon():
    """Test automatic semicolon addition"""
    code = "const x = 10\nreturn x"
    fixer = create_fixer(code, "javascript")
    fixed = fixer.auto_fix()
    
    assert "const x = 10;" in fixed

def test_fix_preview():
    """Test fix preview without applying"""
    code = "var x = 10;"
    fixer = create_fixer(code, "javascript")
    fixed = fixer.auto_fix_rule("var-to-const-let")
    
    assert "const" in fixed
    assert "var" not in fixed
