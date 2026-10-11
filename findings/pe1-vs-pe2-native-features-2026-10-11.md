# Parasite Eve 1 native vs Parasite Eve 2 HD Remaster: feature gap (2026-10-11)

What the Parasite Eve 2 native port
([faligame/Parasite-Eve-2-HD-Remaster](https://github.com/faligame/Parasite-Eve-2-HD-Remaster))
offers, and where our Parasite Eve 1 native build stands on each. Both are psxrecomp static
recompilations. The PE2 project lists its features but publishes no source, so everything
about PE2 here comes from its README.

**Who does what**

- **Engine:** psxrecomp / recomp-ui work. mstan and Alex own this; we don't plan to build it.
- **Game (us):** PE1-specific mods in `src/mods/` and the F1 `PE Enhancements` page.
- **Assets:** HD art, fonts and upscaled video. A separate, very large content project.

**PE1 status key:** ✅ have it · ⚙️ in the engine but switched off or untested on PE1 ·
🟢 we could do it · 🟡 needs research · ❌ missing

---

## Summary

| PE2 feature | PE1 native today | Owner |
|---|---|---|
| Internal resolution up to 4K | ⚙️ `supersampling` setting exists (set to 1×) | Engine |
| PGXP (no wobble / warping) | ⚙️ `geometry_correction`, `perspective_texturing` exist (off) | Engine |
| 60 fps via 3D-only interpolation | ⚙️ partial: `frame_interpolation` blends whole frames, not per-object | Engine |
| FXAA, scanlines, window/fullscreen | ✅ antialiasing, CRT filters, window/fullscreen | Engine |
| 16:9 widescreen, per-camera framing | ❌ engine has widescreen hooks; PE1 backgrounds are 4:3 | Engine + Game + Assets |
| HD backgrounds, text boxes, fonts, FMVs, textures | ❌ | Assets (+ Engine for replacement) |
| DuckStation texture packs, hot reload | ❌ not in our engine version (newer upstream has an HD-pack API) | Engine |
| Modern analog controls (camera-relative, run at full tilt) | ✅ PE1's field code already does this | — |
| Speed x4 (hold Tab / L2) | ✅ engine turbo key (Tab) | Engine |
| Infinite HP | ✅ God mode | Game |
| Infinite MP | 🟢 PE1's Parasite Energy | Game |
| Max BP / max EXP | ✅ Add bonus points, bonus-points floor, Stats level | Game |
| Booster hotkeys with on-screen icons | ❌ ours are F1 rows | Game |
| Save-state menu, 12 slots, thumbnails | ✅ same engine feature (F7 / Select+R1) | Engine |
| Single-disc play (auto disc swap) | 🟡 PE1 discs differ only in FMVs; multi-disc support exists | Engine + Game |
| Exit in the pause menu | ⚙️ newer recomp-ui adds standard Quit / Return-to-launcher items | Engine |
| Faster door / camera loads, shorter "Now Loading" | 🟢 engine has load-acceleration and disc-speed switches for mods | Game |
| Remaster options menu | ✅ launcher + F1 runtime menu (different design) | Engine |
| Six languages, Japanese engine | ❌ US release only | Game + Engine |

---

## Graphics (engine)

The PE1 engine already has most of PE2's rendering switches; they just haven't been tried on
PE1:

- **Higher internal resolution:** `supersampling` in `settings.toml` (set to 1). Try 2–4.
- **Wobble/warp fixes:** `geometry_correction` and `perspective_texturing` (both off).
  PE2 calls this PGXP; it removes the shimmering polygons.
- **60 fps:** PE1's `frame_interpolation` crossfades whole frames. PE2's version interpolates
  only 3D geometry and leaves text, HUD and FMVs alone, which is renderer work in the engine.
- **Widescreen:** the engine has widescreen hooks, but PE1 draws over 4:3 pre-rendered
  backgrounds. Filling 16:9 needs either wider background art or per-camera cropping, like
  PE2's per-camera framing. That's engine + game + asset work, and the hardest item here.

Because these are engine settings, the first step is just testing them on PE1 and reporting
anything that breaks. That's useful input for mstan and Alex, with no engine code from us.

## HD assets (separate project)

PE2's HD backgrounds (1440×1080), HD text boxes and fonts, AI-upscaled FMVs and per-language
textures are a large art pipeline, plus engine support for swapping assets in. Our engine
version can't load texture packs; newer upstream psxrecomp has an HD-texture-pack API. Not a
mod-menu task.

## Controls

PE1 is already ahead of where PE2 started: its field movement reads the analog stick and moves
Aya relative to the camera at any angle, and full tilt runs (decomp `Scene_PlayerMovement.c`,
checked live). The d-pad gives 8-way camera-relative movement, not tank controls. On top of
that we added **Always run** (hold the run button to walk), **Run speed** and **Walk speed**.
Not checked: battle movement, and whether direction is kept across camera cuts (PE2 lists that).

## Boosters (game side, mostly done)

| PE2 booster | PE1 equivalent |
|---|---|
| Speed x4 (hold) | Engine turbo key (Tab) |
| Infinite HP | **God mode** |
| Infinite MP | 🟢 not yet: keep Aya's Parasite Energy full (needs PE's battle field mapped) |
| Max BP | **Debug > Add 1000 bonus points**, plus the bonus-points-floor package |
| Max EXP | **Stats > Level** (raising it works like a real level-up) |

PE2 toggles these with SELECT combos and shows icons on screen. Ours live in the F1 menu.
Hotkeys are possible (we read the pad), but on-screen icons would mean drawing into the frame.

## Saves, discs and menus

- **Save states:** same engine feature in both: 12 slots, thumbnails, Select+R1 (F7 on keyboard).
- **Single-disc play:** 🟡 PE2 swaps discs automatically. PE1's two discs are identical except
  for FMVs (per the decomp developer), so the same is plausible: mount the right disc, or
  serve disc 2's FMVs from disc 1. Needs the engine's multi-disc support plus game knowledge of
  when PE1 asks for disc 2.
- **Exit from the pause menu:** newer recomp-ui adds standard "Quit" / "Return to launcher"
  items with a confirm press; they arrive with an engine update. (We dropped our own exit rows.)

## Loading (game side, good candidate)

PE2 shortened door/camera loads and cut "Now Loading" screens from about 8 to 3 seconds. Our
engine already exposes the pieces to mods: `psx_mod_set_load_acceleration` (speeds up
wall-clock time during data loads without changing game timing) and `psx_mod_set_disc_speed`
(faster emulated CD). A **Faster loading** row in `PE Enhancements` could switch them on. 🟢
Needs testing for music/FMV sync, which PE2 calls out.

## Languages

PE2 ships six languages and a second engine built from the Japanese release. Our PE1 build is
the US release only. Other regions would mean recompiling their executables. Out of scope for
now.

---

## What this suggests for us

Game-side items worth doing, in order:

1. **Faster loading** toggle (engine pieces exist; needs sync testing).
2. **Infinite Parasite Energy** (find the PE field; same pattern as God mode).
3. **Booster hotkeys** for God mode / PE / speed, as an alternative to opening F1.
4. **Single-disc play** research: when PE1 asks for disc 2, and how the engine swaps.

Engine items to *test and report* rather than build: higher `supersampling`,
`geometry_correction` / `perspective_texturing`, `frame_interpolation`.
