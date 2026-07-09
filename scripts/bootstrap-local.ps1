param(
    [switch]$AutoInstallRuntimes,
    [switch]$StartInfra
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {

function Invoke-ExternalChecked {
    param(
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
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
        python = @("C:\\Python312\\python.exe", "C:\\Python311\\python.exe", "C:\\Users\\$env:USERNAME\\AppData\\Local\\Programs\\Python\\Python312\\python.exe")
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

function Ensure-WingetInstalled {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "winget not found. Please install App Installer (Microsoft Store)."
    }
}

function Ensure-Command {
    param(
        [string]$Name,
        [string]$WingetId
    )

    $resolved = Resolve-Executable $Name
    if ($resolved) {
        return $resolved
    }

    if (-not $AutoInstallRuntimes) {
        throw "$Name is missing. Re-run with -AutoInstallRuntimes to install automatically."
    }

    Ensure-WingetInstalled
    Write-Host "Installing $Name via winget ($WingetId)..."
    Invoke-ExternalChecked -FilePath "winget" -Arguments @("install", "-e", "--id", $WingetId, "--accept-package-agreements", "--accept-source-agreements")

    $resolved = Resolve-Executable $Name
    if (-not $resolved) {
        $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $env:Path = "$machinePath;$userPath"
    }

    $resolved = Resolve-Executable $Name
    if (-not $resolved) {
        throw "$Name installation did not become available in current shell. Open a new terminal and run again."
    }

    return $resolved
}

$pythonExe = Ensure-Command -Name "python" -WingetId "Python.Python.3.12"
$nodeExe = Ensure-Command -Name "node" -WingetId "OpenJS.NodeJS.LTS"
$npmExe = Ensure-Command -Name "npm" -WingetId "OpenJS.NodeJS.LTS"
$dockerExe = Ensure-Command -Name "docker" -WingetId "Docker.DockerDesktop"

$venvPython = Join-Path $RepoRoot "backend\venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating backend venv..."
    Invoke-ExternalChecked -FilePath $pythonExe -Arguments @("-m", "venv", (Join-Path $RepoRoot "backend/venv"))
}

Write-Host "Installing backend Python dependencies..."
$requirementsFile = Join-Path $RepoRoot "backend/core/requirements.local.txt"
if (-not (Test-Path $requirementsFile)) {
    $requirementsFile = Join-Path $RepoRoot "backend/core/requirements.txt"
}
Invoke-ExternalChecked -FilePath $venvPython -Arguments @("-m", "pip", "install", "-r", $requirementsFile)

Write-Host "Installing Node dependencies for API gateway and frontend..."
Push-Location (Join-Path $RepoRoot "backend/api-gateway")
Invoke-ExternalChecked -FilePath $npmExe -Arguments @("install")
Pop-Location

Push-Location (Join-Path $RepoRoot "frontend/web")
Invoke-ExternalChecked -FilePath $npmExe -Arguments @("install")
Pop-Location

if ($StartInfra) {
    Write-Host "Starting infrastructure with Docker Compose..."
    Invoke-ExternalChecked -FilePath $dockerExe -Arguments @("compose", "-f", (Join-Path $RepoRoot "deployment/docker-compose.yml"), "up", "-d")
}

Write-Host "Bootstrap completed successfully."
}
finally {
    Pop-Location
}
