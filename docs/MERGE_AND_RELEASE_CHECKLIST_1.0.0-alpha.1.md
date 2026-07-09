# Merge and Release Checklist - 1.0.0-alpha.1

Date: 2026-07-09

## 1) Open and merge PR
- Open compare page:
  - https://github.com/savasaldemir/my-agent/compare/main...feat/github-integration?expand=1
- Verify PR includes:
  - docs/PR_DRAFT_d60fa33.md
  - CHANGELOG.md entry for 1.0.0-alpha.1
  - docs/RELEASE_NOTES_1.0.0-alpha.1.md
  - docs/GITHUB_RELEASE_BODY_1.0.0-alpha.1.md
- Merge PR into main.

## 2) Sync local main
```powershell
git checkout main
git pull origin main
```

## 3) Create and push release tag
```powershell
git tag -a v1.0.0-alpha.1 -m "Release 1.0.0-alpha.1"
git push origin v1.0.0-alpha.1
```

## 4) Publish GitHub Release (Web UI)
- Go to: https://github.com/savasaldemir/my-agent/releases/new
- Tag: v1.0.0-alpha.1
- Release title: 1.0.0-alpha.1
- Release body source:
  - docs/GITHUB_RELEASE_BODY_1.0.0-alpha.1.md
- Check "Set as a pre-release" (alpha).
- Publish release.

Optional (token-based API publish):
```powershell
$env:GITHUB_TOKEN = "<your_token>"
.\scripts\publish-github-release.ps1
```

## 5) Post-release verification
- Confirm tag exists on remote:
```powershell
git ls-remote --tags origin
```
- Confirm release is visible on:
  - https://github.com/savasaldemir/my-agent/releases
