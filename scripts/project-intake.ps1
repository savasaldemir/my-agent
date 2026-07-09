param(
    [string]$ProjectPath = ".",
    [string]$OutputDir = ".agent-intake",
    [string[]]$ExtraExcludeDirs = @("fabrika_Agent")
)

$ErrorActionPreference = "Stop"

$resolvedProjectPath = Resolve-Path -Path $ProjectPath -ErrorAction Stop
$projectRoot = $resolvedProjectPath.Path

if (-not (Test-Path -Path $projectRoot -PathType Container)) {
    throw "Project path is not a directory: $projectRoot"
}

$outputPath = Join-Path $projectRoot $OutputDir
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null

Write-Host "Scanning project: $projectRoot"
Write-Host "Output directory: $outputPath"

$excludeDirs = @(
    ".git", "node_modules", ".venv", "venv", "dist", "build", "out", "coverage", ".next", ".turbo", "target", "bin", "obj", ".agent-intake", "__pycache__"
)

if ($ExtraExcludeDirs -and $ExtraExcludeDirs.Count -gt 0) {
    $excludeDirs += $ExtraExcludeDirs
}

$extensionToLanguage = @{
    ".py" = "python"
    ".js" = "javascript"
    ".jsx" = "javascript"
    ".ts" = "typescript"
    ".tsx" = "typescript"
    ".go" = "go"
    ".java" = "java"
    ".kt" = "kotlin"
    ".cs" = "csharp"
    ".rs" = "rust"
    ".php" = "php"
    ".rb" = "ruby"
    ".swift" = "swift"
    ".dart" = "dart"
    ".cpp" = "cpp"
    ".cc" = "cpp"
    ".cxx" = "cpp"
    ".c" = "c"
    ".h" = "c"
    ".hpp" = "cpp"
    ".sql" = "sql"
}

$frameworkHints = @(
    @{ name = "fastapi"; kind = "framework"; indicators = @("requirements.txt", "pyproject.toml", "app.py", "main.py") },
    @{ name = "django"; kind = "framework"; indicators = @("manage.py", "settings.py") },
    @{ name = "flask"; kind = "framework"; indicators = @("app.py", "wsgi.py") },
    @{ name = "express"; kind = "framework"; indicators = @("package.json") },
    @{ name = "nestjs"; kind = "framework"; indicators = @("nest-cli.json", "main.ts") },
    @{ name = "react"; kind = "frontend"; indicators = @("package.json", "vite.config.ts", "next.config.js") },
    @{ name = "spring-boot"; kind = "framework"; indicators = @("pom.xml", "build.gradle", "application.properties") },
    @{ name = "aspnet-core"; kind = "framework"; indicators = @("*.csproj", "Program.cs") },
    @{ name = "laravel"; kind = "framework"; indicators = @("artisan", "composer.json") },
    @{ name = "rails"; kind = "framework"; indicators = @("Gemfile", "config/routes.rb") }
)

$dbPatterns = @(
    @{ name = "postgresql"; regex = "postgres(ql)?|psycopg|asyncpg|typeorm.*postgres|prisma.*postgres" },
    @{ name = "mysql"; regex = "mysql|mariadb|pymysql|mysql2" },
    @{ name = "sqlite"; regex = "sqlite|sqlite3" },
    @{ name = "mongodb"; regex = "mongodb|mongoose|motor" },
    @{ name = "redis"; regex = "redis|ioredis|aioredis" },
    @{ name = "sqlserver"; regex = "sqlserver|mssql|pyodbc|EntityFramework" },
    @{ name = "oracle"; regex = "oracle|cx_oracle|oracledb" }
)

$securityPatterns = @(
    @{ id = "hardcoded-secret"; regex = '(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["''][^"'']{8,}'; severity = "high" },
    @{ id = "unsafe-eval"; regex = '(?i)\beval\s*\('; severity = "high" },
    @{ id = "unsafe-exec"; regex = '(?i)\bexec\s*\('; severity = "high" },
    @{ id = "debug-enabled"; regex = '(?i)debug\s*=\s*true'; severity = "medium" },
    @{ id = "console-log"; regex = '(?i)console\.log\('; severity = "low" }
)

function Is-ExcludedPath {
    param([string]$FullPath)

    foreach ($dir in $excludeDirs) {
        if ($FullPath -match "[\\/]$([regex]::Escape($dir))([\\/]|$)") {
            return $true
        }
    }
    return $false
}

$allFiles = Get-ChildItem -Path $projectRoot -Recurse -File | Where-Object {
    -not (Is-ExcludedPath $_.FullName)
}

$totalFiles = $allFiles.Count

$languageCounts = @{}
foreach ($file in $allFiles) {
    $ext = $file.Extension.ToLowerInvariant()
    if ($extensionToLanguage.ContainsKey($ext)) {
        $lang = $extensionToLanguage[$ext]
        if (-not $languageCounts.ContainsKey($lang)) {
            $languageCounts[$lang] = 0
        }
        $languageCounts[$lang]++
    }
}

$detectedDatabases = @()
$textFiles = $allFiles | Where-Object {
    $_.Length -lt 2MB -and $_.Extension.ToLowerInvariant() -notin @(
        ".pyc", ".pyo", ".exe", ".dll", ".so", ".dylib", ".msix", ".zip", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".pdf"
    )
}

