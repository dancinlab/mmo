# fable asset strategy — mmo block dioramas · 2026-07-02 · sidecar fable (claude-fable-5, headless) · grounded on 6 opened images

6개 대표 이미지(town-square, dungeon-boss, cyber-market, world-tree-village, lava-mines, hotspring-ryokan)를 직접 열어 확인했고, `scenes.json`(32씬)·`gen-dioramas.py`·`img-block/`(26장, 84–142KB) 상태를 대조했습니다. 아래가 전체 답입니다.

---

# mmo 블록 디오라마 → 프로덕션 에셋 운영 전략

**관찰 근거(직접 열어본 6장 공통):** 아이소메트릭 페데스탈(받침대) 디오라마, 피사체 질량은 프레임 중앙~중앙 위쪽에 집중, 좌우 각 ~8–12% / 상단 ~5–10%는 어두운 배경 여백, **하단 ~12–15%는 페데스탈 하단 모서리 + 바닥 반사 + 빈 배경**. 예외: `world-tree-village.webp`는 나무 캐노피가 **상단 프레임에 닿아 잘려** 있음(상단 여백 0). `cyber-market.webp`·`lava-mines.webp`는 배경이 순흑이 아니라 노을/웜 그라데이션 하늘. `dungeon-boss.webp`·`haunted-crypt.webp`(84–87KB, 최소 용량 파일들)는 배경이 거의 순흑으로 가장 어두움. `cyber-market.webp`에는 네온 사인에 글자 형태(glyph-like) 요소가 존재 — 실제 단어로는 안 읽히지만 QA 감시 대상.

---

## 1. ASSET SPEC — 표면별 매트릭스

마스터: `landscape_16_9` 1장/씬 (`gen-dioramas.py:25`). **마스터 실측 px는 이 세션에서 미확인(sips 승인 거부)** — 파이프라인 착수 전 `sips -g pixelWidth -g pixelHeight img-block/*.webp`로 1회 확정할 것. 이하 스펙은 마스터 ≥1536×864 가정, 미달 시 §2의 업스케일 단계가 필수로 승격.

| 표면 | 픽셀 (@1x / @2x) | 크롭 전략 | 포맷·품질 | 용량 예산 |
|---|---|---|---|---|
| marketplace card 16:9 | 640×360 / 1280×720 | 크롭 없음, Lanczos 다운스케일 | webp q80 | ≤70KB (@2x ≤140KB) |
| detail hero 16:9 | 1920×1080 | 크롭 없음 (마스터<1920이면 업스케일) | webp q88 | ≤300KB |
| list icon 1:1 | 512×512 (+256 파생) | **중앙 정사각 + 상향 바이어스 크롭**: 가로 중앙, 세로는 크롭창을 이미지 높이의 **5% 위로** 이동(하단 페데스탈/반사 사각지대 버림). `world-tree-village`만 바이어스 0·상단 고정 | webp q85 | ≤30KB |
| mobile 9:16 | 1080×1920 | **크롭 불가 → 재생성** (§2) | webp q82 | ≤180KB |
| OG/social 1200×630 | 1200×630 (1.905:1) | 전폭 유지, 높이만 트림: 총 6.7% 컷을 **상단 20% / 하단 80% 배분** (하단이 반사·빈 배경이므로) | **jpg q85** (webp 미지원 스크레이퍼 대응) | ≤200KB |

9:16 크롭 불가 근거: 16:9에서 9:16을 잘라내면 원본 가로의 31.6%만 남는데, 6장 모두 디오라마가 가로 70–80%를 점유 — 어떤 크롭창도 디오라마를 절단함.

## 2. DERIVATION PIPELINE — 권장: "크롭 오버라이드 테이블 + 결정론적 파생 스크립트"

**스마트크롭(saliency) 불필요.** 구도가 6/6 이미지에서 일관되게 중앙 배치라, 기본 규칙(중앙 + 세로 -5% 바이어스) + 씬별 예외 테이블이면 충분하고 결과가 결정론적이라 QA가 쉬움.

