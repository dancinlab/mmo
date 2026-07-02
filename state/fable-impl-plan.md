# fable full implementation plan — mmo 3D asset program · 2026-07-02 · sidecar fable (claude-fable-5, headless, plan-only)

# mmo 블록 디오라마 → 3D 게임 에셋 — FULL 구현 계획 (plan-only)

> 근거: `state/fable-3d-assets.md`(전략 SSOT) · `scenes.json`(32씬) · `prompts.json` v4 룩.
> 본 문서는 계획만 기술하며 어떤 파일도 생성/수정하지 않았다. 아래의 모든 경로·수치·파라미터는 **확정값**이다 — 실행자는 재결정 없이 그대로 수행한다.

---

## 1. PROGRAM OVERVIEW

**목표.** `img-block/`의 2D 블록 디오라마 룩(v4: 비균일 블록 + 세분화 캐릭터 + 시네마틱 조명)을 실제 3D 게임 에셋으로 성립시킨다. 산출물은 ① 재사용 가능한 GLB 킷 라이브러리(~400피스) ② 씬당 레이아웃 JSON + 베이크된 씬 GLB ③ 웹(three.js) 인터랙티브 프리뷰 ④ Cycles 오프라인 스틸컷 썸네일(webp) ⑤ Godot 4 런타임 호환 확인.

**범위.** M1 = pet-ranch 버티컬 슬라이스(파이프라인 전 구간 최소 물량 관통) → M2+ = 바이옴별 킷 재사용으로 32씬 전체 스케일아웃.

**비목표(non-goals).** 게임플레이 로직·네트워크·사운드 · 씬당 3종(idle/walk/emote) 초과 애니메이션 · PBR 텍스처 맵 · 모바일 최적화 · AI image-to-3D 산출물의 최종 에셋 사용(블록아웃 참고용으로만) · 물/불의 물리 시뮬레이션(전부 셰이더/카드) · 2D 이미지 파이프라인(`gen-dioramas.py`) 변경.

**프로그램 전체 DoD.**
1. `tools/vox2blocks.py`·`tools/palette_gen.py` 골든 테스트 전부 green (`pytest tests/` exit 0).
2. 32씬 각각: `scenes3d/<slug>.layout.json`(스키마 검증 통과) + `scenes3d/<slug>.baked.glb`(gltf-validator 에러 0, 씬 tri ≤ 500k) 존재.
3. 32씬 각각: 뷰어 A/B 스코어(§6 기준: hue-histogram corr ≥ 0.6 AND 체크리스트 ≥ 4/5) 통과 기록이 `state/3d/ab/<slug>/`에 존재.
4. 32씬 각각: Cycles 스틸컷 `renders3d/<slug>.webp`(1920×1080, `cwebp -q 82`) 존재.
5. Godot 4.3 headless import가 킷 전체 + 대표 씬 5개에서 에러 0.
6. 전 마일스톤 게이트 증거가 `state/3d/gate-M*.md`로 기록됨.

**핵심 성립 조건(전략 SSOT 결론).** 균일 복셀 저작 → greedy box decomposition(병합 상한 8) → 챔퍼 박스 집합 GLB. 이 변환기(`vox2blocks`) 없이는 룩이 성립하지 않으므로 M0 최우선.

---

## 2. MILESTONES

| 마일스톤 | 이름 | 진입 기준 | 종료 기준(게이트) | 산출물 | 공수(인일) |
|---|---|---|---|---|---|
| **M0** | 툴링 기반 + 그리드 바이블 | 본 계획 승인 | `pytest` 전부 green · 그리드 바이블 문서 확정 · 32씬 팔레트 전량 생성 성공 | `tools/vox2blocks.py`, `tools/palette_gen.py`, `scenes3d/layout.schema.json`, `state/3d/grid-bible.md`, `palettes/*(32)` | **5** |
| **M1** | pet-ranch 버티컬 슬라이스 | M0 게이트 통과 | A/B 스코어 통과 · baked GLB validator 0에러 · Godot 임포트 0에러 · Cycles 스틸 1장 | 킷 ~22에셋 GLB · `scenes3d/pet-ranch.layout.json` · `viewer/` · 베이크 배치 · idle 애니 1종 · `state/3d/gate-M1.md` | **13** |
| **M2** | 자연/전원 바이옴 (7씬) + 베이스·자연 킷 완성 | M1 게이트 · 그리드 바이블 동결 | 7씬 전부 §6 게이트 통과 · 킷 택소노미 1차 감사 완료 | harvest-farm, housing-garden, pixel-forest, fishing-pier, sky-island, desert-oasis, world-tree-village | **28** |
| **M3** | 중세 판타지 바이옴 (8씬) + 중세 건축 킷 | M2 게이트 | 8씬 게이트 통과 · 군중 인스턴싱(town-square) 60fps@web 확인 | town-square, auction-plaza, blacksmith-forge, cozy-tavern, guild-hall, arena-colosseum, snowy-fortress, siege-battle | **30** |
| **M4** | 던전/마법 바이옴 (9씬) + FX/셰이더 킷 | M3 게이트 | 9씬 게이트 통과 · FX 10종(용암·포탈·안개 등) 셰이더 완성 | dungeon-boss, dragon-lair, haunted-crypt, lava-mines, mushroom-cavern, coral-ruins, magic-academy, alchemy-lab, rune-portal-hub | **32** |
| **M5** | 동양/축제 + SF + 특수 (7씬) | M4 게이트 | 7씬 게이트 통과 · 히어로 원오프(갤리온·스타쉽·비행선) 완성 | hotspring-ryokan, fireworks-festival, spaceport-hangar, cyber-market, pirate-cove, airship-deck, overworld-map | **28** |
| **M6** | 마켓플레이스 산출 파이프 + 최종 QA | 32씬 게이트 통과 | 프로그램 DoD 1–6 전부 충족 | 턴테이블 렌더 파이프 · 32 썸네일 webp · 최종 감사 리포트 `state/3d/final-audit.md` | **8** |

**합계 ≈ 144인일** (1인 기준 약 29주; §7의 병렬화로 캘린더 단축 가능). M1 종료 시점이 최대 리스크(조명 매칭 갭) 측정점 — 여기서 A/B 스코어가 기준 미달이면 §9-R1 완화 경로로 분기.

---

## 3. WORK BREAKDOWN (마일스톤별 태스크)

