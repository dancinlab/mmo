#!/usr/bin/env python3
"""Generate ~20 game/MMO 3D isometric diorama images via fal-ai/gpt-image-2 -> webp.
Run: python3 gen-dioramas.py  (outputs img/<slug>.webp + prompts.md)"""
import json, os, subprocess, tempfile, time, urllib.request, shutil, concurrent.futures

KEY = subprocess.run(["secret", "get", "fal.api_key"], capture_output=True, text=True).stdout.strip()
OUT = os.environ.get("MMO_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "img-block")
os.makedirs(OUT, exist_ok=True)

# Prompt SKEL/TAIL live in prompts.json (versioned v1..vN). Pick a version with MMO_VER, else the "active" one.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.json"), encoding="utf-8") as f:
    PROMPTS = json.load(f)
VER = os.environ.get("MMO_VER") or PROMPTS["active"]
TAIL = PROMPTS["tail"]
SKEL = PROMPTS["versions"][VER]["skel"]
print(f"prompt version: {VER} — {PROMPTS['versions'][VER]['label']}", flush=True)

# (slug, subject, palette) rows live in scenes.json — edit there, rerun to refresh
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes.json"), encoding="utf-8") as f:
    SCENES = [tuple(row) for row in json.load(f)]

def gen(scene):
    slug, subj, pal = scene
    prompt = SKEL.format(subj=subj) + TAIL.format(pal=pal)
    body = json.dumps({"prompt": prompt, "image_size": "landscape_16_9", "num_images": 1}).encode()
    status = "❌ not attempted"
    for attempt in range(2):  # one retry — a 20-scene batch usually has 1-2 transient failures
        try:
            req = urllib.request.Request("https://fal.run/fal-ai/gpt-image-2", data=body, method="POST",
                headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            url = (d.get("images") or [{}])[0].get("url", "")
            if not url:
                raise RuntimeError(f"no url — {str(d)[:120]}")
            raw = os.path.join(tempfile.gettempdir(), f"fal_{slug}_raw")
            urllib.request.urlretrieve(url, raw)
            out = os.path.join(OUT, f"{slug}.webp")
            if shutil.which("cwebp"):
                subprocess.run(["cwebp", "-q", "82", raw, "-o", out], capture_output=True, check=True)
            else:
                shutil.copy(raw, out)
            return slug, prompt, f"✅ {os.path.getsize(out)//1024}KB"
        except Exception as e:
            status = f"❌ {str(e)[:120]}"
            time.sleep(5)
    return slug, prompt, status

SUBSET = SCENES[:int(os.environ["MMO_N"])] if os.environ.get("MMO_N") else SCENES
if os.environ.get("MMO_ONLY"):  # comma-joined slugs — partial regen without touching the rest
    only = set(os.environ["MMO_ONLY"].split(","))
    SUBSET = [s for s in SUBSET if s[0] in only]
rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for slug, prompt, status in ex.map(gen, SUBSET):
        print(f"{status:14} {slug}", flush=True)
        rows.append((slug, prompt, status))

# append run log (state/gen-log.jsonl) — which image came from which version, when
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state", "gen-log.jsonl")
os.makedirs(os.path.dirname(LOG), exist_ok=True)
with open(LOG, "a", encoding="utf-8") as lf:
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    for slug, prompt, status in rows:
        lf.write(json.dumps({"ts": ts, "ver": VER, "out": OUT, "slug": slug, "status": status}, ensure_ascii=False) + "\n")

# write prompts.md — full-set runs only (a subset run would clobber the other scenes' sections)
if not (os.environ.get("MMO_N") or os.environ.get("MMO_ONLY")):
    lines = ["# Block (voxel) diorama prompts (game / MMO)\n",
             f"{len(rows)} game/MMO scenes in a shared **3D isometric chunky-BLOCK (voxel)** style (bold simple cube blocks, ",
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
