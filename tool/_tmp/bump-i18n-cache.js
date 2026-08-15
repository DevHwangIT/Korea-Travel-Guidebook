const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..");
const langs = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"];
const bundle = {};
for (const lang of langs) {
  bundle[lang] = JSON.parse(
    fs.readFileSync(path.join(root, "i18n", lang + ".json"), "utf8")
  );
}
const out = "window.__I18N_MESSAGES__ = " + JSON.stringify(bundle) + ";\n";
fs.writeFileSync(path.join(root, "i18n", "messages.js"), out);
console.log(
  "messages.js bytes",
  out.length,
  "filterToggle ko",
  bundle.ko.transport.filterToggle
);

const now = new Date();
const pad = (n) => String(n).padStart(2, "0");
const ver =
  "" +
  now.getFullYear() +
  pad(now.getMonth() + 1) +
  pad(now.getDate()) +
  pad(now.getHours()) +
  pad(now.getMinutes()) +
  pad(now.getSeconds());

const cv =
  "/* Single source of truth for static asset cache-busting.\n" +
  " * Bump SITE_ASSET_VERSION via tool/update-version.py (or edit here),\n" +
  " * then HTML ?v= is applied automatically by that tool / apply-cache-bust.\n" +
  " */\n" +
  'window.SITE_ASSET_VERSION = "' +
  ver +
  '";\n';
fs.writeFileSync(path.join(root, "js", "cache-version.js"), cv);
console.log("version", ver);

// Light HTML ?v= replace for common asset refs (styles/js/i18n) — mirror cache_bust pattern.
const oldVer = "20260815111539";
let htmlUpdated = 0;
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (name === "node_modules" || name === ".git" || name === "tool") continue;
    const full = path.join(dir, name);
    const st = fs.statSync(full);
    if (st.isDirectory()) walk(full);
    else if (name.endsWith(".html")) {
      let txt = fs.readFileSync(full, "utf8");
      if (!txt.includes(oldVer) && !txt.includes("SITE_ASSET_VERSION")) {
        // still replace any ?v=YYYYMMDDHHMMSS near assets if matches old
      }
      if (txt.includes(oldVer)) {
        txt = txt.split(oldVer).join(ver);
        fs.writeFileSync(full, txt);
        htmlUpdated += 1;
      }
    }
  }
}
walk(root);
console.log("htmlUpdated", htmlUpdated);
