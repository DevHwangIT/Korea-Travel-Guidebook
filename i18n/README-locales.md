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
2. Create `i18n/{code}.json` (copy `en.json` as a base for incomplete locales; for Traditional Chinese start from `zh.json` then convert).
3. Keep in sync:
   - `i18n/build-bundle.py` `LANGS`
   - `js/site-config.js` `LANGS`
   - `tool/lib/i18n_store.py` `LANGS` / `BUNDLE_LANGS`
   - `tool/lib/translate.py` `TARGET_LANGS` (everything except `ko`)
4. Rebuild:

   ```bash
   python i18n/build-bundle.py
   ```

5. Bump `js/cache-version.js` (or run `tool/update-version.py`) so browsers pick up `messages.js`.

## CMS / auto-translate

Admin forms are **Korean-first**. On save, `tool/lib/translate.py` fills:

- Primary: `en` / `ja` / `zh` (from KO via DeepL / Google / OpenAI / deep-translator)
- Secondary: `zh-Hant` / `vi` / `th` / `ru` (same engines when supported; otherwise **copy English**)

Dish/shop/place/section scaffolds write keys into **all** `i18n_store.LANGS` JSON files. Body text blocks keep per-lang keys for the full set.

## Fallback (public site)

Runtime lookup uses **selected → (zh for zh-Hant) → en → ko**.
Incomplete locale strings can still fall back, but new CMS saves should populate every locale file.

## UI switcher

`.lang-switch` navs are **rebuilt at runtime** as a dropdown from `GUIDE_LANGS`.
Pages may keep empty `<nav class="lang-switch" aria-label="Language"></nav>`.

`window.GuideI18n.languages` / `.supported` / `.fallbackLangs` expose the same config.
