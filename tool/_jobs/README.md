# One-off jobs (not part of the public site)

`tool/` 루트에는 로컬 관리자(`content-admin`)와 사이트 업데이트(`update-version`, `build-food-recommend-catalog`, `generate-sitemap`)만 둡니다.

여기 파일은 일회성 패치·이미지 수집·마이그레이션입니다. 공개 페이지 런타임에서 쓰이지 않습니다.

다시 실행할 때는 `tool/`로 복사한 뒤 돌리세요. 대부분의 스크립트는 `Path(__file__).parents[1]`을 프로젝트 루트로 가정합니다.
