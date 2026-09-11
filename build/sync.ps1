<#
  Wrapper for bridge/decomp_bridge.py suitable for Task Scheduler / manual runs.
  Puts the GitHub Desktop bundled git on PATH (no standalone git on this box),
  then pulls the decomp and regenerates the recomp build inputs.

  decomp_bridge.py is generic -- -Config picks which games/<name>/config.toml
  it targets. Defaults to Parasite Eve.

  Usage:
    powershell -ExecutionPolicy Bypass -File build\sync.ps1
    powershell -ExecutionPolicy Bypass -File build\sync.ps1 -NoPull
    powershell -ExecutionPolicy Bypass -File build\sync.ps1 -Config games\some-other-game\config.toml
#>
param([switch]$NoPull, [string]$Config = (Join-Path $PSScriptRoot '..\games\parasite-eve\config.toml'))

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

# Resolve newest GitHub Desktop bundled git, if there's no standalone git on PATH.
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $gd = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    $gitCmd = Get-ChildItem $gd -Directory -Filter 'app-*' -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        ForEach-Object { Join-Path $_.FullName 'resources\app\git\cmd' } |
        Where-Object { Test-Path (Join-Path $_ 'git.exe') } |
        Select-Object -First 1
    if ($gitCmd) {
        $env:Path = "$gitCmd;$env:Path"
        $env:GIT  = Join-Path $gitCmd 'git.exe'
    }
}

$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $py) { throw 'python not found on PATH' }

$bridge = Join-Path $repoRoot 'bridge\decomp_bridge.py'
$args = @($bridge, '--config', $Config)
if ($NoPull) { $args += '--no-pull' }

$log = Join-Path $PSScriptRoot 'sync.log'
$stamp = (Get-Date).ToString('s')
"=== $stamp ===" | Out-File -Append -Encoding utf8 $log
& $py @args 2>&1 | Tee-Object -Append -FilePath $log
exit $LASTEXITCODE
