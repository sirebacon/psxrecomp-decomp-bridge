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
    # Default = the RoomLib hot set found 2026-09-09, plus 0x80191200 found
    # 2026-09-11 -- same shared RoomLib region, hot specifically at the idle
    # title screen (201K insn/entry, ~87% of all interpreted instructions
    # during an idle window). Confirmed force-interior carves it fine once
    # added; it just hadn't been found yet. See findings/ in
    # psxrecomp-decomp-bridge for the stall_report data behind this list.
    [string[]]$ForceInterior = @('0x80191B94','0x801927D0','0x80192E3C','0x801925D4','0x80191200',
        # Found 2026-09-13 during the intro-FMV dirty-RAM investigation: these
        # showed up as "excluded: OBSERVED_PC_ONLY" in autocompile_status while
        # the intro FMV was playing (dirty_ram_insns climbed from ~250 to 45M+
        # over ~2 minutes of playback, then went flat the instant the menu
        # settled) -- same failure mode as the 0x80191200 entry above, same
        # 0x80191xxx RoomLib region, just not yet in this list. Not yet
        # verified this actually reduces the interpreted count -- see
        # pe-mod-movement-verification-2026-09-13.md's dirty-RAM follow-up.
        # Found 2026-09-14: these 8 were missed the first time because the
        # runtime's autocompile_status output_tail is capped and literally
        # cut off mid-word ("uded: OBSERVED_PC_ONLY") right before them.
        # Found by re-running compile_overlays.py --check --only-region
        # 0x80191000 offline (uncapped output) against this session's real
        # captures.
        '0x80191210','0x80191214','0x80191218','0x8019121C','0x80191220',
        '0x80191224','0x80191228','0x8019122C',
        '0x80191230','0x801912A4','0x801912A8','0x801912AC','0x801912B0',
        '0x801912B4','0x801912B8','0x801912BC','0x801912C0','0x801912C4',
        '0x801912C8','0x80191318','0x8019131C',
        # Found 2026-09-14, targeting the residual dirty-RAM count left
        # after the fix above (20,304 -> 101,046, still ~80-400x the
        # harmless BIOS baseline of ~257). Ran compile_overlays.py --check
        # --only-region 0x8018F000 offline against this session's real
        # overlay_captures.json (same method as the "Tested directly
        # against Parasite Eve" section of roomlib-interior-classification
        # -ai-brief.md) and got a stark result for that region:
        # executed_pcs=183, function_entry_pcs=1 -- only the dispatch entry
        # itself (0x8018F958) is classified; every other observed address
        # in the region is excluded. These 182 addresses are DIRECTLY
        # OBSERVED in real capture data, not a projection (contrast with
        # the 64-address projected list in
        # roomlib-jump-table-dispatch-classifier-gap-2026-09-14.md's
        # companion file, which is inference from this one). Two
        # contiguous clusters: 0x8018F77C-0x8018F7EC (29 addrs) and
        # 0x8018F95C-0x8018FBBC (153 addrs).
        '0x8018F77C','0x8018F780','0x8018F784','0x8018F788','0x8018F78C','0x8018F790','0x8018F794','0x8018F798','0x8018F79C','0x8018F7A0','0x8018F7A4','0x8018F7A8','0x8018F7AC','0x8018F7B0','0x8018F7B4','0x8018F7B8','0x8018F7BC','0x8018F7C0','0x8018F7C4','0x8018F7C8','0x8018F7CC','0x8018F7D0','0x8018F7D4','0x8018F7D8','0x8018F7DC','0x8018F7E0','0x8018F7E4','0x8018F7E8','0x8018F7EC',
        '0x8018F95C','0x8018F960','0x8018F964','0x8018F968','0x8018F96C','0x8018F970','0x8018F974','0x8018F978','0x8018F97C','0x8018F980','0x8018F984','0x8018F988','0x8018F98C','0x8018F990','0x8018F994','0x8018F998','0x8018F99C','0x8018F9A0','0x8018F9A4','0x8018F9A8','0x8018F9AC','0x8018F9B0','0x8018F9B4','0x8018F9B8','0x8018F9BC','0x8018F9C0','0x8018F9C4','0x8018F9C8','0x8018F9CC','0x8018F9D0','0x8018F9D4','0x8018F9D8','0x8018F9DC','0x8018F9E0','0x8018F9E4','0x8018F9E8','0x8018F9EC','0x8018F9F0','0x8018F9F4','0x8018F9F8','0x8018F9FC','0x8018FA00','0x8018FA04','0x8018FA08','0x8018FA0C','0x8018FA10','0x8018FA14','0x8018FA18','0x8018FA1C','0x8018FA20','0x8018FA24','0x8018FA28','0x8018FA2C','0x8018FA30','0x8018FA34','0x8018FA38','0x8018FA3C','0x8018FA40','0x8018FA44','0x8018FA48','0x8018FA4C','0x8018FA50','0x8018FA54','0x8018FA58','0x8018FA5C','0x8018FA60','0x8018FA64','0x8018FA68','0x8018FA6C','0x8018FA70','0x8018FA74','0x8018FA78','0x8018FA7C','0x8018FA80','0x8018FA84','0x8018FA88','0x8018FA8C','0x8018FA90','0x8018FA94','0x8018FA98','0x8018FA9C','0x8018FAA0','0x8018FAA4','0x8018FAA8','0x8018FAAC','0x8018FAB0','0x8018FAB4','0x8018FAB8','0x8018FABC','0x8018FAC0','0x8018FAC4','0x8018FAC8','0x8018FACC','0x8018FAD0','0x8018FAD4','0x8018FAD8','0x8018FADC','0x8018FAE0','0x8018FAE4','0x8018FAE8','0x8018FAEC','0x8018FAF0','0x8018FAF4','0x8018FAF8','0x8018FAFC','0x8018FB00','0x8018FB04','0x8018FB08','0x8018FB0C','0x8018FB10','0x8018FB14','0x8018FB18','0x8018FB1C','0x8018FB20','0x8018FB24','0x8018FB28','0x8018FB2C','0x8018FB30','0x8018FB34','0x8018FB38','0x8018FB3C','0x8018FB40','0x8018FB44','0x8018FB48','0x8018FB4C','0x8018FB50','0x8018FB54','0x8018FB58','0x8018FB5C','0x8018FB60','0x8018FB64','0x8018FB68','0x8018FB6C','0x8018FB70','0x8018FB74','0x8018FB78','0x8018FB7C','0x8018FB80','0x8018FB84','0x8018FB88','0x8018FB8C','0x8018FB90','0x8018FB94','0x8018FB98','0x8018FB9C','0x8018FBA0','0x8018FBA4','0x8018FBA8','0x8018FBAC','0x8018FBB0','0x8018FBB4','0x8018FBB8','0x8018FBBC',
        # Found 2026-09-16: psxrecomp-decomp-bridge's classifier_gap_finder.py
        # scan-shared-libs auto-discovered RoomLib_HandlerB.inc and
        # RoomLib_HandlerC.inc as AT-RISK templates (a switch statement in
        # the shared body, same shape as ROOMLIB_STATE_DISPATCH_VARIANT2
        # above), with zero prior knowledge of either being bad. These are
        # real addresses that showed bare "excluded: OBSERVED_PC_ONLY" in a
        # real compile_overlays.py --check transcript (genuine gameplay
        # capture, not synthetic) -- not a computed prediction.
        # NOT YET LIVE-VERIFIED, unlike every other entry in this list: a
        # second --check pass with --force-interior added for these
        # addresses did NOT show the "; isolated fragment demand retained"
        # success marker the already-proven 0x80191xxx entries above show
        # when they succeed -- but neither did most of THOSE already-working
        # addresses on this same limited capture (only 4 overlay regions,
        # a short session), so this looks like a capture-richness limit on
        # re-verification, not evidence the fix is wrong. Needs an actual
        # live launch + play + dirty-RAM before/after to confirm, the same
        # way every entry above this comment was actually confirmed. See
        # psxrecomp-decomp-bridge/findings/
        # roomlib-handlerb-handlerc-confirmed-2026-09-16.md.
        # RoomLib_HandlerB (4 live instances, offsets 0x0-0x2C observed):
        '0x80191D70','0x80191D8C','0x80191D90',
        '0x80191E0C','0x80191E10','0x80191E14',
        '0x80191ED8','0x80191EDC','0x80191EE0','0x80191EE4','0x80191EE8',
        '0x80191EEC','0x80191EF0','0x80191EF4','0x80191EF8','0x80191EFC','0x80191F00',
        '0x801929BC','0x801929C0',
        # RoomLib_HandlerC (1 live instance, offsets 0x0/0x4/0x8 observed):
        '0x801929EC','0x801929F0','0x801929F4'),
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
