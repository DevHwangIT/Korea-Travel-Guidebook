# Adding a locale (e.g. Chinese `zh`)

Languages are **data-driven** in `js/i18n.js` via `GUIDE_LANGS`:

```js
var GUIDE_LANGS = [
  { code: "ko", label: "KR" },
  { code: "en", label: "EN" },
  { code: "ja", label: "JP" },
  // { code: "zh", label: "中文" },
];
```

## Steps

1. Uncomment / add `{ code: "zh", label: "中文" }` in `GUIDE_LANGS`.
2. Copy `i18n/ko.json` → `i18n/zh.json` and translate string leaves (keep body-block `ko`/`en`/`ja` keys; add `"zh"` on each block when you start using Chinese in freeform bodies).
3. Update `i18n/build-bundle.py` to include `"zh"` in the lang list, then run:

   ```bash
   python i18n/build-bundle.py
   ```

4. Bump `js/cache-version.js` (or run `tool/update-version.py`) so browsers pick up `messages.js`.

## UI switcher

`.lang-switch` navs are **rebuilt at runtime** from `GUIDE_LANGS`. You do not need to hardcode KR/EN/JP buttons on every page. Pages may keep empty `<nav class="lang-switch" aria-label="Language"></nav>` or legacy three buttons — both are replaced on load.

`window.GuideI18n.languages` / `.supported` expose the same config for other scripts (map, buy hub).

## Notes

- Keep existing KO/EN/JA working while adding a fourth locale.
- Freeform `*Body` arrays currently store `ko`/`en`/`ja` per block; extend blocks with `zh` when Chinese editorial content is ready (`js/content-body.js` already prefers the active lang key).