표기: **입력 → 출력 · 툴 · 수용 기준 · 시간**. 순서 = 실행 순서(의존성 반영).

### M0 — 툴링 기반 (총 ~39h)

| # | 태스크 | 입력 | 출력 | 툴 | 수용 기준 | h |
|---|---|---|---|---|---|---|
| 0.1 | 환경 셋업 | §8 매트릭스 | venv + 설치 확인 로그 | `python3 -m venv`, `pip`, brew | `python -c "import trimesh, pygltflib, numpy"` exit 0 · `blender --version` = 4.2.x · `npx gltf-validator --version` 동작 | 3 |
| 0.2 | 블록 그리드 바이블 작성 | §5의 확정값 | `state/3d/grid-bible.md` | 문서 | §5 표의 전 항목이 수치로 기재, TBD 0건 | 2 |
| 0.3 | .vox 테스트 픽스처 생성기 | vox 포맷 스펙 | `tests/fixtures/make_fixtures.py` → T1~T10용 .vox 바이트 | Python(struct) | MagicaVoxel에서 픽스처 3개 수동 오픈 시 정상 표시 | 2 |
| 0.4 | `vox2blocks` 파서 | .vox 스펙(MAIN/SIZE/XYZI/RGBA/MATL/nTRN/nGRP/nSHP) | `read_vox()` | Python | T7(멀티모델), T9(빈 모델) 통과 | 6 |
| 0.5 | greedy box decomposition | 파서 출력 | `greedy_boxes()` (cap·jitter·seed) | Python+numpy | T1~T4 박스 수 일치 · 10⁶ 복셀 < 10s | 6 |
| 0.6 | 챔퍼 메시 + GLB 라이터 | 박스 리스트 | `chamfer_box_mesh()`, `write_glb()` | pygltflib | T1: 44tri/24vert · T5 emissive 머티리얼 분리 · T8 결정성 | 6 |
| 0.7 | 골든 테스트 완성 | 0.4–0.6 | `tests/test_vox2blocks.py` (T1–T10) | pytest | 전부 green, 커버리지: 파서·분해·메시·CLI 4구획 각 ≥1 테스트 | 4 |
| 0.8 | `palette_gen` | `scenes.json` | `tools/palette_gen.py` + `palettes/<slug>.{png,json}` ×32 | Python | 32씬 전량 파싱 성공(미지 색명 0) · 결정성 테스트 green | 6 |
| 0.9 | 레이아웃 스키마 + 검증기 | §4-3 설계 | `scenes3d/layout.schema.json` + `tools/validate_layout.py` | JSON Schema, check-jsonschema | 유효/무효 샘플 각 3개가 기대대로 pass/fail | 4 |

### M1 — pet-ranch 버티컬 슬라이스 (총 ~103h)

| # | 태스크 | 입력 | 출력 | 툴 | 수용 기준 | h |
|---|---|---|---|---|---|---|
| 1.1 | 플레이스홀더 생성기 | 킷 스펙(§5 표) | `tools/make_placeholder.py` → `kits/_placeholder/*.glb` 22개 | Python(vox2blocks 재사용) | 각 GLB의 AABB가 §5 스펙 그리드 ±1u 이내 | 4 |
| 1.2 | 에셋 매니페스트 | 킷 스펙 | `kits/manifest.json` (논리 id → glb 경로 + tri 예산 클래스) | 수기 JSON | validate 스크립트 통과, 22 엔트리 | 1 |
| 1.3 | three.js 뷰어 | 플레이스홀더 + 레이아웃 | `viewer/` (§4-4 파일 구성) | three.js r168 | 플레이스홀더 씬이 60fps 로드 · 포스트 스택 5단 전부 토글 가능 | 12 |
| 1.4 | pet-ranch 레이아웃 초안 | 2D 레퍼런스 `img-block/pet-ranch.webp` | `scenes3d/pet-ranch.layout.json` (플레이스홀더 참조) | 수기 + validate | 스키마 통과 · 뷰어에서 구도가 2D와 러프 일치(수동 확인) | 4 |
| 1.5 | 팔레트 락 + MagicaVoxel 셋업 | `palettes/pet-ranch.png` | MagicaVoxel에 팔레트 로드된 작업 파일 | MagicaVoxel(GUI, 사람) | 팔레트 16색이 §5 인덱스 레이아웃과 일치 | 1 |
| 1.6 | 킷 저작 1차(소형→대형) | §5 저작 순서 | `vox/pet-ranch/*.vox` 20종 | MagicaVoxel(사람) | 각 에셋이 스펙 그리드 이내, 팔레트 외 색 사용 0 | 32 |
| 1.7 | 변환 배치 | 1.6 + vox2blocks | `kits/nature/*.glb` 등 | `tools/build_kits.sh`(vox2blocks 루프) | gltf-validator 에러 0 · `tools/check_budget.py` 전 에셋 예산 내 | 3 |
| 1.8 | 대형 드래곤(세미 스컬프트) | 2D 레퍼런스 | `vox/pet-ranch/dragon_large.vox` → GLB | Blender 스컬프트→복셀 리메시→MagicaVoxel 보정(사람) | 32×24×28 그리드 내 · 실루엣 수동 승인 | 8 |
| 1.9 | NPC 리깅 + idle 애니 | NPC 파트 GLB | `kits/chars/npc_caretaker.rig.glb` (본 14개, idle 1) | Blender(강체 블록 스키닝, 12fps 스텝) | 재생 시 블록 변형(쉬어링) 0 — 각 버텍스 웨이트가 정확히 1본 100% | 8 |
| 1.10 | Blender 어셈블+베이크 배치 | 레이아웃 JSON + 킷 | `tools/blender/assemble_bake.py` → `scenes3d/pet-ranch.baked.glb` + PNG | `blender -b`(§4-5) | 무인 실행 exit 0 · baked GLB validator 0에러 | 8 |
| 1.11 | 조명 A/B 수렴 | 뷰어 + `img-block/pet-ranch.webp` | 수렴된 env 파라미터(레이아웃에 반영) + `state/3d/ab/pet-ranch/` | 뷰어 compare 모드 + `tools/ab_score.py` | §6 G3 기준 통과 | 12 |
| 1.12 | Cycles 스틸컷 | baked 씬 | `renders3d/pet-ranch.webp` | blender -b + cwebp | 1920×1080 · 룩매치 루브릭 ≥ 4/5(§6) | 4 |
| 1.13 | Godot 스모크 | 킷 + baked GLB | `godot-smoke/` 프로젝트 import 로그 | Godot 4.3 `--headless --import` | import 에러 0 · GUI 1회 육안: emissive/버텍스컬러 표시 정상 | 3 |
| 1.14 | 게이트 기록 | 1.1–1.13 증거 | `state/3d/gate-M1.md` | 문서 | DoD 체크리스트 전 항목 evidence 링크 | 3 |

