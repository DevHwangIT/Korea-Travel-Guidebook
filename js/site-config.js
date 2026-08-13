/**
 * Canonical site URL and shared SEO defaults.
 * Custom domain on GitHub Pages (served at site root /).
 * Change SITE_ORIGIN if the Pages URL or custom domain changes.
 */
window.SITE_CONFIG = {
  SITE_ORIGIN: "https://korea-guidebook.cloud",
  SITE_NAME: "Korea Travel Guide",
  DEFAULT_OG_IMAGE: "Images/cover/korea-cover.png",
  LANGS: ["ko", "en", "ja", "zh"],
  DEFAULT_LANG: "ko",
  /** Used as hreflang="x-default" target */
  X_DEFAULT_LANG: "en",

  /**
   * Reserved for a future TourAPI integration on pages/festivals.
   * The festivals hub currently shows official VisitKorea links only —
   * no key is required.
   */
  TOUR_API_KEY: "",
};
