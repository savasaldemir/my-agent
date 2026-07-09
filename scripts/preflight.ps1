param(
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"

function Test-CommandAvailable {
    param([string]$Name)

    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        return $true
    }

    $knownPaths = @{
        node = @("C:\\Program Files\\nodejs\\node.exe")
        npm = @("C:\\Program Files\\nodejs\\npm.cmd")
        docker = @("C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe")
    }

    if ($knownPaths.ContainsKey($Name)) {
        foreach ($path in $knownPaths[$Name]) {
            if (Test-Path $path) {
                return $true
            }
        }
    }

    return $false
}

function Resolve-Executable {
    param([string]$Name)

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $knownPaths = @{
        node = @("C:\\Program Files\\nodejs\\node.exe")
        npm = @("C:\\Program Files\\nodejs\\npm.cmd")
        docker = @("C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe")
    }

    if ($knownPaths.ContainsKey($Name)) {
        foreach ($path in $knownPaths[$Name]) {
            if (Test-Path $path) {
                return $path
            }
        }
    }

    return $null
}

$pythonPath = if (Test-Path ".\backend\venv\Scripts\python.exe") { ".\backend\venv\Scripts\python.exe" } else { $null }
$pythonAvailable = Test-CommandAvailable "python"
$nodeAvailable = Test-CommandAvailable "node"
$npmAvailable = Test-CommandAvailable "npm"
$dockerAvailable = Test-CommandAvailable "docker"

$dockerComposeAvailable = $false
if ($dockerAvailable) {
    try {
        $dockerExe = Resolve-Executable "docker"
        & $dockerExe compose version | Out-Null
        $dockerComposeAvailable = $true
    }
    catch {
        $dockerComposeAvailable = $false
    }
}

$result = [pscustomobject]@{
    python = [pscustomobject]@{
        available = $pythonAvailable
        backendVenv = [bool]$pythonPath
        backendVenvPath = $pythonPath
    }
    node = [pscustomobject]@{ available = $nodeAvailable }
    npm = [pscustomobject]@{ available = $npmAvailable }
    docker = [pscustomobject]@{
        available = $dockerAvailable
        compose = $dockerComposeAvailable
    }
    ready = [pscustomobject]@{
        backend = ([bool]$pythonPath)
        fullstack = ($nodeAvailable -and $npmAvailable -and $dockerAvailable -and $dockerComposeAvailable)
    }
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "Preflight Check"
Write-Host "- Python available: $pythonAvailable"
Write-Host "- Backend venv python: $([bool]$pythonPath)"
Write-Host "- Node available: $nodeAvailable"
Write-Host "- npm available: $npmAvailable"
Write-Host "- Docker available: $dockerAvailable"
Write-Host "- Docker Compose available: $dockerComposeAvailable"
Write-Host "- Backend ready: $($result.ready.backend)"
Write-Host "- Fullstack ready: $($result.ready.fullstack)"