### M2~M5 — 씬 스케일아웃 (씬당 반복 태스크 템플릿)

각 씬은 동일 6단계: ① 신규 킷 갭 목록화(레퍼런스 정독 → `kits/manifest.json` 대비 diff, 1h) ② 신규 킷 저작+변환(피스당 ~1.2h) ③ 히어로 원오프 저작(개당 ~4h) ④ 레이아웃 JSON 작성(3h) ⑤ 베이크+A/B 수렴(4h) ⑥ QA 게이트+기록(2h). 씬별 합계는 §7의 한계 공수 모델을 따른다. 마일스톤 공통 선행 태스크: 바이옴 건축 킷 벌크 저작(M3: 30피스 ~4d · M4: 동굴/마법 킷 + FX 셰이더 10종 ~6d · M5: 히어로 원오프 3종 ~5d).

### M6 — 마켓 산출 파이프 (총 ~60h)
① 턴테이블 렌더 스크립트(`tools/blender/turntable.py`, 36프레임 orbit → webp 시퀀스, 8h) ② 32씬 썸네일 일괄 Cycles 렌더(배치 무인, 16h 머신타임/4h 인력) ③ `state/gen-log.jsonl` 관행에 맞춘 `state/3d/render-log.jsonl` 통합(4h) ④ 최종 감사: DoD 1–6 전수 검사 + `state/3d/final-audit.md`(8h) ⑤ 킷 라이브러리 재판매 패키징 검토(라이선스 표기, 4h).

---

## 4. FILE-LEVEL DESIGN

### 4-1. `tools/vox2blocks.py` (단일 파일 CLI, ~600줄)

**데이터 타입**
```
@dataclass VoxModel:  name:str · size:(x,y,z) · voxels:np.ndarray[N,4](x,y,z,color_idx)
                      · palette:np.ndarray[256,4] · emissive_idx:set[int] · transform:4×4
@dataclass Box:       lo:(x,y,z) · hi:(x,y,z) · color_idx:int
```

**함수 맵 (호출 순서대로)**
| 함수 | 역할 | 핵심 규칙 |
|---|---|---|
| `read_vox(path) -> list[VoxModel]` | RIFF 청크 워커: `MAIN`→`PACK`/`SIZE`+`XYZI` 쌍, `RGBA`(없으면 기본 팔레트), `MATL`(`_emit`>0 → emissive_idx 추가), `nTRN/nGRP/nSHP` 씬그래프 → 모델별 월드 변환 | 멀티모델 지원이 1급 기능 (파트별 캐릭터 저작에 필수) |
| `cull_hidden(voxels, size)` | 6면 전부 이웃으로 막힌 복셀 제거 | `--keep-hidden`으로 비활성 가능 |
| `greedy_boxes(voxels, cap, seed, jitter=0.15)` | 색상별 점유 그리드에서 결정적 스캔 순서(z→y→x)로 미점유 복셀 발견 → x축 최대 성장 → y → z, 각 축 `cap` 이하 & 완전 충만 조건 | seeded RNG로 확률 0.15로 성장폭 −1 (줄눈 단조 방지). `--no-jitter`로 테스트 시 비활성. 무제한 병합 금지 — cap 기본 (8,8,8) |
| `chamfer_box_mesh(box, bevel, unit)` | 24 vert / 44 tri 챔퍼 박스: 6면(12tri) + 12엣지 쿼드(24tri) + 8코너(8tri), 면별 플랫 노멀 | `bevel_eff = min(bevel, 0.45 * min_dim)` |
| `assemble(models, args)` | 모델별 박스 → 최대 2 프리미티브(일반/emissive)로 배칭, `COLOR_0` 버텍스 컬러(팔레트 sRGB→linear) | 노드명 = vox 모델명 |
| `write_glb(gltf, out)` | pygltflib 직렬화 | emissive 머티리얼에 `KHR_materials_emissive_strength` |
| `main(argv)` | argparse + 통계 리포트 | exit 0 정상 / 2 파싱오류 / 3 빈모델 / 4 예산초과 |

**CLI 표면**
```
vox2blocks.py IN.vox -o OUT.glb
  --cap 8[,8,4]           # 축별 병합 상한 (기본 8,8,8)
  --bevel 0.08            # 챔퍼 폭(복셀 단위, 기본 0.08)
  --unit 0.1              # 1복셀 = 0.1m (GLB는 미터)
  --seed auto|<int>       # auto = slug 해시. 결정성 보장
  --no-jitter
  --emissive-idx 15,16    # 팔레트 인덱스 → emissive 머티리얼
  --emissive-strength 5.0
  --keep-hidden
  --pivot bottom-center|origin   # 기본 bottom-center
  --max-tri <int>         # 초과 시 exit 4
  --stats --json-report OUT.json # tri/vert/box 수, 예산 검사용
```

**골든 테스트 (`tests/test_vox2blocks.py`, 픽스처는 programmatic .vox 바이트)**
| ID | 입력 | 기대값 |
|---|---|---|
| T1 | 8×4×2 단색 솔리드 | 박스 1 · 44 tri · 24 vert · AABB (0.8, 0.4, 0.2)m |
| T2 | 16×1×1 단색, cap 8 | 박스 2 · 88 tri |
| T3 | 9×9×9 단색, cap 8, `--no-jitter` | 박스 8 (각 축 8+1 분할) |
| T4 | 2복셀 인접 이색 | 박스 2 (색 경계 병합 금지) |
| T5 | 팔레트 idx 15 복셀 1 + 일반 1 | 머티리얼 2 · emissive_strength = 5.0 |
| T6 | 3×3×3 솔리드 | `cull_hidden` 후 복셀 26개 |
| T7 | 2모델 .vox (nTRN 이동 포함) | GLB 노드 2, 변환 반영된 AABB |
| T8 | 동일 입력+seed 2회 실행 | GLB 바이트 동일 (타임스탬프 미기록) |
| T9 | XYZI 0복셀 | exit 3 |
| T10 | `--pivot bottom-center` | min.y = 0, x/z 센터링 |

