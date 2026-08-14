# Adding a locale

Languages are **data-driven** in `js/i18n.js` via `GUIDE_LANGS`:

```js
var GUIDE_LANGS = [
  { code: "ko", label: "한국어" },
  { code: "en", label: "English" },
  { code: "ja", label: "日本語" },
  { code: "zh", label: "简体中文" },
  { code: "zh-Hant", label: "繁體中文" },
  { code: "vi", label: "Tiếng Việt" },
  { code: "th", label: "ภาษาไทย" },
  { code: "ru", label: "Русский" },
];
```

## Steps

1. Add `{ code, label }` to `GUIDE_LANGS` (label in that language’s own script).
2. Create `i18n/{code}.json` (copy `en.json` as a base for incomplete locales; for Traditional Chinese start from `zh.json`).
3. Keep `i18n/build-bundle.py` `LANGS` and `js/site-config.js` `LANGS` in sync.
4. Rebuild:

    ```bash
    python i18n/build-bundle.py
    ```

5. Bump `js/cache-version.js` (or run `tool/update-version.py`) so browsers pick up `messages.js`.

## Fallback

Runtime lookup uses **selected → en → ko** (`zh-Hant` also tries `zh` before `en`).
Incomplete locales can ship chrome-only translations and fall back for the rest.

## UI switcher

`.lang-switch` navs are **rebuilt at runtime** as a dropdown from `GUIDE_LANGS`.
Pages may keep empty `<nav class="lang-switch" aria-label="Language"></nav>`.

`window.GuideI18n.languages` / `.supported` / `.fallbackLangs` expose the same config.

## Notes

- Freeform `*Body` arrays store per-lang keys (`ko`/`en`/`ja`/`zh`…); `js/content-body.js` follows the same fallback chain.
- Editorial CMS (`tool/lib/i18n_store.py`) still focuses on `ko`/`en`/`ja`/`zh`; other locales are runtime/bundle locales.
