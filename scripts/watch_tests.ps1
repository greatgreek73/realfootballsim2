param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')),
    [string[]]$PytestArgs = @()
)

$ErrorActionPreference = 'Stop'

function Get-Snapshot {
    param([string]$Path)

    Get-ChildItem -Path $Path -Recurse -File -Include *.py |
        Where-Object {
            $_.FullName -notmatch '\\(venv|env|\.git|node_modules|__pycache__|staticfiles|logs)(\\|$)'
        } |
        Sort-Object FullName |
        ForEach-Object { "$($_.FullName):$($_.LastWriteTimeUtc.Ticks)" }
}

function Invoke-Pytest {
    param([string]$ProjectRoot, [string[]]$Args)

    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] Running pytest $($Args -join ' ')..." -ForegroundColor Cyan
    Push-Location $ProjectRoot
    try {
        & python -m pytest @Args
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path $Root)) {
    throw "Path '$Root' does not exist."
}

$signature = (Get-Snapshot -Path $Root) -join '|'

Invoke-Pytest -ProjectRoot $Root -Args $PytestArgs

while ($true) {
    Start-Sleep -Milliseconds 800
    $nextSignature = (Get-Snapshot -Path $Root) -join '|'
    if ($nextSignature -ne $signature) {
        $signature = $nextSignature
        Invoke-Pytest -ProjectRoot $Root -Args $PytestArgs
    }
}
