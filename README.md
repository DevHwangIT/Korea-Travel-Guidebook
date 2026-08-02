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
├── templates/          # HTML 템플릿
└── components/         # (예비) 공통 조각
```

## 번역

1. `i18n/ko.json` · `en.json` · `ja.json` 수정  
2. `python i18n/build-bundle.py` 실행 → `i18n/messages.js` 갱신  

로컬에서 `file://`로도 번들 로드가 됩니다. JSON fetch가 필요하면 `npx serve .` 권장.

## 주요 스크립트

| 경로 | 역할 |
|------|------|
| `i18n/build-bundle.py` | 언어 JSON → messages.js |
| `scripts/reorg-food-images.py` | 음식 이미지 dishes/brands/restaurants 정리 |
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
