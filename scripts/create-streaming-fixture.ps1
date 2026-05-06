# scripts/create-streaming-fixture.ps1
# Create an empty streaming-course fixture for se-admin portability tests.
# run with
#   .\scripts\create-streaming-fixture.ps1

$ErrorActionPreference = "Stop"

$FixtureRoot = Join-Path "tests" "fixtures"
$StreamingFixture = Join-Path $FixtureRoot "streaming-admin"

$DataDir = Join-Path $StreamingFixture "data"
$WorkspaceDir = Join-Path $StreamingFixture "workspace"

$Repos = @(
    "streaming-00-admin",
    "streaming-01-foundations",
    "streaming-02-kafka",
    "streaming-03-data",
    "streaming-04-visualization",
    "streaming-05-storage",
    "streaming-06-scenarios",
    "streaming-07-applied"
)

# Create fixture directories.
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
New-Item -ItemType Directory -Force -Path $WorkspaceDir | Out-Null

foreach ($Repo in $Repos) {
    $RepoRoot = Join-Path $WorkspaceDir $Repo
    New-Item -ItemType Directory -Force -Path $RepoRoot | Out-Null

    # Minimal files expected by common profiles.
    New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "src") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "tests") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot "docs") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $RepoRoot ".github/workflows") | Out-Null

    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot "README.md") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot "LICENSE") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot ".markdownlint.yml") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot "pyproject.toml") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot "zensical.toml") | Out-Null

    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot ".github/workflows/ci-python-zensical.yml") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot ".github/workflows/deploy-zensical.yml") | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $RepoRoot ".github/workflows/links.yml") | Out-Null
}

# Fixture config files.
New-Item -ItemType File -Force -Path (Join-Path $DataDir "repos.toml") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $DataDir "profiles.toml") | Out-Null

Write-Host "Created fixture at $StreamingFixture"
