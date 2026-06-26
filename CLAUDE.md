# mmo — game-art image prompts (working guide)

Image-generation prompts for game / MMO marketplace thumbnails.
Model: `fal-ai/gpt-image-2` · 16:9 (`landscape_16_9`) · output downloaded → `cwebp -q 82` → `.webp`.
No baked price/currency/text in any image.

## Key files
- `gen-dioramas.py` — batch generator. Builds `SKEL.format(subj=...) + TAIL.format(pal=...)`,
  6-way ThreadPool, writes images to `OUT` and a prompt log. Env knobs:
  - `MMO_OUT=<dir>` — override output dir (default `img-block/`). Use for preview batches.
  - `MMO_N=<int>` — only generate the first N scenes (preview / partial regen).
- `SCENES` (in the script) — 20 `(slug, subject, palette)` tuples. Edit a row → rerun to refresh one scene.
- Image dirs: `img-block/` (block) · `img/` (pixel) · `img-nano/` (nanoblock) · `game-audio-diorama.*` (main hero).

## FINAL prompt — Block (voxel) dioramas — THE WINNER ✅
Mixed, non-uniform block scale (big structural blocks + many small detail blocks),
main-hero level of density. This is the current `SKEL` in `gen-dioramas.py`.

**SKEL** (`{subj}` = per-scene subject):
```
A richly-detailed 3D ISOMETRIC DIORAMA, a game world built out of smooth 3D BLOCKS of MIXED, NON-UNIFORM sizes — big chunky blocks for the large masses (walls, terrain, roofs) combined with many small blocks for fine detail (windows, props, characters, foliage, trim), all clean smooth cube/box shapes with NO studs and NO bumps, sitting on a glossy pedestal base: {subj}. Dense, intricate blocky build with lots of little blocks adding texture and depth, varied block scale, tilt-shift miniature feel, premium crisp studio render, main-hero level of detail.
```

**TAIL** (`{pal}` = per-scene palette, e.g. "emerald and teal"):
```
 16:9 widescreen composition. Cohesive {pal} color grade, soft studio lighting, soft long shadows, dark premium background. No text, no price, no currency.
```

### Why this version (iteration history → lessons)
- **chunky uniform blocks** → too big, monotone, toy-ish (rejected).
- **nanoblock micro-bricks** → too small, literal studs + assembly grooves (rejected).
- **mixed non-uniform blocks** → big masses + small detail blocks = the main-hero richness. ✅
- Core lesson: it's a plain **block design** (no studs/grooves); richness comes from **varied block sizes**,
  not from micro-detail. Keep "NO studs, NO bumps" + "mixed, non-uniform sizes" in the prompt.

## Other style prompts (kept for reference)
- **Pixel-art** (`prompts.md`) — isometric low-poly + retro pixel-art dioramas.
- **Nanoblock** (`prompts-nano.md`) — micro-brick studded look (kept, moved to README bottom).

## Gotchas
- The background generator detaches via `nohup python &`; the launching shell exits immediately.
  Poll `pgrep -f gen-dioramas` until it exits before trusting file counts — do NOT trust the wrapper's
  early "completed".
- When editing the script, verify the edit actually applied (a no-match `sed`/`replace` passes silently)
  BEFORE launching an expensive generation run.
- Commit with gpg signing off: `git -c commit.gpgsign=false commit -m "..."`. Never force-push.
- `FAL_KEY` comes from `secret get fal.api_key` inside the script — never inline/commit the key.
