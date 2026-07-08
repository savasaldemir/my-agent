"""Advanced code analysis tests"""

import pytest
from ..modules.analyzer_factory import create_analyzer
from ..modules.analyzers.base import Severity, IssueCategory

def test_python_syntax_error():
    """Test Python syntax error detection"""
    code = """
def hello(
    print("missing closing paren")
"""
    analyzer = create_analyzer(code, "python")
    issues = analyzer.analyze()
    
    assert len(issues) > 0
    assert any(issue.severity == Severity.ERROR for issue in issues)

def test_python_unused_import():
    """Test unused import detection"""
    code = """
import os
import sys

print("hello")
"""
    analyzer = create_analyzer(code, "python")
    issues = analyzer.analyze()
    
    assert any("unused" in issue.rule.lower() for issue in issues)

def test_python_security_eval():
    """Test security issue detection"""
    code = """
user_input = "1 + 1"
result = eval(user_input)
"""
    analyzer = create_analyzer(code, "python")
    issues = analyzer.analyze()
    
    assert any(issue.category == IssueCategory.SECURITY for issue in issues)

def test_javascript_var_usage():
    """Test JavaScript var usage detection"""
    code = """
var x = 10;
console.log(x);
"""
    analyzer = create_analyzer(code, "javascript")
    issues = analyzer.analyze()
    
    assert any("var" in issue.rule for issue in issues)

def test_typescript_any_type():
    """Test TypeScript 'any' type detection"""
    code = """
function foo(param: any) {
    return param.toString();
}
"""
    analyzer = create_analyzer(code, "typescript")
    issues = analyzer.analyze()
    
    assert any("any" in issue.rule for issue in issues)

def test_analysis_metrics():
    """Test metrics calculation"""
    code = """
def hello():
    # This is a comment
    print("Hello, World!")
"""
    analyzer = create_analyzer(code, "python")
    issues = analyzer.analyze()
    metrics = analyzer.calculate_metrics()
    
    assert metrics.total_lines == 4
    assert metrics.code_lines > 0
    assert 0 <= metrics.quality_score <= 100
    assert 0 <= metrics.security_score <= 100
