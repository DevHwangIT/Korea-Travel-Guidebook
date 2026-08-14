/**
 * Canonical site URL and shared SEO defaults.
 * Custom domain on GitHub Pages (served at site root /).
 * Change SITE_ORIGIN if the Pages URL or custom domain changes.
 */
window.SITE_CONFIG = {
  SITE_ORIGIN: "https://korea-guidebook.cloud",
  SITE_NAME: "Korea Travel Guide",
  DEFAULT_OG_IMAGE: "Images/cover/korea-cover.png",
  LANGS: ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"],
  /** Fallback only; first-visit pick is in js/i18n.js (match GUIDE_LANGS, else en / ko*). */
  DEFAULT_LANG: "en",
  /** Used as hreflang="x-default" target */
  X_DEFAULT_LANG: "en",

  /** Festivals hub uses VisitKorea links only (no TourAPI client key). */
  TOUR_API_KEY: "",
};
