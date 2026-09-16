#!/usr/bin/env python3
"""Batch classifier-gap survey across a folder of PS1 memory-card saves.

Generic driver, not game-specific: everything about *where* things live
comes from the same games/<name>/config.toml decomp_bridge.py already
reads, plus the target build's own settings.toml (a psxrecomp convention,
not this game's). The only game-specific knowledge baked in is the guest
exe's filename, which is a CLI flag with a Parasite Eve default -- override
it for a different title.

What it does, once per save file found in --saves-dir:
  1. Unzip it, find the one *.mcr inside, copy it over the target build's
     configured card1.mcd (a plain 128KB raw memory-card image -- ePSXe's
     .mcr and this project's .mcd are the same format under different
     extensions). The original card1/card2 are backed up once at the start
     of the whole run, never per-save.
  2. Launch build/play.ps1 (this repo's existing generic launcher) against
     the requested build dir with a debug port enabled.
  3. Wait for the debug server to come up, then capture a fixed-length
     window with the recomp's own tools/stall_report.py.
  4. Snapshot that run's overlay_captures.json and run the recomp's own
     tools/compile_overlays.py --check against it, then this repo's own
     classifier_gap_finder.py annotate on the result -- the exact same
     manual pipeline used earlier this session, just looped.
  5. Kill the game, store everything under --out-dir/<save-name>/, and
     move to the next save.

At the end, writes SUMMARY.md ranking every save by how many un-recovered
addresses its capture found, so a human can tell at a glance which saves
are worth a closer look -- the same triage step done by hand for the
GiantWorms save, now repeatable across an arbitrary pile of them.

This does NOT drive in-game navigation (no synthetic button presses): PS1
memory cards resume from wherever the save itself was written, and this
project's own debug-server input injection is confirmed to only reach
menu navigation, not field movement (see findings/
pe-mod-movement-verification-2026-09-13.md) -- not a reliable way to
script "walk to X" regardless. Whatever a save boots into (or is left
sitting at) is exactly what gets captured.

Usage:
  python bridge/save_survey.py --config games/parasite-eve/config.toml \\
      --saves-dir "D:\\Recomp Games\\Parasite Eve Project\\pe saves" \\
      --out-dir findings/save-survey-2026-09-16 --build-dir build-dbg \\
      --debug-port 4370 --secs 60
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("error: need Python 3.11+", file=sys.stderr)
    raise SystemExit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decomp_bridge  # noqa: E402
import classifier_gap_finder  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAY_PS1 = REPO_ROOT / "build" / "play.ps1"


def log(msg: str) -> None:
    print(msg, flush=True)


def read_memcard_path(recomp: Path, build_dir: str) -> Path:
    settings = recomp / build_dir / "settings.toml"
    if not settings.is_file():
        raise SystemExit(f"error: missing {settings} (build it first)")
    data = tomllib.loads(settings.read_text(encoding="utf-8"))
    card1 = data.get("memcard", {}).get("card1")
    if not card1:
        raise SystemExit(f"error: no [memcard].card1 in {settings}")
    return Path(card1)


def find_mcr_in_zip(zpath: Path, dest_dir: Path) -> tuple[Path | None, str]:
    """Extract the .mcr and any readme from a save zip. Returns (mcr_path, readme_text)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    mcr_out = None
    readme = ""
    with zipfile.ZipFile(zpath) as zf:
        for name in zf.namelist():
            low = name.lower()
            if low.endswith(".mcr") or low.endswith(".mcd"):
                out = dest_dir / Path(name).name
                out.write_bytes(zf.read(name))
                mcr_out = out
            elif "readme" in low:
                try:
                    readme = zf.read(name).decode("utf-8", errors="replace")
                except Exception:
                    pass
    return mcr_out, readme


def wait_for_port(host: str, port: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(2)
    return False


def kill_tree(pid: int, exe_name: str) -> None:
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                    capture_output=True)
    # play.ps1 launches the guest exe via `cmd /c`, one level below the
    # powershell.exe pid above -- taskkill /T should already reach it, but
    # the exe name is the reliable fallback if that tree gets detached.
    subprocess.run(["taskkill", "/IM", exe_name, "/F"], capture_output=True)