# Limit DB signal scan to dependency/config files to reduce false positives from docs.
$dbSignalFiles = $allFiles | Where-Object {
    $_.Name -in @(
        "requirements.txt",
        "pyproject.toml",
        "Pipfile",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "go.mod",
        "Cargo.toml",
        "composer.json",
        "Gemfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env",
        ".env.example"
    )
}

foreach ($pattern in $dbPatterns) {
    $found = Select-String -Path ($dbSignalFiles.FullName) -Pattern $pattern.regex -SimpleMatch:$false -CaseSensitive:$false -ErrorAction SilentlyContinue
    if ($found) {
        $detectedDatabases += $pattern.name
    }
}
$detectedDatabases = $detectedDatabases | Sort-Object -Unique

$securityFindings = @()
foreach ($pattern in $securityPatterns) {
    $matches = Select-String -Path ($textFiles.FullName) -Pattern $pattern.regex -SimpleMatch:$false -CaseSensitive:$false -ErrorAction SilentlyContinue
    foreach ($m in $matches) {
        if ($pattern.id -eq "hardcoded-secret" -and $m.Line -match "<your_|<token>|<secret>") {
            continue
        }

        $securityFindings += [pscustomobject]@{
            id = $pattern.id
            severity = $pattern.severity
            file = $m.Path
            line = $m.LineNumber
            preview = $m.Line.Trim()
        }
    }
}

$envFiles = Get-ChildItem -Path $projectRoot -Recurse -File -Filter ".env" -ErrorAction SilentlyContinue | Where-Object {
    -not (Is-ExcludedPath $_.FullName)
}
foreach ($envFile in $envFiles) {
    $securityFindings += [pscustomobject]@{
        id = "env-file-present"
        severity = "medium"
        file = $envFile.FullName
        line = 0
        preview = ".env file exists; ensure it is not committed with secrets"
    }
}

$securityFindings = $securityFindings | Select-Object -First 200

$topLanguages = $languageCounts.GetEnumerator() | Sort-Object -Property Value -Descending
$primaryLanguage = if ($topLanguages.Count -gt 0) { $topLanguages[0].Key } else { "unknown" }

$profile = [pscustomobject]@{
    scannedAt = (Get-Date).ToString("s")
    projectRoot = $projectRoot
    totalFiles = $totalFiles
    primaryLanguage = $primaryLanguage
    languageBreakdown = $languageCounts
    databases = $detectedDatabases
    securityFindingCount = ($securityFindings | Measure-Object).Count
    securityFindingsBySeverity = @{
        high = ($securityFindings | Where-Object { $_.severity -eq "high" } | Measure-Object).Count
        medium = ($securityFindings | Where-Object { $_.severity -eq "medium" } | Measure-Object).Count
        low = ($securityFindings | Where-Object { $_.severity -eq "low" } | Measure-Object).Count
    }
}

$profilePath = Join-Path $outputPath "project-profile.json"
$findingsPath = Join-Path $outputPath "security-findings.json"
$reportPath = Join-Path $outputPath "intake-report.md"

$profile | ConvertTo-Json -Depth 8 | Set-Content -Path $profilePath -Encoding UTF8
$securityFindings | ConvertTo-Json -Depth 8 | Set-Content -Path $findingsPath -Encoding UTF8

$languageTable = if ($topLanguages.Count -gt 0) {
    ($topLanguages | ForEach-Object { "- $($_.Key): $($_.Value) file(s)" }) -join "`n"
}
else {
    "- No recognized source files found"
}

$dbTable = if ($detectedDatabases.Count -gt 0) {
    ($detectedDatabases | ForEach-Object { "- $_" }) -join "`n"
}
else {
    "- No database patterns detected"
}

$highRiskCount = ($securityFindings | Where-Object { $_.severity -eq "high" } | Measure-Object).Count
$mediumRiskCount = ($securityFindings | Where-Object { $_.severity -eq "medium" } | Measure-Object).Count

$recommendations = @()
$recommendations += "1. Add/verify CI checks: lint, test, dependency audit, secret scan."
$recommendations += "2. Move all secrets to environment variables and a secret manager."
$recommendations += "3. Enforce authZ/authN boundaries and input validation on all API boundaries."
if ($highRiskCount -gt 0) {
    $recommendations += "4. Resolve high severity findings before shipping."
}
if ($detectedDatabases.Count -gt 0) {
    $recommendations += "5. Add migration and backup strategy for: $($detectedDatabases -join ', ')."
}

$report = @"
# Project Intake Report

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Project Root: $projectRoot

## Summary
- Total files scanned: $totalFiles
- Primary language: $primaryLanguage
- Databases detected: $($detectedDatabases -join ", ")
- Security findings: $($securityFindings.Count)
  - High: $highRiskCount
  - Medium: $mediumRiskCount
  - Low: $(($securityFindings | Where-Object { $_.severity -eq "low" } | Measure-Object).Count)

## Language Breakdown
$languageTable

## Database Signals
$dbTable

## Top Recommendations
$($recommendations -join "`n")

## Output Files
- project-profile.json
- security-findings.json
- intake-report.md

"@

Set-Content -Path $reportPath -Value $report -Encoding UTF8

Write-Host "Intake completed."
Write-Host "- Profile: $profilePath"
Write-Host "- Findings: $findingsPath"
Write-Host "- Report: $reportPath"
