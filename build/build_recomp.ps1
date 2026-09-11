<#
  Build a psxrecomp-based game, always syncing decomp symbols/seeds first.
  This is the "pre-build sync" path: run this instead of calling cmake directly.
  Generic across games -- the recomp checkout location comes from the bridge
  config (games/<name>/config.toml), same as sync.ps1.

  Steps:
    1. bridge sync   (decomp pull -> symbols.toml / seeds / psx_symbols.h)
    2. build the recompiler emitters  (psxrecomp-game, psxrecomp-bios)
    3. generate OpenBIOS + game C from the disc
    4. configure + build psx-runtime

  Requires on PATH: cmake >= 3.20, ninja, a C/C++ compiler (MSYS2 MinGW-w64
  or MSVC), python3. If cmake/ninja are missing, try:
      python <recomp>/psxrecomp/psxrecomp_cli.py ensure-toolchain
  which downloads a portable clang+cmake+ninja pack.

  Usage:
    powershell -ExecutionPolicy Bypass -File build\build_recomp.ps1
    ... -NoPull        # skip the decomp git pull, still regenerate + build
    ... -SkipSync      # build only
    ... -Disc 2        # generate from Disc 2 instead of Disc 1
    ... -Config games\some-other-game\config.toml
#>
param(
    [switch]$NoPull,
    [switch]$SkipSync,
    [ValidateSet('1','2')][string]$Disc = '1',
    [string]$Config = (Join-Path $PSScriptRoot '..\games\parasite-eve\config.toml')
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

function Need($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "'$name' not found on PATH. See the header of this script."
    }
}

# --- 0. resolve the target recomp checkout from the bridge config -----------
Need python
$printed = python (Join-Path $repoRoot 'bridge\decomp_bridge.py') --config $Config --print-paths
$recomp = ($printed | Where-Object { $_ -like 'recomp=*' }) -replace '^recomp=', ''
if (-not $recomp) { throw "could not resolve [paths].recomp from $Config" }

# NOTE: the disc filename is Parasite Eve-specific (unlike the bridge sync
# above, which is fully generic). Bridging a different game means changing
# this line -- or replacing it with a --disc argument -- to match its own
# disc image naming.
$cue = Join-Path $recomp "disc\Parasite Eve (USA) (Disc $Disc).cue"

# --- 1. sync -----------------------------------------------------------------
if (-not $SkipSync) {
    $syncArgs = @('-Config', $Config)
    if ($NoPull) { $syncArgs += '-NoPull' }
    & (Join-Path $PSScriptRoot 'sync.ps1') @syncArgs
    if ($LASTEXITCODE -ne 0) { throw "sync failed ($LASTEXITCODE)" }
}

if (-not (Test-Path $cue)) {
    throw "missing $cue - prepare the disc under $recomp\disc\ first"
}

Need cmake
Need ninja

Push-Location $recomp
try {
    # --- 2. emitters -------------------------------------------------------
    Write-Host "`n[2/4] building recompiler emitters..." -ForegroundColor Cyan
    cmake -S psxrecomp/recompiler -B build-recompiler -G Ninja -DCMAKE_BUILD_TYPE=Release
    cmake --build build-recompiler --target psxrecomp-game psxrecomp-bios

    # --- 3. generate C ---------------------------------------------------------
    Write-Host "`n[3/4] generating OpenBIOS + game C from Disc $Disc..." -ForegroundColor Cyan
    python psxrecomp/psxrecomp_cli.py generate --config game.toml --project-root . --disc $cue

    # --- 4. runtime ---------------------------------------------------------
    Write-Host "`n[4/4] building psx-runtime..." -ForegroundColor Cyan
    cmake -S . -B build-release -G Ninja -DCMAKE_BUILD_TYPE=Release
    cmake --build build-release --target psx-runtime

    $exe = Get-ChildItem build-release -Recurse -Filter '*.exe' |
        Where-Object { $_.Name -notmatch 'emitter|recomp-game|recomp-bios' } |
        Select-Object -First 1
    Write-Host "`ndone: $($exe.FullName)" -ForegroundColor Green
}
finally {
    Pop-Location
}
