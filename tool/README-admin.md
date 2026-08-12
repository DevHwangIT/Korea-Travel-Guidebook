# Admin (localhost)

## 올바르게 열기

1. `tool/content-admin.bat` 더블클릭 (또는 `python tool/content-admin.py`)
2. 브라우저에서 **http://127.0.0.1:8765/** (또는 `/admin`, `/cms`) 를 엽니다
3. 왼쪽 사이드바가 보이면 **관리자 CMS**입니다

**하지 마세요:** 프로젝트의 `index.html`을 파일로 직접 열거나(`file://`), `index.html?admin=1`만으로 “전체 관리자”를 기대하기.

| URL | 용도 |
|-----|------|
| http://127.0.0.1:8765/ | CMS 대시보드 (글·가게·명소 등록) |
| http://127.0.0.1:8765/cms | 위와 동일 |
| http://127.0.0.1:8765/viewer | 공개 사이트 + 오버레이 (빠른 수정 진입) |

이미 켜 둔 검은 창(서버)이 있으면 **Ctrl+C로 끈 뒤** 다시 실행하세요. 예전 프로세스에 붙으면 최신 코드가 반영되지 않습니다.

### 저장했는데 화면이 안 바뀌면

1. CMS에서 **저장** (문구는 `i18n` 번들 + 캐시 버전을 자동 갱신합니다)
2. 공개 화면에서 **Ctrl+F5** (강력 새로고침) — 또는 `/viewer`를 다시 엽니다
3. 반드시 **http://127.0.0.1:8765/...** 로 확인하세요 (`file://`로 연 탭은 예전 파일을 붙잡을 수 있음)

Admin is **localhost-only**. GitHub Pages에는 관리자가 없습니다.

## Boards (공개 IA 기준)

| 보드 | 내용 |
|------|------|
| 떠나기 전에 | 서류·돈·통신·짐·**혼자 식사** 탭 |
| 준비·안내 | 앱(카카오 T·배민·요기요 등 카테고리 포함)·한국어·긴급 연락 |
| 먹거리 | 식사(고기집·닭한마리·신규 국물류 등)·디저트(빵집 브랜드는 `bread` 하위 가게)·가게·편의점 |
| 쇼핑 및 놀거리 | 쇼핑 상품(souvenir)·놀거리(fun)·쇼핑 팁 |
| 명소 | 전국 지도 핀 (`city` / `nature` / `heritage` / `airport` / `info`) — 예전 “교통” 보드명 아님 |
| 축제 및 행사 | 플레이스홀더·지역 섹션 (`/section?id=festivals`) — 추후 행사 목록 확장 |
| 여행 팁 | 일상·식당·교통 (+ 공개 허브의 쇼핑 팁 링크) |
| 제휴·추천 | CMS 전용 보드 없음 — 사이드바 안내 · 공개 `partner-panel` / `partner-strip` · i18n `home.partner*` |

## Languages

공개 사이트·CMS 저장 모두 **ko / en / ja / zh(中文)** 를 지원합니다. CMS는 한국어로 쓰고 저장 시 영어·일본어·중국어를 자동 채웁니다.

## Places (명소)

Detail pages: `pages/transportation/places/{slug}/`. i18n: `places.{slug}`. Map pins: `data/places/places-coords.js` (`type` + `region`). CMS place form includes region + pin type.

## Fun (놀거리)

Section `/section?id=fun`. Public cards: `pages/buy/index.html#fun` → `pages/fun/{slug}/`. Body images: `pages/fun/{slug}/media/body-N.jpg`.

## Shops (가게)

- CMS: `/shops` → **새 가게** (`/shop/new`)
- **등록**: 네이버 플레이스 / 카카오맵 / 구글 지도 URL **또는 주소**를 넣고 **URL/주소로 채우기**
  - `POST /api/shop/resolve` → `{ sourceType, name, address, mapsEmbedUrl, placeUrl, phone?, imageUrl? … }`
  - 이름·주소·지도·(가능하면) 미리보기 이미지를 폼에 자동 채움
  - 네이버·카카오는 스크래핑이 막히는 경우가 많아 전화·영업시간·사진은 수동 보완이 필요할 수 있음
- **공개 페이지**: 사진 → 이름 → **자세한 가게 정보**(가게명·주소·전화·영업시간·소개, 지도 앱 링크는 보조) → **메뉴 목록·사진 갤러리**(스크래핑 시) → 지도
- 상호 사진: `shop_image` → `pages/foods/{meals|desserts}/{dish}/{shop}/media/cover.jpg`
- i18n 필드: `sourceType`, `placeUrl`, `mapsUrl`, `mapsEmbedUrl`, `mapsProvider`, `phone`, `hours`, `previewImage`, `menuItems`, `photos`, `placeId`
- 플레이스 보강: `POST /api/shop/resolve` 가 네이버 Apollo 상태를 파싱해 전화·영업시간·메뉴·사진을 채움 (막히면 기존 값 유지)
- 일괄 보강: `python tool/migrate_shop_enrich.py` (이미지·메뉴를 `media/`에 로컬 저장)
