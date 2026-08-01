# Korea Travel Guidebook

한국 여행을 위한 정적 HTML 가이드입니다. (KR / EN / JP)

## 폴더 구조

```
Korea-Travel-Guidebook/
├── index.html                 ← 메인 페이지
├── styles.css
├── Images/
├── pages/
│   ├── foods/
│   │   ├── index.html         ← 음식 가이드 목록
│   │   └── *.html             ← 개별 음식 페이지
│   ├── emergency/
│   │   └── index.html
│   └── ...                    ← 섹션별 폴더 + index.html
├── templates/                 ← 새 페이지 만들 때 참고/복사
│   ├── page-template.html
│   ├── header.html
│   └── footer.html
├── components/                ← 재사용 UI 스니펫
│   ├── navbar.html
│   └── card.html
└── README.md
```

## 새 페이지 추가 방법

1. `templates/page-template.html`을 복사합니다.
2. `pages/섹션이름/index.html`로 저장합니다.
3. 제목·본문·이미지 경로를 수정합니다.
4. 필요하면 `components/navbar.html`, `components/card.html` 내용을 붙여 넣습니다.
5. 메인 `index.html` 메뉴에 링크를 추가합니다.

> 이 프로젝트는 빌드 도구 없이 정적 HTML로 동작합니다.  
> `templates/`, `components/`는 **복사해서 쓰는 참고용** 파일입니다.

## 로컬에서 보기

`index.html`을 브라우저로 열거나, 프로젝트 루트에서 간단한 서버를 실행하세요.

```bash
npx serve .
```
