"""Fix Suggestion Engine Core Service"""
import re
import ast

class FixSuggestionEngine:
    @staticmethod
    def analyze_and_suggest(code: str, language: str, auto_fix: bool = False):
        language = language.lower()
        issues = []
        fixed_code = code
        
        if language in ['python', 'py']:
            issues, fixed_code = FixSuggestionEngine._fix_python(code, auto_fix)
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            issues, fixed_code = FixSuggestionEngine._fix_javascript(code, auto_fix)
        else:
            issues.append({
                "rule": "unsupported-language",
                "severity": "INFO",
                "message": f"{language} için otomatik düzeltme kuralları henüz yüklenmedi.",
                "line": 1
            })

        confidence_level = "HIGH" if len(issues) > 0 else "NONE"
        for issue in issues:
            if issue["severity"] == "RISKY":
                confidence_level = "MEDIUM"

        return {
            "language": language,
            "total_issues_found": len(issues),
            "confidence_level": confidence_level,
            "original_code": code,
            "fixed_code": fixed_code,
            "suggestions": issues
        }

    @staticmethod
    def _fix_python(code: str, auto_fix: bool):
        issues = []
        fixed_lines = code.split('\n')
        
        # 1. Trailing Whitespace check
        for idx, line in enumerate(fixed_lines):
            if line.endswith(' ') or line.endswith('\t'):
                issues.append({
                    "rule": "trailing-whitespace",
                    "severity": "AUTOMATIC",
                    "message": "Satır sonundaki gereksiz boşluklar temizlenmeli (PEP 8).",
                    "line": idx + 1
                })
                if auto_fix:
                    fixed_lines[idx] = line.rstrip()

        # 2. Dangerous eval/exec usage check (AST Analizi)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            "rule": "dangerous-builtin",
                            "severity": "RISKY",
                            "message": f"Kritik Güvenlik Açığı: '{node.func.id}()' kullanımı SQL Injection ve uzaktan kod yürütme riskleri barındırır.",
                            "line": node.lineno
                        })
        except SyntaxError:
            issues.append({
                "rule": "syntax-error",
                "severity": "MANUAL",
                "message": "Kod içerisinde sözdizimi (Syntax) hatası tespit edildi, AST analizi durduruldu.",
                "line": 1
            })

        return issues, '\n'.join(fixed_lines)

    @staticmethod
    def _fix_javascript(code: str, auto_fix: bool):
        issues = []
        lines = code.split('\n')
        fixed_lines = lines.copy()

        for idx, line in enumerate(lines):
            # 1. var to const/let check
            if re.search(r'\bvar\s+\w+', line):
                issues.append({
                    "rule": "var-to-const-let",
                    "severity": "SAFE",
                    "message": "'var' yerine modern ES6+ standartlarında 'const' veya 'let' kullanılmalıdır.",
                    "line": idx + 1
                })
                if auto_fix:
                    fixed_lines[idx] = re.sub(r'\bvar\s+', 'let ', line)

            # 2. innerHTML XSS risk check
            if '.innerHTML' in line:
                issues.append({
                    "rule": "innerHTML-xss-risk",
                    "severity": "RISKY",
                    "message": "Potansiyel XSS (Cross-Site Scripting) Açığı: '.innerHTML' yerine '.textContent' tercih edilmelidir.",
                    "line": idx + 1
                })

            # 3. Production console.log check
            if 'console.log' in line:
                issues.append({
                    "rule": "production-console-log",
                    "severity": "AUTOMATIC",
                    "message": "Canlı ortamda log sızıntılarını önlemek için 'console.log' kaldırılmalıdır.",
                    "line": idx + 1
                })
                if auto_fix:
                    fixed_lines[idx] = re.sub(r'console\.log\(.*?\);?', '', line)

        return issues, '\n'.join(fixed_lines)