**엣지 케이스 처리 규칙**
- **멀티모델 .vox**: nGRP 계층 그대로 GLB 노드 트리로. 이름 없는 모델은 `model_<i>`.
- **팔레트 >256 / MATL 인덱스 초과**: .vox 포맷상 256 고정 — 범위 밖 MATL 인덱스는 경고 후 무시 (exit 0 유지).
- **emissive 경로**: `--emissive-idx` ∪ MATL `_emit`>0 의 합집합. emissive 박스는 병합 시 일반 박스와 섞지 않음(머티리얼 경계 = 병합 경계).
- 256³ 초과 월드(MagicaVoxel 분할 SHP) → 씬그래프 변환으로 봉합. 1복셀 모델 → 박스 1, bevel 클램프. bevel ≥ min_dim/2 → 0.45배 클램프.

### 4-2. `tools/palette_gen.py` (~250줄)

**알고리즘 (확정): OKLCH 앵커-램프 방식.**
1. `NAMED_COLORS`: scenes.json에 등장하는 전 색명(약 50개: mint, butter-yellow, emerald, teal, red, charcoal, sky-blue, ocean-teal, sand, violet, fuchsia, amber, brown, warm-neutral, black, purple, gold, lime, forest-green, cyan, navy, magenta, plum, graphite, tangerine, indigo, coral, burgundy, blush, steel-blue, copper, peach, terracotta, blue, orange, aqua, driftwood-brown, ivory, azure, neon-teal, pastel-pink, sage, royal-blue, brass, jade, cream, deep-purple, midnight-blue, steel-grey, flame-orange) → hex 하드코딩 사전.
2. `parse_palette_string("mint and butter-yellow")` → `" and "` 분리, 하이픈/공백 정규화 → (anchorA, anchorB). 미지 색명은 지원 목록을 출력하며 exit 2.
3. `ramp(anchor, n=5)`: OKLCH에서 hue 고정, L을 0.35→0.85 등분, C는 중간에서 최대인 종형, 그림자 쪽 hue −8°(냉색), 밝은 쪽 +8°(난색). sRGB 감뭇 밖은 C 축소 클램프.
4. **16색 고정 레이아웃**: idx 1–5 = A램프(어둠→밝음) · 6–10 = B램프 · 11 = charcoal `#26262B` · 12 = cream `#F1E8D7` · 13 = wood `#8A5A3B` · 14 = stone `#9A9AA2` · 15 = emissive-warm `#FFC46B` · 16 = emissive-cool `#8FE9FF` (11–16은 전 씬 공통 고정 — 킷 간 색 호환의 근거).

**출력**: `palettes/<slug>.png`(16×1 PNG — MagicaVoxel 팔레트 임포트용) + `palettes/<slug>.json`(`{slug, anchors:{a,b}, colors:[{idx,hex,oklch,role}]}`).
**CLI**: `palette_gen.py --scenes scenes.json [--slug pet-ranch | --all] --out palettes/`.
**테스트**: ① 32씬 전량 파싱 성공(scenes.json을 직접 순회) ② "mint and butter-yellow" → 결정적 16 hex 스냅샷 일치 ③ 고정 슬롯 11–16 불변 검증 ④ 감뭇 클램프(고채도 anchor) 시 유효 sRGB.

### 4-3. 씬 레이아웃 스키마 — `scenes3d/<slug>.layout.json`

```jsonc
{
  "schema": "mmo.layout/1",
  "slug": "pet-ranch",
  "unit": 0.1,                          // m per grid unit — 그리드 바이블과 일치 필수
  "palette": "palettes/pet-ranch.json",
  "pedestal": { "size": [144, 6, 144], "material": "pedestal" },   // 그리드 단위
  "env": {
    "key_light":  { "color": "#FFD9A6", "intensity": 3.0, "azimuth_deg": 225, "elevation_deg": 25, "shadow": true },
    "rim_light":  { "color": "#9FD8E8", "intensity": 1.2, "azimuth_deg": 30,  "elevation_deg": 55, "shadow": false },
    "ambient":    { "sky": "#3A4A5A", "ground": "#1A1616", "intensity": 0.35 },
    "background": { "top": "#101018", "bottom": "#000000" },
    "post": { "bloom": {"threshold":1.0,"intensity":0.8}, "tilt_shift": {"focus_y":0.45,"band":0.35,"max_blur_px":3},
              "vignette": 0.25, "saturation": 0.10, "tonemap": "ACES" }
  },
  "camera": { "fov_deg": 25, "yaw_deg": 45, "pitch_deg": 35, "distance_u": 260, "target_u": [64, 12, 64],
              "limits": { "pitch_min": 15, "pitch_max": 55, "zoom_min_u": 180, "zoom_max_u": 400 } },
  "instances": [
    { "id": "barn_01", "asset": "nature/barn",       // manifest 논리 id — 경로 아님
      "pos_u": [40, 0, 30], "rot_y": 90,
      "emissive": [{ "slot": "window", "color": "#FFD9A0", "strength": 5 }] }
  ],
  "point_lights": [ { "pos_u": [44,10,32], "color": "#FFC46B", "intensity": 8, "radius_u": 30 } ]  // 씬당 ≤ 6
}
```

**검증 규칙 (`tools/validate_layout.py` = JSON Schema + 추가 코드 검사)**: ① `pos_u` 정수(그리드 스냅) ② `rot_y ∈ {0,90,180,270}` (블록 문법 — 임의 회전 금지) ③ scale 필드 자체를 불허(크기 변형은 별도 에셋으로) ④ `asset`이 `kits/manifest.json`에 존재 ⑤ `id` 유일 ⑥ `point_lights` ≤ 6 ⑦ `unit`이 grid-bible 값(0.1)과 일치 ⑧ emissive `slot`명이 해당 GLB의 emissive 머티리얼 이름과 일치(코드 검사).

### 4-4. `viewer/` — three.js 뷰어

