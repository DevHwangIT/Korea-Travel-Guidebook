# Pages layout

## Page-owned media

Content pages that own their photos keep them next to the HTML:

```
pages/foods/meals/kimbap/oto/
  index.html
  media/
    cover.jpg      # 상호·대표
    body-1.jpg     # 본문 이미지
    body-2.jpg
```

Same pattern for dish hubs (`pages/foods/{meals|desserts}/{slug}/media/cover.jpg`),
souvenir items (`pages/souvenir/{slug}/media/`), and convenience details
(`pages/convenience-store/{slug}/media/`).

The shopping & fun hub is `pages/buy/index.html` (product + fun tabs).
`pages/shopping/index.html` and `pages/souvenir/index.html` redirect there.
Fun detail pages live under `pages/fun/{slug}/`
(e.g. `pcbang`, `noraebang`, `escape-room`, `jjimjilbang`, `lotte-world`, `everland`).

Canonical media: **page-owned** photos go in `pages/.../{slug}/media/`
(`cover.jpg`, `body-N.jpg`). Shared hub/menu/cover art stays under `Images/`.
Do not put souvenir/shop/fun covers back into empty `Images/shopping/` etc.

In i18n body blocks, image `src` is usually **site-root-relative**
(`pages/foods/meals/kimbap/oto/media/body-1.jpg`). Page-relative `media/body-1.jpg`
also works — `js/content-body.js` resolves both. Legacy `Images/...` paths still resolve via the site root prefix.

## Shared assets

Keep global/shared files under `Images/`:

- `Images/menu/` — main menu icons
- `Images/cover/` — covers, footer
- `Images/transport/` — maps
- `Images/foods/hub/` — food guide hub header

Admin uploads for shops / souvenir / convenience / section bodies write into the target page’s `media/` folder.
