param(
    [string]$Tag = "v1.0.0-alpha.1",
    [string]$Message = "Release 1.0.0-alpha.1"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Switching to main..."
git checkout main

Write-Host "[2/5] Pulling latest main from origin..."
git pull origin main

Write-Host "[3/5] Creating annotated tag $Tag..."
$existingTag = git tag -l $Tag
if ($existingTag) {
    throw "Tag '$Tag' already exists locally."
}
git tag -a $Tag -m $Message

Write-Host "[4/5] Pushing tag to origin..."
git push origin $Tag

Write-Host "[5/5] Verifying remote tag..."
git ls-remote --tags origin | Select-String $Tag

Write-Host "Done. Now publish the GitHub release in Web UI and mark it as pre-release."