**파일 구성** (빌드 스텝 없음 — importmap + 고정 CDN, `python3 -m http.server 8000`으로 서빙):
| 파일 | 역할 |
|---|---|
| `index.html` | importmap: `three@0.168.0`, `postprocessing@2.19.x` 고정 · 캔버스 + compare UI |
| `main.js` | 부트스트랩 · 리사이즈 · 렌더 루프 · `?slug=pet-ranch` 쿼리로 레이아웃 선택 |
| `loader.js` | layout.json fetch → manifest 해석 → GLTFLoader · 동일 asset 4회 이상 참조 시 `InstancedMesh` 자동 전환 |
| `lights.js` | env → key 디렉셔널(그림자 2048 PCFSoft) + rim 디렉셔널(무그림자) + HemisphereLight + point ≤6 |
| `pedestal.js` | `Reflector` 평면 반사 + roughness 0.05 블렌드 · 저사양 폴백: 다크 큐브맵 근사 |
| `post.js` | EffectComposer: Render → SelectiveBloom(emissive 레이어만, threshold 1.0) → TiltShift(수직 그라디언트 블러 — 물리 DOF 금지) → Vignette → HueSaturation(+10% sat) → ACES 출력 |
| `compare.js` | A/B 모드: `../img-block/<slug>.webp` 로드 → ① 좌우 나란히 ② 50% 와이프 슬라이더 · 스크린샷 버튼 → `<slug>-viewer.png` 다운로드 |
| `gui.js` | lil-gui — env 전 파라미터 실시간 조정 + "Export env JSON" 버튼(클립보드, layout에 붙여넣기용) |

**카메라 제약**: OrbitControls · pan 비활성 · polar = 90°−pitch, pitch [15°, 55°] 클램프(등각 35° ± 20°) · fov 25°(망원 — 미니어처 감) · 줌 한계는 layout `limits` · damping 0.08.
**렌더 파이프**: `outputColorSpace = SRGB` · 톤매핑은 포스트 스택에서만(이중 적용 금지) · 배경 = 지오메트리 없는 수직 그라디언트(layout `background`).

### 4-5. 헤드리스 베이크 배치 — `tools/blender/assemble_bake.py`

**호출**: `blender -b -P tools/blender/assemble_bake.py -- --layout scenes3d/<slug>.layout.json --kits kits/ --out scenes3d/<slug>.baked.glb --still renders3d/<slug>.png --samples 256 --bake-res 2048`

**내부 단계**: ① 씬 클리어 → layout 파싱 ② GLB 링크(반복 에셋은 collection instance) + 배치(그리드 단위 × 0.1m) ③ 머티리얼 3종 강제 통일: 블록(무광 roughness 0.72 / metallic 0), emissive(strength = layout값), 받침대(유광 roughness 0.05) ④ 라이트: 키 Sun(3500K, layout 각도) + 림 Sun(무그림자) + point ≤6 ⑤ Cycles Metal GPU(맥 헤드리스 동작) samples 256 · denoise ⑥ 정적 메시 병합체에 Smart UV Project(margin 0.02) 2번째 UV → DIFFUSE(direct+indirect+color) 라이트맵 2048px 베이크 → 텍스처 팩 ⑦ baked GLB 익스포트 ⑧ 스틸 1920×1080 PNG 렌더 ⑨ (셸 래퍼 `tools/bake.sh`가) `cwebp -q 82` 변환 + `state/3d/bake-log.jsonl` append(ts·slug·samples·tri·경과초).
**수용 기준**: 무인 exit 0 · baked GLB gltf-validator 에러 0 · 캐릭터/동적 오브젝트는 베이크 제외(실시간 키라이트 그림자 담당).

---

## 5. ASSET AUTHORING PLAN — pet-ranch 킷

**블록 그리드 바이블 (M0에서 `state/3d/grid-bible.md`로 동결 — 이후 3D 킷이 SSOT, 2D는 무드 레퍼런스로 강등):**
| 항목 | 확정값 |
|---|---|
| 1 그리드 유닛(u) | **0.1 m** (GLB는 미터 단위) |
| 휴머노이드 신장 | **16u** (1.6 m) |
| 문 개구부 | **높이 20u × 폭 10u** · 벽 두께 2u · 층고 24u |
| 울타리 높이 | 6u |
| 받침대 | 씬 풋프린트 + **사방 8u 마진**, 두께 6u, 챔퍼 1u, 유광 검정 |
| 챔퍼(베벨) | **0.08u 절대값**(8mm), min_dim의 45% 클램프 |
| 병합 상한 | 기본 **8u³** · 지형 슬래브만 (8,8,4) |
| pet-ranch 씬 풋프린트 | 128×128u (받침대 144×144u) |

**킷 리스트 (22에셋 · 저작 순서 = 표 순서: 소형 연습 → 대형 → 유기체 최후):**
| # | 에셋 (manifest id) | 그리드 | 블록(박스) 예산 | 주 팔레트 idx | 저작 주체 |
|---|---|---|---|---|---|
| 1 | `nature/fence_post` | 2×2×6 | ≤4 | 13(wood) | 사람·MagicaVoxel |
| 2–5 | `fence_straight/corner/gate/low` | 8×2×6 | ≤12 | 13 | 사람 |
| 6 | `nature/feeding_trough` | 10×4×4 | ≤14 | 13, 6–8 | 사람 |
| 7 | `base/path_tile` | 8×8×1 | ≤10 | 14(stone) | 사람 |
| 8 | `base/ground_slab` | 32×32×6 | ≤130 | 1–3(mint=풀), 13 | 사람 |
| 9 | `base/water_pond` | 16×12×2 | ≤20 + 물셰이더 | 16 계열 | 사람+셰이더 |
| 10 | `base/cliff_module` | 16×16×12 | ≤60 | 14, 11 | 사람 |
| 11–13 | `nature/tree_l/m/s` | 24×24×32 / 16×16×24 / 10×10×14 | ≤180/≤90/≤40 | 1–4(잎), 13(줄기) | 사람 |
| 14 | `nature/bush` + `flower_patch` | 6×6×5 · 4×4×3 | ≤12 · ≤8 | 1–5, 6–7 | 사람 |
| 15 | `light/lantern_post` | 4×4×12 | ≤10 | 13 + **15(emissive)** | 사람 |
| 16 | `light/lantern_hanging` | 3×3×4 | ≤6 | 15 | 사람 |
| 17 | `nature/cottage` | 32×24×28 | ≤350 | 6–9(벽), 1–3(지붕), 15(창) | 사람 |
| 18 | `nature/barn` | 48×32×40 | ≤600 | 6–10, 13, 15(창) | 사람 |
| 19 | `creature/slime` (×3색 = 팔레트 스왑 1모델) | 8×8×7 | ≤25 | 1–5 / 6–10 / 16 | 사람 |
| 20 | `creature/baby_dragon` | 12×10×12 | ≤60 | 1–5 + 12 | 사람 |
| 21 | `chars/npc_caretaker` (머리·헤어·몸통·팔×2·다리×2 파트별 .vox 멀티모델) | 조립 후 신장 16u | ≤120 (파트합) | 12(피부 대용 cream), 6–8(옷) | 사람 |
| 22 | `creature/dragon_large` | 32×24×28 | ≤400 | 1–5, 15(눈) | 사람·**세미 스컬프트 경로**(Blender 로우폴리 스컬프트 → 복셀 리메시 → MagicaVoxel 보정 → vox2blocks) |