1. **원본 PNG 보존이 선행 조건.** 현재 `gen-dioramas.py`는 fal raw를 `cwebp -q 82`로 변환 후 raw를 버림 → **q82 webp를 재인코딩하면 세대 손실**. 스크립트에 raw PNG를 `masters/<slug>.png`로 보관하는 한 줄을 추가하고, 모든 파생은 raw에서 시작.
2. `derive.py` (Pillow/libvips): `scenes.json` 순회 → 표면별 리사이즈/크롭 → `cwebp` 표면별 q 적용 → `assets/<slug>/` 출력. 크롭 예외는 `crops.json` (`{"world-tree-village": {"icon_bias": 0.0, "anchor": "top"}}`).
3. **재렌더가 불가피한 경우 2가지:** (a) 9:16 전 씬 — `gen-dioramas.py`에 `MMO_SIZE=portrait_16_9` 경로 추가, 동일 SKEL/TAIL에 "tall vertical composition, pedestal in lower half, headroom above" 한 줄 추가한 v4-portrait를 `prompts.json`에 버전 등록. (b) 피사체가 프레임 모서리에 닿은 씬(현재 `world-tree-village`) — "full diorama visible with margin on all sides" 지시로 16:9 재생성.
4. hero 1920 업스케일이 필요하면 fal 업스케일러(또는 Real-ESRGAN) 1패스 → 다운스트림 동일.

대안(한 줄): 표면별 전량 재생성 — 비용 5배·씬간 비일관성 유발이라 기각. 9:16만 예외.

## 3. NAMING & LAYOUT

```
mmo/
├─ masters/<slug>.png            # fal raw 원본 — bucket 보관, git-lfs 또는 git 제외
├─ assets/
│   └─ <slug>/
│       ├─ master.webp           # 현 img-block/*.webp 이동 (git 유지, ~100KB×32는 부담 없음)
│       ├─ card.webp  hero.webp  icon.webp  og.jpg  portrait.webp
│       └─ meta.json             # §5 사이드카
├─ crops.json                    # 씬별 크롭 오버라이드
└─ state/gen-log.jsonl           # 런 이력 (현행 유지)
```

- **git에는** `assets/<slug>/master.webp` + `meta.json` + `crops.json`만. 파생 표면(card/hero/icon/og/portrait)은 **git 제외** — `derive.py`가 결정론적으로 재생산하므로 산출물이지 소스가 아님.
- **CDN/bucket**(R2/S3)에 파생 표면을 콘텐츠 해시 경로로 발행: `cdn/.../<slug>/card.<sha8>.webp`, `Cache-Control: immutable`. 리프레시 = 새 해시 = 캐시 무효화 자동.
- 버전 규율: 마스터 교체는 git 커밋이 곧 버전(현행 `prompts.json` v1..vN 규율과 동일 정신). `img-block/` 등 스타일별 평면 디렉토리는 실험용으로 동결, 프로덕션은 `assets/`가 SSOT.

## 4. QA GATE — 이미지당 출고 전 체크리스트 (하나라도 실패 → 재생성)

1. **텍스트 침입**: 200% 확대로 간판·배너·네온 검사. 실제 단어로 읽히면 reject. (`cyber-market`의 네온 glyph처럼 비문자 형상은 pass — 현재 6장 모두 pass)
2. **페데스탈 무결성**: 받침대 4변이 프레임 안에 완전히 들어오고 바닥 반사 존재. (`lava-mines`의 2단 분할 받침대 같은 변형은 pass — 절단만 reject)
3. **여백**: 피사체가 좌·우·상 프레임에서 각 ≥5% 떨어질 것. 위반 시 `crops.json` 오버라이드 등록 또는 재생성. (**현재 `world-tree-village` 위반**)
4. **팔레트 일치**: `scenes.json` 3열의 팔레트 쌍이 지배 색상인지 육안 대조. (6장 모두 일치 확인 — emerald/teal, red/charcoal, magenta/plum, forest-green/gold, orange/charcoal, jade/cream)
5. **스타일 v4 준수**: 스터드/홈 없음, 거대 단일 큐브 없음, 캐릭터가 다중 블록으로 세분화, 시네마틱 라이팅(웜 키 + 림) 존재.
6. **밝기 하한**: 카드 크기(360px)로 축소해 다크 테마 UI 목업 위에서 실루엣이 식별되는지 확인. `dungeon-boss`·`haunted-crypt`급 저조도 씬이 경계선 — 림 글로우가 살아 있으면 pass.
7. **AI 아티팩트**: NPC 사지 융합·중복, 물리적으로 불가능한 구조물 없음 (축소 썸네일에선 안 보여도 hero 1920에선 보임).
8. **파일 검증**: 정확한 16:9 비율, 표면별 용량 예산(§1) 내.

