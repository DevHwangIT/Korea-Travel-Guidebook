# Adding a locale / i18n layout

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

## Source layout

Locale strings live under `i18n/` as **common + page groups** (not one file per HTML page):

```
i18n/
  common/{lang}.json           # common, cities, areas, restaurantFields, misc
  pages/
    home/{lang}.json
    before-trip/{lang}.json    # beforeTrip, prepTips
    travel-tips/{lang}.json    # tips
    travel-courses/{lang}.json # travelCourses (when present)
    apps/{lang}.json
    foods/{lang}.json          # dishes, restaurants, food hubs, …
    prep/{lang}.json
    transport/{lang}.json      # transport, places
    fun/{lang}.json
    shopping/{lang}.json       # shopping, souvenir, buyHub
    convenience/{lang}.json
    emergency/{lang}.json
    festivals/{lang}.json
    korean/{lang}.json
    misc/{lang}.json           # privacy, welcome, travelUtils
    _other/{lang}.json         # unknown top-level keys
  {lang}.json                  # assembled mirror (CMS-friendly)
  locale_routing.py            # key → folder map + merge helpers
  build-bundle.py              # merge → messages.js (+ refresh assembled)
  messages.js                  # runtime: window.__I18N_MESSAGES__
```

Ownership map is defined once in `i18n/locale_routing.py` (`KEY_OWNERS`).

Merge order for each language: residual `{lang}.json` (fallback) → `common/` → `pages/**`.

## Steps (new language)

1. Add `{ code, label }` to `GUIDE_LANGS` (label in that language’s own script).
2. Add `{code}.json` under `i18n/common/` and each needed `i18n/pages/<group>/` (copy from `en` as a base for incomplete locales; for Traditional Chinese start from `zh` then convert). Or copy assembled `en.json` then re-run the split script.
3. Keep in sync:
   - `i18n/build-bundle.py` / `i18n/locale_routing.py` `LANGS`
   - `js/site-config.js` `LANGS`
   - `tool/lib/i18n_store.py` `LANGS` / `BUNDLE_LANGS`
   - `tool/lib/translate.py` `TARGET_LANGS` (everything except `ko`)
4. Rebuild:

   ```bash
   python i18n/build-bundle.py
   ```

5. Bump `js/cache-version.js` (or run `tool/update-version.py`) so browsers pick up `messages.js`.

## One-time split (already done if folders exist)

```bash
python tool/migrate_i18n_split.py          # write sources + verify
python tool/migrate_i18n_split.py --dry-run
```

## CMS / auto-translate

Admin forms are **Korean-first**. On save, `tool/lib/translate.py` fills:

- Primary: `en` / `ja` / `zh` (from KO via DeepL / Google / OpenAI / deep-translator)
- Secondary: `zh-Hant` / `vi` / `th` / `ru` (same engines when supported; otherwise **copy English**)

`i18n_store.load_*` returns the **merged** dict. `save_*` routes each top-level key into the correct `common/` or `pages/<group>/` file and refreshes the assembled `i18n/{lang}.json` mirror, then callers rebuild `messages.js` as before.

Dish/shop/place/section scaffolds write keys into **all** `i18n_store.LANGS`. Body text blocks keep per-lang keys for the full set.

## Fallback (public site)

Runtime lookup uses **selected → (zh for zh-Hant) → en → ko**.
Incomplete locale strings can still fall back, but new CMS saves should populate every locale file.

## UI switcher

`.lang-switch` navs are **rebuilt at runtime** as a dropdown from `GUIDE_LANGS`.
Pages may keep empty `<nav class="lang-switch" aria-label="Language"></nav>`.

`window.GuideI18n.languages` / `.supported` / `.fallbackLangs` expose the same config.