(+received: `base/pedestal`은 vox 저작 없이 `tools/make_placeholder.py`가 프로시저럴 생성하는 유일한 정식 에셋.)

**플레이스홀더 → 최종 스왑 프로토콜.**
1. M1 T1.1에서 22에셋 전부의 **프로그램 생성 플레이스홀더**(스펙 그리드의 단색 매스 박스, `kits/_placeholder/`)를 먼저 만들어 뷰어·레이아웃·베이크를 언블록.
2. 레이아웃은 경로가 아닌 **manifest 논리 id**만 참조 → 스왑 = `kits/manifest.json`의 경로 1줄 교체, 레이아웃 무수정.
3. 스왑 수용 기준: 최종 에셋 AABB가 플레이스홀더 대비 ±1u 이내(초과 시 레이아웃 재검토 플래그) + 예산 검사 통과.
4. 플레이스홀더 잔존 감시: `tools/check_budget.py --fail-on-placeholder`가 manifest에 `_placeholder` 경로가 남아 있으면 exit 1 — **M1 게이트에서 실행 의무**(품질 락인 방지, §9-R7).

---

## 6. QA & VERIFICATION PLAN

| 게이트 | 시점 | 검사 | 합격 기준 (검증 명령) | state/ 증거 |
|---|---|---|---|---|
| **G0 유닛** | 매 커밋 | vox2blocks·palette_gen·validate_layout 테스트 | `pytest tests/ -q` exit 0 | CI 로그 불요(로컬) — 게이트 문서에 실행 결과 붙임 |
| **G1 에셋** | 킷 변환마다 | GLB 구조 + 예산 | `npx gltf-validator <glb>` 에러 0 · `python tools/check_budget.py --manifest kits/manifest.json` exit 0 (클래스별 tri 상한: 소형 프롭 500 · 대형 프롭/나무 2,000 · 건물 4,000 · 히어로 30,000 · 휴머노이드 3,000 · 대형 크리처 10,000) | `state/3d/budget-<milestone>.json` (json-report 집계) |
| **G2 씬** | 레이아웃/베이크마다 | 스키마 + 씬 예산 | `check-jsonschema --schemafile scenes3d/layout.schema.json <layout>` 통과 · baked 씬 tri ≤ 500k · 뷰어 드로우콜 ≤ 100(뷰어 stats 패널 수치) | `state/3d/bake-log.jsonl` |
| **G3 룩 매치** | 씬당 A/B 수렴 종료 시 | 뷰어 스크린샷 vs `img-block/<slug>.webp` | ① `python tools/ab_score.py A.png B.webp` — 양쪽 64×36 다운스케일·휘도 정규화 후 **hue 히스토그램 상관 ≥ 0.6 AND 휘도 히스토그램 교차 ≥ 0.55** ② 사람 체크리스트 5항목 중 ≥4 합격: 키라이트 방향感 · 랜턴 글로우 풀 · 림 실루엣 분리 · 틸트시프트 밴드 · 받침대 반사 | `state/3d/ab/<slug>/` (스크린샷 쌍 + 스코어 JSON + 체크리스트) |
| **G4 스틸** | 씬당 Cycles 렌더 후 | 썸네일 품질 | 룩매치 루브릭(G3 체크리스트 동일 5항목) ≥ 4/5 · 1920×1080 · webp 존재 | `renders3d/<slug>.webp` + 루브릭 기록 |
| **G5 런타임** | 마일스톤당 1회 | Godot 임포트 | `godot --headless --path godot-smoke --import` 에러 0 · GUI 육안 1회(emissive·버텍스컬러) | 임포트 로그 사본 |
| **G6 애니** | 리깅 에셋마다 | 강체성 | Blender 스크립트 검사: 전 버텍스 웨이트 = 단일 본 1.0 (위반 0건) · 12fps 스텝 보간 재생 육안 | 게이트 문서 기재 |

마일스톤 종료 시 `state/3d/gate-M<n>.md`에 G0–G6 결과·증거 링크·미결 리스크를 집계한다. **G3 미달 씬은 스케일아웃 대열에 넣지 않는다** — 수렴 재시도 또는 §9-R1 분기.

---

## 7. SCALE-OUT PLAN (M2+)

**바이옴 그룹과 진행 순서 (킷 재사용률 내림차순):**
| 순서 | 바이옴 | 씬 | 신규 킷 부담 |
|---|---|---|---|
| M2 | 자연/전원 (7) | harvest-farm → housing-garden → pixel-forest → fishing-pier → sky-island → desert-oasis → world-tree-village(히어로: 세계수) | M1 킷 직계 재사용 최대. 신규: 농작물·풍차·부두·야자/사막 변형 |
| M3 | 중세 판타지 (8) | town-square → auction-plaza → blacksmith-forge → cozy-tavern(실내) → guild-hall(실내) → arena-colosseum → snowy-fortress(눈 변형) → siege-battle(파괴 변형) | 중세 건축 킷 30피스 선행 벌크 저작 · 군중 인스턴싱 검증 |
| M4 | 던전/마법 (9) | dungeon-boss(오우거=세미 스컬프트) → dragon-lair → haunted-crypt → lava-mines → mushroom-cavern → coral-ruins(수중) → magic-academy → alchemy-lab → rune-portal-hub | 동굴 지형 킷 + **FX 10종**(용암·포탈·안개 카드·룬 글로우) — FX를 이 마일스톤 선두에 |
| M5 | 동양/축제 + SF + 특수 (7) | hotspring-ryokan → fireworks-festival(파티클) → spaceport-hangar → cyber-market → pirate-cove(갤리온) → airship-deck(비행선) → overworld-map(보드형 — 미니 스케일 별도 그리드 1u=0.05m 예외 승인) | 바이옴당 씬 2개뿐이라 킷 투자 최소화 — 원오프 비중 상향 허용 |

