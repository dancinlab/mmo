# mmo — game-art image prompts (working guide)

Image-generation prompts for game / MMO marketplace thumbnails.
Model: `fal-ai/gpt-image-2` · 16:9 (`landscape_16_9`) · output downloaded → `cwebp -q 82` → `.webp`.
No baked price/currency/text in any image.

## Key files
- `gen-dioramas.py` — batch generator. Builds `SKEL.format(subj=...) + TAIL.format(pal=...)`,
  6-way ThreadPool, one auto-retry per scene, writes images to `OUT` and appends a run log to
  `state/gen-log.jsonl` (ts · version · out dir · slug · status). Env knobs:
  - `MMO_OUT=<dir>` — override output dir (default `img-block/`). Use for preview batches.
  - `MMO_N=<int>` — only generate the first N scenes (preview / partial regen).
  - `MMO_ONLY=<slug,slug,...>` — only generate the named scenes (partial regen).
  - Subset runs (`MMO_N`/`MMO_ONLY`) do NOT rewrite `prompts-block.md` (would clobber other scenes).
- `scenes.json` — the `(slug, subject, palette)` rows (32 scenes). Edit a row → rerun to refresh one scene.
- Image dirs: `img-block/` (block) · `img/` (pixel) · `img-nano/` (nanoblock) · `game-audio-diorama.*` (main hero).

## Prompts live in `prompts.json` — the SSOT (versioned, NOT prose here)
The block SKEL/TAIL are versioned in [`prompts.json`](./prompts.json): `{ active, tail, versions{v1..vN} }`.
`gen-dioramas.py` loads the `active` version (override per run with `MMO_VER=v3`). To tune the look,
add a new `vN` and flip `active` — do NOT paste prompt text into this file or hardcode it in the script.

Version history — newest first (see each version's `label` / `note` / `status` in the JSON):
- **v4** + finely-subdivided characters — `active` (many tiny blocks, no big cubic Minecraft heads).
- **v3** + open-air outdoor + cinematic lighting (warm key, glowing lanterns, rim light).
- **v2** mixed non-uniform blocks — `ok` (big masses + small detail = main-hero density).
- **v1** chunky uniform blocks — `rejected` (too big, monotone, toy-ish).
- (nanoblock micro-bricks were also tried → rejected: too small, literal studs/grooves.)

Core lesson: it's a plain **block design** (no studs/grooves); richness comes from **varied block sizes**,
finely-subdivided characters, outdoor framing and dramatic lighting — not from micro-detail.

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
