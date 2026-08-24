# Place cover photos — sources

Real photographs under `Images/places/{slug}.jpg`, mostly from Wikimedia Commons
(CC / Public domain / CC0). Downloaded via Commons API + Special:FilePath.

## Coverage
- Map places with local real photos: **67** (all coords entries with `image:`)
- No test / unknown pins (zz-verify removed)

## Notes
- Lockers use place-specific station / airport / district photos (not coin-locker close-ups).
- `noryangjin-cupbap`: Commons has no dedicated “컵밥거리” street photo; uses adjacent Noryangjin Fish Market tourist shot.
- `embassy-japan-seoul`: uses Seoul City Hall / civic plaza photo (Commons lacked a clean modern embassy exterior without protest framing).
- `_types/*.jpg` remain as last-resort fallbacks only.

## Tooling
- `tool/_fetch-place-photos.ps1` — initial Commons batch fetch
- `tool/_place-photo-fetch-log.json` — first-pass titles/licenses (some later replaced)