**씬당 한계 공수 모델 (검증: M2 처음 2씬 실측으로 계수 보정):**
`씬 공수(일) = 0.15 × 신규킷피스 + 0.5 × 히어로원오프수 + 0.5(레이아웃) + 0.5(베이크·A/B) + 0.25(QA)`
→ M2 초반 ~5일/씬(신규 킷 ~20) → M3 이후 재사용률 80% 도달 시 **2.5~3.5일/씬**으로 수렴. 전략 문서의 3~5일 예측과 정합.

**병렬화 기회.** ① 사람-GUI 작업(MagicaVoxel 저작)과 헤드리스 작업(변환·베이크·A/B 스코어·QA)은 항상 오버랩 — 저작이 임계 경로 ② 씬 단위는 킷이 갖춰지면 상호 독립 → 작업자/에이전트 2–3개로 바이옴 내 씬 병렬 ③ Cycles 베이크·스틸은 야간 무인 배치 큐(`tools/bake.sh`를 씬 목록 루프) ④ 팔레트·플레이스홀더·레이아웃 초안은 저작 착수 전에 일괄 선행 가능.

**킷 택소노미 재방문 시점 (고정 2회).** ① M2 종료: 첫 재사용 실측 데이터로 manifest 분류·명명 감사, 중복 피스 병합 ② M4 종료: FX·실내 킷 편입 후 중간 감사 — 마켓 재판매 패키지 단위(바이옴별 팩)를 이때 확정. 임의 시점의 택소노미 확장은 금지(§9-R6 범위 증식 통제).

---

## 8. DEPENDENCY & ENVIRONMENT MATRIX

| 도구 | 버전(고정) | 용도 | macOS 헤드리스 | 라이선스 |
|---|---|---|---|---|
| MagicaVoxel | 0.99.7.1 | 복셀 저작 | **불가 — 사람 GUI 전용** | 무료(프리웨어, 비OSS — 산출물 사용 제한 없음) |
| Blender | 4.2 LTS | 스컬프트·리깅·베이크·스틸 | 가능(`blender -b`, Cycles Metal GPU) | GPL(산출물 자유) |
| Python | 3.11 + trimesh 4.x · pygltflib 1.16 · numpy 1.26 · Pillow | vox2blocks·palette_gen·검증기 | 가능 | MIT/BSD |
| three.js | r168 (CDN importmap 고정) | 웹 뷰어 | 브라우저(뷰어 자체는 GUI·스크린샷은 사람 또는 Playwright 자동화 선택지) | MIT |
| postprocessing (pmndrs) | 2.19.x | 포스트 스택 | 〃 | Zlib |
| Godot | 4.3 | 게임 런타임 스모크 | import는 `--headless` 가능 · 육안 확인만 GUI | MIT |
| gltf-validator | 최신 npx | GLB 검증 | 가능 | Apache-2.0 |
| check-jsonschema | pipx 최신 | 레이아웃 검증 | 가능 | Apache-2.0 |
| cwebp | 기존 설치본 | webp 변환(기존 `-q 82` 관행 승계) | 가능 | BSD |

전부 무료 — 소프트웨어 비용 0원(전략 문서와 일치). **사람 필수 구간은 정확히 3곳**: MagicaVoxel 저작, Blender 스컬프트/리깅의 조형 판단, G3/G4의 육안 체크리스트. 나머지 전 구간 무인 실행 가능.

---

## 9. RISK REGISTER (top 8)

| # | 리스크 | 트리거 | 임팩트 | 완화 | 소유 단계 |
|---|---|---|---|---|---|
| R1 | **AI 이미지 조명의 실시간 재현 불가** (물리 불가능한 바운스·블룸) | M1 G3 스코어 미달 | 웹 프리뷰 품질이 마켓 기대 미달 | 스틸컷은 Cycles 이원화(G4)로 품질 상한 확보 · 실시간은 "95% 무드" 목표로 A/B 수렴 · M1에서 갭 조기 계측 후 기준 재협상은 **1회만** 허용 | M1 |
| R2 | **소형 블록+베벨 폴리 폭발** (잎 클러스터 수천 tri) | G1/G2 예산 초과 | 웹 60fps 붕괴 | 잎·군중·자갈 GPU 인스턴싱(뷰어 자동 전환) · 원거리 LOD = 베벨 제거 플레인 박스(−60% tri) · `--cap` 파라미터로 씬별 밀도 조절 | M1–M3 |
| R3 | **세분화 캐릭터 애니 파탄** (관절 벌어짐/겹침) | G6 검사 실패 또는 육안 NG | 캐릭터 상품성 하락 | 강체 블록 스키닝 강제(G6 자동 검사) · 관절부 의도적 갭 컨벤션 · 12fps 스텝 = 스톱모션 미니어처 문법화 · 애니 3종 한정 | M1 |
| R4 | **2D 레퍼런스 간 그리드 불일치** (32장이 서로 다른 스케일) | 씬별 레이아웃 시 비율 충돌 | 킷 재사용 붕괴 | M0 그리드 바이블 동결 → **3D 킷이 신규 SSOT**, 2D는 무드 참조로 강등(레이아웃은 2D 구도만 차용, 치수는 바이블 준수) | M0–M2 |
| R5 | **볼류메트릭(물·불꽃·안개)의 블록 문법 이질성** | M4 FX 착수 | 룩 일관성 붕괴 | 전부 스타일라이즈드 셰이더/카드(폭포=스크롤 UV 블록기둥, 불꽃놀이=포인트 스프라이트, 안개=알파 카드) · 시뮬레이션 전면 금지 · FX 10종을 M4 선두에 몰아 조기 검증 | M4 |
| R6 | **범위 증식(scope creep)** — 킷 피스·애니·씬 디테일 무한 추가 | manifest 피스 수가 계획(~400) 대비 +20% 초과 | 일정 폭주 | 택소노미 변경은 §7의 고정 2회 감사에서만 · 씬당 원오프 상한 5개 · 신규 피스는 "2씬 이상에서 재사용 예정"을 manifest에 명기해야 승인 | 전 구간 |
| R7 | **플레이스홀더 품질 락인** — 임시 매스가 최종으로 출하 | `--fail-on-placeholder` 검출 또는 스왑 시 AABB ±1u 초과 | 마켓 품질 사고 | manifest 간접 참조로 스왑 무비용화(§5 프로토콜) · M1/각 마일스톤 게이트에서 플레이스홀더 잔존 검사 의무화 | M1+ 게이트 |
| R8 | **저작 병목·단일 작업자 의존** — MagicaVoxel 구간만 사람 필수 | 저작 속도 < 1.2h/피스 지속 | 임계 경로 지연 | 저작/헤드리스 오버랩(§7) · 반복물(울타리·나무 변형)은 부분 프로시저럴(vox 프로그램 생성) 전환 · AI image-to-3D는 **블록아웃 밑그림 한정**(TRELLIS 러프 → 복셀화 임포트 → 위에 재저작 — 최종 지오메트리는 항상 vox2blocks 경유) | M2+ |

