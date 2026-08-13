# Korea Travel Guidebook

정적 HTML 기반 한국 여행 가이드 (KR / EN / JP).

**GitHub Pages:** https://devhwangit.github.io/Korea-Travel-Guidebook/

## SEO

| 파일 | 역할 |
|------|------|
| `js/site-config.js` | 캐노니컬 origin (`SITE_ORIGIN`) · OG 기본 이미지 |
| `js/seo.js` | canonical / Open Graph / Twitter / hreflang 동기화 |
| `robots.txt` | 크롤 허용 + sitemap 위치 |
| `sitemap.xml` | 홈·주요 허브·놀거리 등 우선 색인 URL (가게 전체는 제외) |

- 홈·주요 허브 HTML에 `meta description`, OG/Twitter, `hreflang`(`?lang=ko|en|ja`), JSON-LD(홈)가 있습니다.
- 언어는 클라이언트 i18n이라 **로케일별 별도 경로가 없습니다.** `?lang=` + hreflang으로 보완합니다. (한계는 Search Console에서 확인)
- Pages URL·커스텀 도메인이 바뀌면 `js/site-config.js`의 `SITE_ORIGIN`과 `robots.txt` / `sitemap.xml`을 함께 수정하세요.

## 폴더 구조

```
Korea-Travel-Guidebook/
├── index.html          # 메인
├── robots.txt          # 크롤러 안내
├── sitemap.xml         # 주요 URL
├── styles.css          # 공통 스타일
├── README.md
├── pages/              # 섹션별 페이지
│   ├── foods/          # 음식·디저트
│   │   ├── meals/      # 식사 메뉴
│   │   └── desserts/   # 디저트·베이커리
│   ├── transportation/ # 명소 지도 (한반도 핀)
│   ├── convenience-store/
│   ├── buy/            # 쇼핑 및 놀거리 통합 허브
│   ├── fun/            # 놀거리 상세 (피시방·테마파크 등)
│   ├── souvenir/       # 기념품 상세 (허브는 buy로 리다이렉트)
│   ├── shopping/       # 쇼핑 팁 → travel-tips#shopping/* 리다이렉트
│   ├── travel-tips/    # 일상·식당·교통·쇼핑 (카테고리→서브탭)
│   ├── festivals/      # 축제 — 현재 공식 링크 안내 (API 추후)
│   ├── before-trip/
│   ├── apps/
│   ├── emergency/
│   └── …
├── Images/             # 공유 이미지 (메뉴·커버·교통·허브 등)
│   ├── cover/          # 사이트 커버·푸터
│   ├── menu/           # 메인 메뉴 타일
│   ├── foods/hub/      # 음식 가이드 허브 헤더
│   ├── before-trip/    # 떠나기 전 본문 이미지 (i18n body src)
│   └── transport/      # 지하철 도식 등
│                       # 가게·음식·기념품·편의점·놀거리 상세 사진은
│                       # pages/.../{slug}/media/ 에 둠 (pages/README.md)
├── audio/korean/       # 유용한 한국어 음성
├── data/
│   ├── food/           # recommend-catalog.js (먹거리 퀴즈 카탈로그)
│   ├── places/         # places-coords.js (명소·안내 핀 좌표)
│   └── metro/          # (레거시) 지하철 GeoJSON — 현재 HTML에서 미사용
├── i18n/               # ko.json / en.json / ja.json → messages.js
├── js/                 # 프론트 스크립트
├── scripts/            # 빌드·마이그레이션용 Python
├── tool/               # 버전 bump · 로컬 콘텐츠 관리
├── templates/          # HTML 템플릿
└── components/         # (예비) 공통 조각
```

## 번역

1. `i18n/ko.json` · `en.json` · `ja.json` 수정  
2. `python i18n/build-bundle.py` 실행 → `i18n/messages.js` 갱신  

로컬에서 `file://`로도 번들 로드가 됩니다. JSON fetch가 필요하면 `npx serve .` 권장.

## 캐시 버스팅 (CSS/JS 강제 갱신)

`tool/update-version.bat` 실행하면 됩니다. (버전을 `YYYYMMDDHHMMSS`로 올리고 모든 HTML의 `?v=`에 반영)

수동으로 할 때:

1. `js/cache-version.js`의 `SITE_ASSET_VERSION` 확인/수정
2. `python scripts/apply-cache-bust.py` 실행 → 로컬 `styles.css` / `i18n/*.js` / `js/*.js` / `data/**/*.js` 참조에 `?v=...` 일괄 반영
3. 커밋 후 푸시

외부 CDN(Leaflet, Google Fonts 등) URL은 건드리지 않습니다.

## 축제 페이지

현재 `pages/festivals/`는 **공식 관광 사이트 링크 안내**만 제공합니다. TourAPI 연동·지역별 정리는 추후입니다. `TOUR_API_KEY`는 필요하지 않습니다.

## AdSense

홈·템플릿·여행팁 등은 **실제 publisher** `ca-pub-7139367317436403`로 연결됩니다.

- `<meta name="google-adsense-account" content="ca-pub-7139367317436403">` — 계정 확인용
- `window.ADSENSE_CLIENT` + `js/ads.js`가 `adsbygoogle.js?client=…`를 로드 (head에 스크립트 중복 삽입 금지)
- 디스플레이 광고: AdSense 대시보드에서 **광고 단위**를 만든 뒤 `data-ad-slot`에 유닛 ID를 넣으세요 (지금은 비워 둠)
- DEV 플레이스홀더는 Google 샘플 client / `file://` / localhost에서만 표시
- 로컬 테스트 시 샘플 client `ca-pub-3940256099942544` + `data-adtest="on"`은 `js/ads.js`의 `TEST_CLIENT` 경로로만 강제됩니다