## 5. OPERATIONS

- **시즌/이벤트 변형**: TAIL에 시즌 수식어 1줄 추가("dusted with snow, holiday lanterns")한 버전을 `prompts.json`에 `v4-winter`식으로 등록(SSOT 규율 유지) → `assets/<slug>/variants/winter-2026/` 아래 동일 표면 세트. 전량이 아니라 **트래픽 상위 8–10씬만** 변형 제작.
- **A/B 썸네일**: 씬당 2렌더 생성 → card 표면만 A/B 배포 → CTR 승자를 master로 승격, 패자는 bucket 보관. 리테일 페이지가 아닌 card에서만 실험(hero까지 바꾸면 신뢰 저하).
- **리프레시 주기**: 스타일 버전 범프 시에만 전량 재생성, 그 외 분기 1회 QA 재감사. 비용 추적은 이미 있는 `state/gen-log.jsonl`이 근거 — 현행 로그 기준 씬당 평균 ~1.2 호출(자동 재시도 포함)로 전량 리프레시 ≈ 38–40 호출.
- **메타데이터 — JSON 사이드카가 정답, gen-log는 보조**: `assets/<slug>/meta.json`에 `{slug, subject, palette, prompt_version, model, generated_at, master_sha256, surfaces: {card: {px, q, sha8}, ...}, qa: {status, checked_at, overrides}, genlog_ref}`. gen-log는 append-only 런 이력으로 유지하되 에셋별 현재 상태의 SSOT는 사이드카.

## 6. GAPS — 지금 물지 않으면 에셋 단계에서 무는 것들

1. **6씬 누락**: `img-block/`은 26장인데 `scenes.json`은 32씬. `housing-garden`, `auction-plaza`, `pet-ranch`, `rune-portal-hub`, `fireworks-festival`, `siege-battle` 미생성 — 파이프라인 착수 전 `MMO_ONLY=`로 생성 필요.
2. **raw PNG 미보관**: 현재 유일한 마스터가 q82 webp — hero q88을 여기서 재인코딩하면 화질 상한이 q82. §2-1의 raw 보관을 다음 런부터 즉시 적용, 기존 26장은 차기 리프레시 때 교체.
3. **`world-tree-village` 상단 절단**: 캐노피가 프레임에 닿아 icon/OG 크롭 시 나무가 목 잘림. 여백 지시 추가 재생성 1회가 크롭 꼼수보다 싸다.
4. **하단 사각지대**: 페데스탈+반사가 하단 12–15%를 소비 — 1:1/OG 크롭이 상향 바이어스를 안 걸면 아이콘의 1/7이 빈 바닥. §1 크롭 규칙이 이걸 흡수.
5. **9:16은 구조적으로 파생 불가**: 재생성 라인(§2-3a)을 처음부터 계획에 포함, "나중에 크롭하지"라고 미루면 안 됨.
6. **배경 밝기 편차**: 순흑(`dungeon-boss`) ↔ 노을 하늘(`cyber-market`, `lava-mines`)이 마켓 리스트 그리드에서 타일별 톤 점프를 만듦. 팔레트 다양성으로 수용하되, QA 6번(다크 테마 실루엣)과 "코너 휘도 범위" 검사로 극단만 걸러낼 것. 라이트 테마 마켓에서는 전 씬이 어두운 배경이라 오히려 대비가 좋음 — 다크 테마가 리스크.
7. **마스터 해상도 미확정**: §1 서두의 실측을 끝내기 전에는 hero 1920 스펙이 가정 위에 서 있음. 1536 미만이면 업스케일 단계가 선택이 아니라 필수.