(전략 문서 §6의 유광 받침대 SSR 비용 리스크는 뷰어 설계에 선반영 — planar reflection 1패스 + 큐브맵 폴백으로 종결 처리.)

---

## 10. EXECUTION ORDER SUMMARY (전 프로그램 체크리스트)

| 스텝 | 산출물 | 검증 명령 / 기준 |
|---|---|---|
| 1. 환경 셋업 | venv + Blender/Godot/validator 설치 | `python -c "import trimesh,pygltflib"` · `blender --version` · `npx gltf-validator --version` |
| 2. 그리드 바이블 | `state/3d/grid-bible.md` | §5 표 전 항목 수치 기재, TBD 0 |
| 3. vox 픽스처 | `tests/fixtures/` | MagicaVoxel 수동 오픈 3종 정상 |
| 4. vox2blocks 구현 | `tools/vox2blocks.py` | `pytest tests/test_vox2blocks.py` — T1~T10 green |
| 5. palette_gen 구현 | `tools/palette_gen.py` + `palettes/*` ×32 | `python tools/palette_gen.py --all` exit 0 · 팔레트 테스트 green |
| 6. 레이아웃 스키마 | `scenes3d/layout.schema.json` | 유효/무효 샘플 pass/fail 일치 |
| 7. **게이트 M0** | `state/3d/gate-M0.md` | G0 전부 green |
| 8. 플레이스홀더 22종 + manifest | `kits/_placeholder/` · `kits/manifest.json` | AABB = 스펙 ±0 · validator 0에러 |
| 9. 뷰어 구축 | `viewer/` | 플레이스홀더 씬 60fps · 포스트 5단 토글 |
| 10. pet-ranch 레이아웃 초안 | `scenes3d/pet-ranch.layout.json` | `check-jsonschema` 통과 |
| 11. 팔레트 락 + 킷 저작(순서: §5 표) | `vox/pet-ranch/*.vox` 20종 | 팔레트 외 색 0 · 그리드 내 |
| 12. 킷 변환 배치 | `kits/nature/*.glb` 등 | gltf-validator 0에러 · `check_budget.py` exit 0 |
| 13. 대형 드래곤 세미 스컬프트 | `dragon_large.glb` | 실루엣 승인 + 예산 ≤400박스 |
| 14. NPC 리깅 + idle | `npc_caretaker.rig.glb` | G6: 전 버텍스 단일본 100% |
| 15. 베이크 배치 구현·실행 | `assemble_bake.py` · `pet-ranch.baked.glb` | 무인 exit 0 · validator 0에러 |
| 16. 조명 A/B 수렴 | env 파라미터 확정 + `state/3d/ab/pet-ranch/` | `ab_score.py` corr ≥0.6 ∧ 교차 ≥0.55 ∧ 체크리스트 ≥4/5 |
| 17. Cycles 스틸 | `renders3d/pet-ranch.webp` | 루브릭 ≥4/5 · 1920×1080 |
| 18. Godot 스모크 | import 로그 | `godot --headless --import` 에러 0 |
| 19. **게이트 M1** | `state/3d/gate-M1.md` | G0–G6 전부 + `--fail-on-placeholder` 통과 |
| 20. M2: 자연 7씬 (씬당 §3 템플릿 6단계) | 씬별 layout+baked+webp | 씬마다 G1–G4 |
| 21. 택소노미 감사 #1 | manifest 정리 커밋 | 중복 피스 0 · 재사용 근거 명기 |
| 22. M3: 중세 킷 30피스 → 8씬 | 〃 | 〃 + town-square 60fps@web |
| 23. **게이트 M2/M3** | gate 문서 | 해당 씬 전부 G3 통과 |
| 24. M4: FX 10종 → 던전/마법 9씬 | 〃 | FX 셰이더 뷰어·Godot 양쪽 표시 정상 |
| 25. 택소노미 감사 #2 + 마켓 팩 단위 확정 | manifest + 팩 정의 | 감사 리포트 존재 |
| 26. M5: 동양/SF/특수 7씬 + 히어로 원오프 3종 | 〃 | 씬마다 G1–G4 · overworld-map 예외 그리드 승인 기록 |
| 27. 턴테이블 파이프 | `tools/blender/turntable.py` | 36프레임 webp 시퀀스 생성 exit 0 |
| 28. 32씬 썸네일 일괄 렌더 | `renders3d/*.webp` ×32 | 파일 32개 · 각 G4 루브릭 통과 |
| 29. 로그 통합 | `state/3d/render-log.jsonl` | 32 엔트리, 기존 gen-log 스키마 준용 |
| 30. **최종 감사 (게이트 M6)** | `state/3d/final-audit.md` | §1 프로그램 DoD 1–6 전 항목 evidence 링크로 충족 |

**결론.** 임계 경로는 `vox2blocks`(스텝 4) → pet-ranch 저작(11) → A/B 수렴(16)이며, 이 세 지점의 게이트를 통과하면 나머지 26씬은 §7의 한계 공수 모델(수렴 시 2.5~3.5일/씬)대로 기계적으로 스케일아웃된다. 총 144인일, 소프트웨어 비용 0원, 사람 필수 구간은 복셀 저작·조형 판단·육안 룩 판정 3곳뿐이다.