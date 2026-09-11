<#
  Launch the Parasite Eve recomp with overlay auto-compilation wired up.

  Parasite Eve streams almost everything (menus, rooms, battles, cutscenes) as
  code overlays. The static recomp only covers the main EXE, so without this
  every overlay runs on the dirty-RAM interpreter -> slow menus, slow FMV, slow
  gameplay. This script:
    * puts the portable clang/gcc toolchain + git on PATH,
    * points PSX_OVERLAY_AUTOCOMPILE_CMD at compile_overlays.py so captured
      overlays get compiled to native DLLs in build-release/cache/,
    * relies on build-release/settings.toml for overlay_cache=true + idle_skip.

  First visit to each area compiles that overlay in the background (brief
  hitch); it's native and full-speed from the next visit on, and the cache
  persists across runs. A full warm-up needs a playthrough.

  This script is Parasite Eve-specific (the reference game's own launcher),
  unlike bridge/decomp_bridge.py -- game.toml, compile_overlays.py, the
  default force-interior set, and the disc/BIOS handling below are all PE
  particulars, not something the generic bridge needed to know about.

  Usage:
    powershell -ExecutionPolicy Bypass -File build\play.ps1
      -VsyncOff     also set PSX_VSYNC=0 (wall-clock pacer)
      -NoAutocompile   launch without the overlay compiler (A/B baseline)
      -Bios <path>  select a retail BIOS dump
      -Config <path>  a different games/<name>/config.toml (default: parasite-eve)
#>
param(
    [switch]$VsyncOff,
    [switch]$NoAutocompile,
    [switch]$Launcher,        # show the recomp-ui launcher instead of booting straight in
    [switch]$OpenBios,        # force OpenBIOS (ignore settings.toml [bios] / --bios) for A/B
    [string]$Bios,
    [string]$BuildDir = 'build-release',   # e.g. build-dbg for the RelWithDebInfo/debug-server build
    [int]$DebugPort = 0,                    # >0 => pass --debug-port (only the debug build listens)
    # Overlay PCs the capture classifier missed -> force compile_overlays to carve
    # them out as native fragments (stall_report [5] "HOTTEST INTERPRETED PCs").
    # Default = the RoomLib hot set found 2026-09-09.
    [string[]]$ForceInterior = @('0x80191B94','0x801927D0','0x80192E3C','0x801925D4'),
    [switch]$AllInteriors,    # see the throw below -- kept as a documented dead end, not silently ignored
    [string]$Config = (Join-Path $PSScriptRoot '..\games\parasite-eve\config.toml')
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$printed = python (Join-Path $repoRoot 'bridge\decomp_bridge.py') --config $Config --print-paths
$recomp  = ($printed | Where-Object { $_ -like 'recomp=*' }) -replace '^recomp=', ''
if (-not $recomp) { throw "could not resolve [paths].recomp from $Config" }
$exe    = Join-Path $recomp "$BuildDir\Parasite_Eve.exe"
$log    = Join-Path $PSScriptRoot ("play" + ($(if ($BuildDir -ne 'build-release') { '-' + ($BuildDir -replace '^build-','') } else { '' })) + '.log')

if (-not (Test-Path $exe)) { throw "not built yet: $exe (run build_recomp.ps1)" }

# --- MinGW GCC on PATH (overlay shards need REAL gcc; the retcomm clang pack
#     hits a hard "cannot add 'dllexport' attribute" error on every shard) ---
$mingwBin = $null
foreach ($cand in @((Join-Path $env:LOCALAPPDATA 'Programs\mingw64\bin'),
                    (Join-Path $env:USERPROFILE 'mingw64\bin'),
                    'C:\msys64\mingw64\bin', 'C:\mingw64\bin')) {
    if (Test-Path (Join-Path $cand 'gcc.exe')) { $mingwBin = $cand; break }
}
$gitCmd = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'GitHubDesktop') -Directory -Filter 'app-*' -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending | ForEach-Object { Join-Path $_.FullName 'resources\app\git\cmd' } |
    Where-Object { Test-Path (Join-Path $_ 'git.exe') } | Select-Object -First 1
$env:Path = @($mingwBin, $gitCmd, $env:Path | Where-Object { $_ }) -join ';'

# --- real Windows python (not the Store shim) ---
$py = $null
try { $py = (& py -3 -c "import sys;print(sys.executable)" 2>$null).Trim() } catch {}
if (-not $py -or -not (Test-Path $py)) {
    $py = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Recurse -Filter 'python.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $py) { throw 'no real python found (need for overlay autocompile)' }

# --- env ---
if ($VsyncOff) { $env:PSX_VSYNC = '0' }
$env:PSX_IDLE_SKIP = '1'          # also in game.toml [runtime]; harmless to reassert
$env:PSX_FPS_TELEMETRY = '2'      # log guest/host fps to the console (-> play.log)

if (-not $NoAutocompile) {
    if (-not $mingwBin) { throw 'MinGW gcc not found (expected C:\Users\...\AppData\Local\Programs\mingw64\bin)' }
    $game    = Join-Path $recomp 'game.toml'
    $gameExe = Join-Path $recomp 'psxrecomp\recompiler\build\psxrecomp-game.exe'
    $rtInc   = Join-Path $recomp 'psxrecomp\runtime\include'
    $gcc     = Join-Path $mingwBin 'gcc.exe'
    foreach ($p in @($game, $gameExe, $rtInc, $gcc)) {
        if (-not (Test-Path $p)) { throw "overlay autocompile input missing: $p" }
    }
    $env:PSX_MINGW_BIN = $mingwBin
    $env:PSX_OVERLAY_BACKEND = 'gcc'
    $env:PSX_OVERLAY_AUTOCOMPILE_CWD = $recomp
    $fi = ($ForceInterior | ForEach-Object { "--force-interior $_" }) -join ' '
    # -AllInteriors: force EVERY decomp-known overlay function via an argparse @-file
    # (compile_overlays.py patched with fromfile_prefix_chars='@'). Off by default:
    # ~1100 forced fragments is a background-compile storm that tanks speed for
    # several minutes. The targeted -ForceInterior hot set is the working config.
    $fiFile = ''
    if ($AllInteriors) {
        # This was a real experiment (force EVERY decomp-known overlay function via
        # an argparse @-file), and it was a failure -- ~1100 forced fragments is a
        # background-compile storm that tanked speed to ~0.19x for several minutes.
        # See findings/perf-investigation-log.md ("force ALL 1,131 overlay
        # interiors"). The @-file it used isn't carried into this repo on purpose;
        # -AllInteriors is kept here as a documented dead end rather than silently
        # doing nothing. Use -ForceInterior with a curated, per-area hot list instead.
        throw '-AllInteriors was a failed experiment (compile storm, ~0.19x) and ' +
              'its @-file was intentionally not kept. See findings/perf-investigation-log.md.'
    }
    $env:PSX_OVERLAY_AUTOCOMPILE_CMD = (
        '"{0}" "{1}\psxrecomp\tools\compile_overlays.py" --game-toml "{2}" ' +
        '--recompiler "{3}" --runtime-include "{4}" --cps --compiler gcc --gcc "{5}" {6} {7}'
    ) -f $py, $recomp, $game, $gameExe, $rtInc, $gcc, $fi, $fiFile
}

# --- launch ---
$args = @()
if (-not $Launcher) {
    $args += '--no-launcher'
    $env:PSX_NO_LAUNCHER = '1'
    # --no-launcher does not read [bios]/[disc] from settings.toml — pass them.
    $set = Join-Path (Split-Path $exe) 'settings.toml'
    if ($OpenBios) {
        # Force OpenBIOS: write a bios.cfg whose path does not exist. resolve_bios_for_runtime
        # then finds no usable explicit pick AND skips first-run retail discovery
        # (which only runs when bios.cfg is absent) -> falls through to bundled OpenBIOS.
        $cfg = Join-Path (Split-Path $exe) 'bios.cfg'
        if ((Test-Path $cfg) -and -not (Test-Path "$cfg.real")) { Move-Item $cfg "$cfg.real" -Force }
        Set-Content -Path $cfg -Value '__openbios_ab__' -Encoding ascii
        $Bios = $null
    }
    elseif (-not $Bios -and (Test-Path $set)) {
        $m = Select-String -Path $set -Pattern '^\s*path\s*=\s*"(.+scph.+\.bin)"' -ErrorAction SilentlyContinue
        if ($m) { $Bios = $m.Matches[0].Groups[1].Value }
    }
    $disc = Get-ChildItem (Join-Path $recomp 'disc') -Filter '*Disc 1*.cue' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($disc) { $args += @('--disc', $disc.FullName) }
}
if ($Bios) { $args += @('--bios', $Bios) }
if ($DebugPort -gt 0) { $args += @('--debug-port', "$DebugPort") }

"=== $(Get-Date -Format s) | vsyncOff=$VsyncOff autocompile=$(-not $NoAutocompile) ===" |
    Out-File -Append -Encoding utf8 $log
"AUTOCOMPILE_CMD=$($env:PSX_OVERLAY_AUTOCOMPILE_CMD)" | Out-File -Append -Encoding utf8 $log

$argStr = ($args | ForEach-Object { if ($_ -match '[ "]') { '"' + $_ + '"' } else { $_ } }) -join ' '
Push-Location (Split-Path $exe)
try {
    cmd /c "`"$exe`" $argStr >> `"$log`" 2>&1"
} finally {
    Pop-Location
}