def run_one_save(*, py: str, cfg, recomp: Path, build_dir: str, debug_port: int,
                  secs: float, boot_timeout_s: float, exe_name: str,
                  card1: Path, save_zip: Path, out_root: Path,
                  work_dir: Path) -> dict:
    save_name = save_zip.stem
    out_dir = out_root / save_name
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict = {"save": save_name, "status": "unknown"}

    mcr, readme = find_mcr_in_zip(save_zip, work_dir / save_name)
    if readme:
        (out_dir / "readme.txt").write_text(readme, encoding="utf-8")
    if not mcr:
        result["status"] = "error: no .mcr/.mcd found in zip"
        return result

    shutil.copyfile(mcr, card1)
    log(f"  [{save_name}] card1.mcd <- {mcr.name}")

    # overlay_captures.json is NOT a per-run snapshot -- the runtime's own
    # overlay_capture.c keeps it as a UNION of an immutable, additive vault
    # (capture_path.d/<content-hash>.json, "different byte variants at the
    # same load address ... survive future captures, rebuilds, and
    # regenerations" per that file's own comment) that compile_overlays.py
    # --check reads in full every time. Without this, "excluded addresses"
    # would silently be a cumulative since-vault-inception count across
    # every save this harness (or anything else) has ever run in this
    # build dir, not something specific to THIS save. Snapshot the vault's
    # file set before launching so we can report what THIS save actually
    # added, separately from the all-time cumulative count.
    vault_dir = recomp / build_dir / "overlay_captures.json.d"
    vault_before = set(p.name for p in vault_dir.glob("*.json")) if vault_dir.is_dir() else set()

    proc = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(PLAY_PS1), "-BuildDir", build_dir, "-DebugPort", str(debug_port),
         "-Config", str(cfg.config_path)],
        cwd=str(PLAY_PS1.parent),
        stdout=open(out_dir / "play.log", "w", encoding="utf-8", errors="replace"),
        stderr=subprocess.STDOUT,
    )
    try:
        log(f"  [{save_name}] launched (pid {proc.pid}), waiting for debug port {debug_port}...")
        if not wait_for_port("127.0.0.1", debug_port, boot_timeout_s):
            result["status"] = "error: debug port never came up (autocompile crash? see play.log)"
            return result

        stall_json = out_dir / "stall.json"
        r = subprocess.run(
            [py, str(recomp / "psxrecomp" / "tools" / "stall_report.py"),
             "--port", str(debug_port), "--out", str(stall_json), "run", "--secs", str(secs)],
            capture_output=True, text=True,
        )
        (out_dir / "stall_report.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode != 0:
            result["status"] = f"error: stall_report.py exit {r.returncode}"
            return result

        captures_src = recomp / build_dir / "overlay_captures.json"
        captures_dst = out_dir / "overlay_captures.json"
        if captures_src.is_file():
            shutil.copyfile(captures_src, captures_dst)

        check_txt = out_dir / "check.txt"
        game_toml = recomp / "game.toml"
        gcc_exe = recomp / "psxrecomp" / "recompiler" / "build" / "psxrecomp-game.exe"
        rt_inc = recomp / "psxrecomp" / "runtime" / "include"
        if captures_dst.is_file() and game_toml.is_file() and gcc_exe.is_file():
            r = subprocess.run(
                [py, str(recomp / "psxrecomp" / "tools" / "compile_overlays.py"),
                 "--captures", str(captures_dst), "--game-toml", str(game_toml),
                 "--recompiler", str(gcc_exe), "--runtime-include", str(rt_inc), "--check"],
                capture_output=True, text=True,
            )
            check_txt.write_text(r.stdout + r.stderr, encoding="utf-8")

            annotate_ns = argparse.Namespace(config=cfg.config_path, check_log=check_txt)
            annotate_md = out_dir / "annotate.md"
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    classifier_gap_finder.cmd_annotate(annotate_ns)
            except Exception as e:  # noqa: BLE001 - best-effort, one save shouldn't abort the batch
                buf.write(f"\n(annotate failed: {e})\n")
            annotate_md.write_text(buf.getvalue(), encoding="utf-8")

        vault_after = set(p.name for p in vault_dir.glob("*.json")) if vault_dir.is_dir() else set()
        new_variants = sorted(vault_after - vault_before)
        if new_variants:
            (out_dir / "new_vault_variants.txt").write_text("\n".join(new_variants), encoding="utf-8")

        stall_data = json.loads(stall_json.read_text(encoding="utf-8")) if stall_json.is_file() else {}
        second = stall_data.get("second", {})
        phase = second.get("phase_profile", {})
        loader = second.get("overlay_loader_status", {})
        m = re.search(r"#\s*(\d+)\s*un-recovered", (out_dir / "annotate.md").read_text(encoding="utf-8"))\
            if (out_dir / "annotate.md").is_file() else None
        result.update({
            "status": "ok",
            "interp_share": phase.get("interp_share"),
            "dispatch_native": loader.get("dispatch_native"),
            "dispatch_interp_fallback": loader.get("dispatch_interp_fallback"),
            # Cumulative since this build dir's vault was first created --
            # NOT specific to this save. See new_variants_this_save for the
            # thing that actually is.
            "excluded_addresses_cumulative": int(m.group(1)) if m else None,
            "new_variants_this_save": len(new_variants),
        })
        return result
    finally:
        kill_tree(proc.pid, exe_name)
        time.sleep(1)


def write_summary(out_root: Path, results: list[dict]) -> None:
    # Rank by what's actually specific to this save (new vault variants,
    # then windowed interp_share) -- NOT by the cumulative excluded-address
    # count, which reflects this whole build dir's history, not one save.
    ranked = sorted(
        results,
        key=lambda r: (r.get("new_variants_this_save") or -1, r.get("interp_share") or -1),
        reverse=True,
    )
    lines = [
        "# Save survey summary", "",
        "New variants and interp_share are specific to this save's capture window. "
        "Excluded-addresses is cumulative across every save run so far in this build "
        "dir's overlay-capture vault (overlay_captures.json.d/) -- see save_survey.py's "
        "module docstring / the comment above the vault_before snapshot for why that "
        "number can't be made per-save without clearing shared project history.", "",
        "| Save | Status | New variants (this save) | interp_share | Excluded addrs (cumulative) | dispatch_native | dispatch_interp_fallback |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in ranked:
        lines.append(
            f"| {r['save']} | {r['status']} | {r.get('new_variants_this_save', '')} | "
            f"{r.get('interp_share', '')} | {r.get('excluded_addresses_cumulative', '')} | "
            f"{r.get('dispatch_native', '')} | {r.get('dispatch_interp_fallback', '')} |"
        )
    (out_root / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--saves-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--build-dir", default="build-dbg")
    ap.add_argument("--debug-port", type=int, default=4370)
    ap.add_argument("--secs", type=float, default=60.0, help="capture window per save")
    ap.add_argument("--boot-timeout", type=float, default=120.0,
                     help="max seconds to wait for the debug port after launch "
                          "(autocompile of a long -ForceInterior list takes real time)")
    ap.add_argument("--exe-name", default="Parasite_Eve.exe",
                     help="guest exe filename, for the taskkill fallback (game-specific, override for another title)")
    ap.add_argument("--limit", type=int, default=None, help="only process the first N saves")
    ap.add_argument("--only", default=None, help="substring filter on save filename")
    args = ap.parse_args()

    if not PLAY_PS1.is_file():
        print(f"error: missing {PLAY_PS1}", file=sys.stderr)
        return 2

    cfg = decomp_bridge.load_config(args.config.resolve())
    card1 = read_memcard_path(cfg.recomp, args.build_dir)
    if not card1.is_file():
        print(f"error: configured card1 {card1} does not exist", file=sys.stderr)
        return 2

    saves = sorted(args.saves_dir.glob("*.zip"))
    if args.only:
        saves = [s for s in saves if args.only.lower() in s.name.lower()]
    if args.limit:
        saves = saves[: args.limit]
    if not saves:
        print(f"error: no *.zip found in {args.saves_dir}", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = args.out_dir / "_card_backup"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / card1.name
    if not backup_path.exists():
        shutil.copyfile(card1, backup_path)
        log(f"backed up original {card1.name} -> {backup_path}")

    py = sys.executable
    work_dir = args.out_dir / "_work"

    results = []
    log(f"survey: {len(saves)} save(s), {args.secs}s capture each")
    for i, save_zip in enumerate(saves, 1):
        log(f"[{i}/{len(saves)}] {save_zip.name}")
        try:
            r = run_one_save(
                py=py, cfg=cfg, recomp=cfg.recomp, build_dir=args.build_dir,
                debug_port=args.debug_port, secs=args.secs,
                boot_timeout_s=args.boot_timeout, exe_name=args.exe_name,
                card1=card1, save_zip=save_zip, out_root=args.out_dir,
                work_dir=work_dir,
            )
        except Exception as e:  # noqa: BLE001 - one bad save must not kill the batch
            r = {"save": save_zip.stem, "status": f"error: {e!r}"}
        log(f"    -> {r['status']}"
            + (f", {r.get('new_variants_this_save')} new variant(s), "
               f"interp_share={r.get('interp_share')} "
               f"(cumulative excluded so far: {r.get('excluded_addresses_cumulative')})"
               if r["status"] == "ok" else ""))
        results.append(r)

    write_summary(args.out_dir, results)
    log(f"done -> {args.out_dir / 'SUMMARY.md'}")

    log("restoring original card1.mcd")
    shutil.copyfile(backup_path, card1)

    shutil.rmtree(work_dir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
