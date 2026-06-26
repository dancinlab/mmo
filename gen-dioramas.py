#!/usr/bin/env python3
"""Generate ~20 game/MMO 3D isometric diorama images via fal-ai/gpt-image-2 -> webp.
Run: python3 gen-dioramas.py  (outputs img/<slug>.webp + prompts.md)"""
import json, os, subprocess, tempfile, urllib.request, shutil, concurrent.futures

KEY = subprocess.run(["secret", "get", "fal.api_key"], capture_output=True, text=True).stdout.strip()
OUT = os.environ.get("MMO_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "img-block")
os.makedirs(OUT, exist_ok=True)

TAIL = " 16:9 widescreen composition. Cohesive {pal} color grade, soft studio lighting, soft long shadows, dark premium background. No text, no price, no currency."
SKEL = ("A richly-detailed 3D ISOMETRIC DIORAMA, a game world built out of smooth 3D BLOCKS of MIXED, "
        "NON-UNIFORM sizes — big chunky blocks for the large masses (walls, terrain, roofs) combined with "
        "many small blocks for fine detail (windows, props, characters, foliage, trim), all clean smooth "
        "cube/box shapes with NO studs and NO bumps, sitting on a glossy pedestal base: {subj}. Dense, "
        "intricate blocky build with lots of little blocks adding texture and depth, varied block scale, "
        "tilt-shift miniature feel, premium crisp studio render, main-hero level of detail.")

# (slug, subject, palette)
SCENES = [
    ("town-square",      "a fantasy MMO town square with a fountain, market stalls, banners and tiny adventurer NPCs", "emerald and teal"),
    ("dungeon-boss",     "a torch-lit dungeon boss arena with a giant ogre, broken pillars, treasure and a hero party", "red and charcoal"),
    ("sky-island",       "a floating sky island with waterfalls, a windmill, glowing crystals and a wooden bridge", "sky-blue and mint"),
    ("pirate-cove",      "a pirate cove harbor with a docked galleon, barrels, a lighthouse and rope bridges", "ocean-teal and sand"),
    ("magic-academy",    "a magic academy library tower with floating books, spell circles and arcane lanterns", "violet and fuchsia"),
    ("blacksmith-forge", "a blacksmith forge workshop with a glowing anvil, weapon racks, a furnace and sparks", "amber and brown"),
    ("cozy-tavern",      "a cozy fantasy tavern interior with a fireplace, mugs, a bard and wooden tables", "warm neutral and black"),
    ("dragon-lair",      "a dragon's lair with a sleeping dragon coiled on a hoard of gold coins and gems", "purple and gold"),
    ("harvest-farm",     "a farming homestead diorama with crop fields, a barn, a windmill and grazing animals", "lime and forest-green"),
    ("spaceport-hangar", "a sci-fi spaceport hangar with a docked starship, robots, crates and neon gantries", "cyan and navy"),
    ("cyber-market",     "a cyberpunk street market alley with neon signs, food stalls, drones and rain puddles", "magenta and plum"),
    ("coral-ruins",      "an underwater coral ruin with sunken temple columns, glowing fish and a treasure chest", "ocean-teal and sand"),
    ("haunted-crypt",    "a haunted graveyard crypt with gravestones, fog, glowing ghosts and a gnarled tree", "graphite and lime"),
    ("arena-colosseum",  "a PvP arena colosseum with tiered stands, two gladiators, banners and torches", "tangerine and indigo"),
    ("alchemy-lab",      "an alchemy lab workbench with bubbling potions, shelves of ingredients and a cauldron", "teal and coral"),
    ("guild-hall",       "a guild hall throne room with a banner-lined hall, a throne, armor stands and a hero", "burgundy and blush"),
    ("snowy-fortress",   "a snowy mountain fortress with stone walls, watchtowers, pine trees and a frozen gate", "steel-blue and copper"),
    ("desert-oasis",     "a desert oasis caravan camp with palm trees, tents, camels and a ruined temple", "peach and terracotta"),
    ("pixel-forest",     "a pixel-art forest village with mushroom houses, a stream, lanterns and woodland critters", "emerald and teal"),
    ("overworld-map",    "a top-down RPG overworld map board with tiny mountains, towns, a winding road and a castle", "blue and orange"),
]

def gen(scene):
    slug, subj, pal = scene
    prompt = SKEL.format(subj=subj) + TAIL.format(pal=pal)
    body = json.dumps({"prompt": prompt, "image_size": "landscape_16_9", "num_images": 1}).encode()
    try:
        req = urllib.request.Request("https://fal.run/fal-ai/gpt-image-2", data=body, method="POST",
            headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.load(r)
        url = (d.get("images") or [{}])[0].get("url", "")
        if not url:
            return slug, prompt, f"❌ no url — {str(d)[:120]}"
        raw = os.path.join(tempfile.gettempdir(), f"fal_{slug}_raw")
        urllib.request.urlretrieve(url, raw)
        out = os.path.join(OUT, f"{slug}.webp")
        if shutil.which("cwebp"):
            subprocess.run(["cwebp", "-q", "82", raw, "-o", out], capture_output=True, check=True)
        else:
            shutil.copy(raw, out)
        return slug, prompt, f"✅ {os.path.getsize(out)//1024}KB"
    except Exception as e:
        return slug, prompt, f"❌ {str(e)[:120]}"

SUBSET = SCENES[:int(os.environ["MMO_N"])] if os.environ.get("MMO_N") else SCENES
rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for slug, prompt, status in ex.map(gen, SUBSET):
        print(f"{status:14} {slug}", flush=True)
        rows.append((slug, prompt, status))

# write prompts.md
lines = ["# Block (voxel) diorama prompts (game / MMO)\n",
         "20 game/MMO scenes in a shared **3D isometric chunky-BLOCK (voxel)** style (bold simple cube blocks, ",
         "tilt-shift miniature on a pedestal). Generated with `fal-ai/gpt-image-2`, 16:9.\n"]
for slug, prompt, status in rows:
    ok = "✅" in status
    lines.append(f"\n## {slug} {'' if ok else '(FAILED)'}\n")
    if ok:
        lines.append(f"![{slug}](./img-block/{slug}.webp)\n")
    lines.append(f"> {prompt}\n")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts-block.md"), "w").write("\n".join(lines))
ok = sum(1 for _,_,s in rows if "✅" in s)
print(f"=== done: {ok}/{len(rows)} ok ===", flush=True)
