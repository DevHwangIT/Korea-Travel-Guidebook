# Korea Travel Guidebook

정적 HTML 기반 한국 여행 가이드 (KR / EN / JP).

## 폴더 구조

```
Korea-Travel-Guidebook/
├── index.html          # 메인
├── styles.css          # 공통 스타일
├── README.md
├── pages/              # 섹션별 페이지
│   ├── foods/          # 음식·디저트
│   │   ├── meals/      # 식사 메뉴
│   │   └── desserts/   # 디저트·베이커리
│   ├── transportation/
│   ├── convenience-store/
│   ├── souvenir/
│   ├── useful-korean/
│   ├── shopping/
│   ├── travel-tips/
│   ├── before-trip/
│   ├── apps/
│   └── …
├── Images/             # 이미지 리소스
│   ├── cover/          # 사이트 커버·푸터
│   ├── menu/           # 메인 메뉴 타일
│   ├── foods/
│   │   ├── dishes/     # 음식 대표 사진
│   │   ├── brands/     # 브랜드(설빙·파리바게뜨 등)
│   │   ├── restaurants/# 가게 사진 (예: kimbap/)
│   │   └── hub/        # 허브 헤더
│   ├── convenience/    # 편의점 꿀조합
│   ├── souvenir/       # 기념품
│   └── transport/      # 지하철 도식 등
├── audio/korean/       # 유용한 한국어 음성
├── data/metro/         # 지하철 GeoJSON·번들
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

## 콘텐츠 관리 툴

`tool/content-admin.bat` 실행 → 브라우저에서 `http://127.0.0.1:8765`. 음식·가게의 KO/EN/JA 문구·이미지 업로드·기존 가게를 음식 하위로 복수 연결할 수 있습니다. 저장 시 `i18n/build-bundle.py`가 자동 실행됩니다. 큰 배포 전에는 버전 툴도 한 번 실행하세요.

## 주요 스크립트

| 경로 | 역할 |
|------|------|
| `tool/update-version.bat` | 캐시 버전 bump + HTML `?v=` 일괄 적용 |
| `tool/content-admin.bat` | 로컬 콘텐츠 관리 UI (음식·가게 CRUD) |
| `i18n/build-bundle.py` | 언어 JSON → messages.js |
| `scripts/apply-cache-bust.py` | 버전을 HTML의 로컬 CSS/JS `?v=`에 일괄 적용 |
| `scripts/reorg-food-images.py` | 음식 이미지 dishes/brands/restaurants 정리 |
| `js/cache-version.js` | 에셋 캐시 버전 (단일 소스) |
| `js/i18n.js` | 언어 전환 |
| `js/region-tabs.js` | 탭 UI |
| `js/metro-map.js` | 지하철 인터랙티브 지도 |
| `js/map-zoom.js` | 도식 노선도 확대·축소 |
| `js/phrase-audio.js` | 한국어 음성 재생 |

## 페이지 경로 규칙

- 섹션 허브: `pages/{section}/index.html`
- 음식: `pages/foods/meals/{slug}/`, `pages/foods/desserts/{slug}/`
- 김밥 가게: `pages/foods/meals/kimbap/{shop}.html`
- 편의점 조합: `pages/convenience-store/{combo}/index.html`
