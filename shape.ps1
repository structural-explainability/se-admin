# shape.ps1
Clear-Host

$ignore = @(
    '\\\.cache\\',
    '\\\.git\\',
    '\\\.venv\\',
    '\\__pycache__\\',
    '\\\.pytest_cache\\',
    '\\\.ruff_cache\\',
    '\\\.vscode\\',
    'uv\.lock'
)

Get-ChildItem -Recurse -Force -File | Where-Object {
    $path = $_.FullName
    -not ($ignore | Where-Object { $path -match $_ })
} | Select-Object FullName, Length | Sort-Object FullName
