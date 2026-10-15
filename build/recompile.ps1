<#
  Rebuild the Parasite Eve recomp after mod changes (src/mods/*.c), optionally launch it.

  Runs `ninja -C <BuildDir>` in the recomp checkout named by games/parasite-eve/config.toml
  ([paths].recomp), the same way play.ps1 finds it. The link step can't replace
  Parasite_Eve.exe while the game runs, so a running game is reported (or waited for with
  -Wait) instead of failing halfway.

  Not for game.toml hook changes (mod_function_entry_funcs): those need a regenerate,
  build_recomp.ps1 -SkipSync (and copy the movie player's overlay cache into the new
  cache folder afterwards).

  Usage:
    powershell -ExecutionPolicy Bypass -File build\recompile.ps1
      -Launch       start the game when the build succeeds (play.ps1, debug port 4370)
      -Wait         wait for a running game to close instead of stopping
      -BuildDir     default build-release
#>
param(
    [switch]$Launch,
    [switch]$Wait,
    [string]$BuildDir = 'build-release',
    [string]$Config = (Join-Path $PSScriptRoot '..\games\parasite-eve\config.toml')
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$printed = python (Join-Path $repoRoot 'bridge\decomp_bridge.py') --config $Config --print-paths
$recomp  = ($printed | Where-Object { $_ -like 'recomp=*' }) -replace '^recomp=', ''
if (-not $recomp) { throw "could not resolve [paths].recomp from $Config" }
$build = Join-Path $recomp $BuildDir
$exe   = Join-Path $build 'Parasite_Eve.exe'
if (-not (Test-Path $build)) { throw "no build folder: $build (run build_recomp.ps1 first)" }

# The game holds Parasite_Eve.exe open, so the link would fail.
$running = Get-Process Parasite_Eve -ErrorAction SilentlyContinue
if ($running) {
    if (-not $Wait) {
        Write-Host 'Parasite Eve is running: close the game (or use -Wait), then run this again.' -ForegroundColor Yellow
        exit 2
    }
    Write-Host 'Waiting for Parasite Eve to close...'
    $running | Wait-Process
}

$before = if (Test-Path $exe) { (Get-Item $exe).LastWriteTime } else { $null }
Write-Host "Building $build"
& ninja -C $build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build FAILED (ninja exit $LASTEXITCODE). The game was not changed." -ForegroundColor Red
    exit $LASTEXITCODE
}
$after = (Get-Item $exe).LastWriteTime
if ($before -and $after -eq $before) {
    Write-Host 'Build OK: already up to date, nothing changed.' -ForegroundColor Green
} else {
    Write-Host "Build OK: Parasite_Eve.exe updated $after" -ForegroundColor Green
}

if ($Launch) {
    Write-Host 'Launching...'
    Start-Process powershell -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -ArgumentList @(
        '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $PSScriptRoot 'play.ps1'),
        '-BuildDir', $BuildDir, '-DebugPort', '4370')
}
