const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const OUT = path.join(__dirname);
fs.mkdirSync(OUT, { recursive: true });

async function run(page, label) {
  await page.addInitScript(() => {
    const d = new Date();
    const key =
      d.getFullYear() +
      "-" +
      String(d.getMonth() + 1).padStart(2, "0") +
      "-" +
      String(d.getDate()).padStart(2, "0");
    localStorage.setItem("korea-guide-welcome-hide-date", key);
  });

  await page.goto("http://127.0.0.1:8770/pages/travel-courses/?lang=ko", {
    waitUntil: "domcontentloaded",
    timeout: 30000,
  });

  const welcome = page.locator("[data-welcome-confirm]");
  if (await welcome.isVisible({ timeout: 2500 }).catch(() => false)) {
    await welcome.click();
  }

  await page.waitForSelector("[data-seoul-course]", {
    state: "attached",
    timeout: 15000,
  });
  const debug = await page.evaluate(() => {
    const chip = document.querySelector("[data-seoul-course]");
    const map = document.querySelector(".course-guide-map__canvas");
    const welcome = document.querySelector(".welcome-popup");
    function box(el) {
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return {
        w: r.width,
        h: r.height,
        top: r.top,
        display: s.display,
        vis: s.visibility,
        opacity: s.opacity,
        hiddenAttr: el.hasAttribute("hidden"),
      };
    }
    return {
      welcomeHidden: welcome ? welcome.hasAttribute("hidden") : "no-welcome",
      chip: box(chip),
      map: box(map),
      leaflet: !!document.querySelector(".leaflet-container"),
    };
  });
  console.error("DEBUG " + label, JSON.stringify(debug));

  await page.evaluate(() => {
    var chip = document.querySelector("[data-seoul-course]");
    if (chip && chip.getBoundingClientRect().height > 0) chip.click();
  });
  await page.waitForFunction(() => {
    var el = document.querySelector(".course-guide-map__canvas");
    if (!el) return false;
    if (el.getBoundingClientRect().height < 80) {
      el.style.height = "260px";
      el.style.minHeight = "260px";
    }
    el.scrollIntoView({ block: "center", inline: "nearest" });
    var r = el.getBoundingClientRect();
    return r.height > 80 && r.width > 80;
  }, { timeout: 15000 });
  await page.waitForTimeout(700);

  const mapShot = path.join(OUT, "quiz-overlay-" + label + "-map-before.png");
  await page.screenshot({ path: mapShot });

  await page.evaluate(() => {
    var btn = document.querySelector("[data-course-quiz-open]");
    if (btn) btn.click();
  });
  await page.waitForSelector(".course-quiz-dialog:not([hidden])", {
    timeout: 8000,
  });
  await page.waitForTimeout(400);

  const info = await page.evaluate(() => {
    const dialog = document.querySelector(".course-quiz-dialog");
    const canvas = document.querySelector(".course-guide-map__canvas");
    const zoom = document.querySelector(".leaflet-control-zoom-in");
    const ds = dialog ? getComputedStyle(dialog) : null;
    const r = canvas ? canvas.getBoundingClientRect() : null;
    const zr = zoom ? zoom.getBoundingClientRect() : null;
    function hit(x, y, name) {
      x = Math.round(Math.max(2, Math.min(innerWidth - 2, x)));
      y = Math.round(Math.max(2, Math.min(innerHeight - 2, y)));
      const el = document.elementFromPoint(x, y);
      return {
        name,
        x,
        y,
        tag: el ? el.tagName : null,
        cls: el ? String(el.className).slice(0, 120) : null,
        inDialog: !!(el && el.closest && el.closest(".course-quiz-dialog")),
        inLeaflet: !!(
          el &&
          el.closest &&
          (el.closest(".leaflet-pane") ||
            el.closest(".leaflet-control") ||
            el.closest(".leaflet-container") ||
            el.closest(".course-guide-map"))
        ),
      };
    }
    return {
      dialogParent: dialog && dialog.parentElement
        ? dialog.parentElement.tagName
        : null,
      dialogZ: ds ? ds.zIndex : null,
      dialogPos: ds ? ds.position : null,
      dialogHidden: dialog ? dialog.hasAttribute("hidden") : true,
      mapInView: !!(r && r.bottom > 0 && r.top < innerHeight && r.height > 40),
      mapTop: r ? r.top : null,
      mapH: r ? r.height : null,
      zoomTop: zr ? zr.top : null,
      hits: [
        r ? hit(r.left + r.width / 2, r.top + r.height / 2, "map-center") : { name: "map-center", missing: true },
        zr ? hit(zr.left + zr.width / 2, zr.top + zr.height / 2, "zoom-in") : { name: "zoom-in", missing: true },
        r ? hit(r.left + 18, r.top + 18, "map-tl") : { name: "map-tl", missing: true },
        hit(innerWidth / 2, innerHeight / 2, "viewport-center"),
      ],
    };
  });

  const overlayShot = path.join(OUT, "quiz-overlay-" + label + "-open.png");
  await page.screenshot({ path: overlayShot });
  return { label, info, mapShot, overlayShot };
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath:
      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  });
  let desk, mob;
  try {
    const deskPage = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    desk = await run(deskPage, "desk");
    await deskPage.close();
  } catch (e) {
    desk = { error: String(e && e.message ? e.message : e) };
  }
  try {
    const mobPage = await browser.newPage({ viewport: { width: 375, height: 812 } });
    mob = await run(mobPage, "mob");
    await mobPage.close();
  } catch (e) {
    mob = { error: String(e && e.message ? e.message : e) };
  }

  console.log(JSON.stringify({ desk, mob }, null, 2));
  await browser.close();
  const fail =
    (desk && desk.error) ||
    (mob && mob.error) ||
    (desk && desk.info && desk.info.hits && desk.info.hits.some((h) => h.inLeaflet)) ||
    (mob && mob.info && mob.info.hits && mob.info.hits.some((h) => h.inLeaflet));
  if (fail) process.exit(1);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