언어 추가(중국어 등): `i18n/README-locales.md` 참고.

## 콘텐츠 관리 툴

`tool/content-admin.bat` 실행 → 브라우저에서 `http://127.0.0.1:8765`.

- 음식·가게 KO/EN/JA · 이미지 업로드 · 가게 연결 가능
- **저장 시** `i18n/build-bundle.py`(messages.js)와 캐시 버전(`SITE_ASSET_VERSION` + HTML `?v=`)이 **자동** 실행됩니다
- 반영 확인: **http://127.0.0.1:8765/viewer** (또는 해당 페이지 URL)에서 **Ctrl+F5**. `file://`로 `index.html`을 열면 예전 화면이 남을 수 있습니다
- 자세한 안내: `tool/README-admin.md`

## 먹거리 추천 퀴즈

`pages/food-life/`의 추천 퀴즈는 **태그 점수 → 카탈로그 매칭**으로 결과를 고릅니다.

1. `pages/foods/meals/*/`, `pages/foods/desserts/*/`, `pages/convenience-store/*/` 를 스캔
2. `python tool/build-food-recommend-catalog.py` → `data/food/recommend-catalog.js` 생성
3. 질문 옵션은 메뉴 id가 아니라 `tags` / `kinds`에 점수를 주고, 카탈로그 항목 중 합산이 가장 높은 것을 추천 (동점 시 무작위)

**새 식사·디저트 카테고리 추가 후**

1. 허브 페이지를 만듭니다 (`pages/foods/meals/{slug}/` 또는 `desserts/{slug}/`)
2. 카탈로그 갱신 (아래 중 하나면 됨)
   - `tool/update-version.bat` / `python tool/update-version.py` (**Update 시 자동**)
   - CMS 저장·음식 생성/삭제 시 **자동**
   - 또는 `python tool/build-food-recommend-catalog.py` 단독 실행
3. 태그가 어색하면 `data/food/recommend-tags.json`의 `items.{slug}`에 `tags` / `extraTags` / `exclude` / `titleKey` / `reasonKey`를 적어 재실행

결과 제목은 `dishes.{slug}.title`(또는 페이지의 `data-i18n-title`)을 쓰고, 이유가 없으면 `dishes.*.desc` → `foodLife.quiz.defaultReason` 순으로 폴백합니다.

## 주요 스크립트

| 경로 | 역할 |
|------|------|
| `tool/update-version.bat` | 먹거리 추천 카탈로그 갱신 + 캐시 버전 bump + HTML `?v=` 일괄 적용 |
| `tool/content-admin.bat` | 로컬 콘텐츠 관리 UI (음식·가게 CRUD) |
| `tool/build-food-recommend-catalog.py` | 먹거리 퀴즈 카탈로그 생성 |
| `i18n/build-bundle.py` | 언어 JSON → messages.js |
| `scripts/apply-cache-bust.py` | 버전을 HTML의 로컬 CSS/JS `?v=`에 일괄 적용 |
| `js/cache-version.js` | 에셋 캐시 버전 (단일 소스) |
| `js/site-config.js` | 사이트 origin · SEO 기본값 (`TOUR_API_KEY`는 추후용 예약) |
| `js/festivals.js` | (미연결) 추후 TourAPI용 예약 스텁 |
| `js/seo.js` | meta/OG/hreflang 헬퍼 |
| `js/i18n.js` | 언어 전환 (`?lang=` 동기화) |
| `js/content-body.js` | 게시글형 본문(문단·사진·유튜브) 렌더 |
| `js/region-tabs.js` | 탭 UI |
| `js/places-map.js` | 명소 전체 화면 한반도 지도 |
| `js/ads.js` | AdSense 로더 (클라이언트 설정 시) |
| `js/buy-hub.js` | 쇼핑/놀거리 허브 뷰 전환 |
| `js/metro-map.js` / `js/map-zoom.js` | 레거시(현 HTML 미연결) — 도식 노선도용 |

## 페이지·미디어 경로 규칙 (캐논)

- 섹션 허브: `pages/{section}/index.html`
- 음식: `pages/foods/meals/{slug}/`, `pages/foods/desserts/{slug}/` + `media/cover.jpg`
- 가게 상세: `pages/foods/meals/kimbap/{shop}/index.html` + `media/` (cover, body-N)
- 쇼핑 및 놀거리 허브: `pages/buy/index.html` (`#shopping` / `#fun`)
- 기념품·편의점 상세: `pages/souvenir/{slug}/`, `pages/convenience-store/{slug}/` + `media/`
- 놀거리 상세: `pages/fun/{pcbang|noraebang|escape-room|jjimjilbang|lotte-world|everland}/`
- 쇼핑 팁: `pages/travel-tips/index.html#shopping/{olive|daiso|duty|market}` (`pages/shopping/*`는 리다이렉트)
- 축제: `pages/festivals/` — 공식 VisitKorea·구석구석 링크 안내 (API 추후)
- 명소 좌표: `data/places/places-coords.js` · 카피: `i18n/*/places`
- 공용 이미지: `Images/menu/`, `Images/cover/`, `Images/transport/`, `Images/foods/hub/`, `Images/before-trip/`
- 자세한 media 규칙: `pages/README.md`
