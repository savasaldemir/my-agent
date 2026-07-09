param(
    [string]$Owner = "savasaldemir",
    [string]$Repo = "my-agent",
    [string]$Tag = "v1.0.0-alpha.1",
    [string]$Name = "1.0.0-alpha.1",
    [string]$BodyPath = "docs/GITHUB_RELEASE_BODY_1.0.0-alpha.1.md",
    [switch]$PreRelease = $true
)

$ErrorActionPreference = "Stop"

$token = $env:GITHUB_TOKEN
if (-not $token) {
    $token = $env:GH_TOKEN
}

if (-not $token) {
    throw "Missing GitHub token. Set GITHUB_TOKEN (or GH_TOKEN) in your environment."
}

if (-not (Test-Path $BodyPath)) {
    throw "Release body file not found: $BodyPath"
}

$bodyText = Get-Content -Raw -Path $BodyPath
$uri = "https://api.github.com/repos/$Owner/$Repo/releases"

$headers = @{
    Authorization         = "Bearer $token"
    Accept                = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$payload = @{
    tag_name   = $Tag
    name       = $Name
    body       = $bodyText
    prerelease = [bool]$PreRelease
}

try {
    $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -ContentType "application/json" -Body ($payload | ConvertTo-Json -Depth 5)
    Write-Host "Release created successfully: $($response.html_url)"
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        throw "Release already exists for tag '$Tag' or payload is invalid. Check existing releases and tag state."
    }
    throw
}
