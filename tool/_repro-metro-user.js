/**
 * Reproduce metro like a real user: collapsed filter, open, check 지하철.
 * Also reproduce the "already checked via localStorage but blank map" boot bug.
 */
const fs = require("fs");
const path = require("path");
const http = require("http");

const ROOT = path.resolve(__dirname, "..");
const PORT = 3409;
const URL = `http://127.0.0.1:${PORT}/pages/transportation/index.html?lang=ko`;
const OUT = path.join(ROOT, "tool", "_tmp");
fs.mkdirSync(OUT, { recursive: true });

function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function countCanvasOpaque(page, selectorHint) {
  return page.evaluate((hint) => {
    const canvases = [...document.querySelectorAll("canvas")];
    return canvases.map((c) => {
      const parent = (c.parentElement && c.parentElement.className) || "";
      let opaque = 0;
      try {
        const ctx = c.getContext("2d", { willReadFrequently: true });
        const { width: w, height: h } = c;
        if (!w || !h) return { parent, opaque: 0, w, h };
        const step = 4;
        const data = ctx.getImageData(0, 0, w, h).data;
        for (let i = 3; i < data.length; i += 4 * step) {
          if (data[i] > 20) opaque++;
        }
      } catch (e) {
        return { parent, opaque: -1, err: String(e) };
      }
      return { parent, opaque, w: c.width, h: c.height, hint };
    });
  }, selectorHint);
}

async function metroStats(page) {
  return page.evaluate(() => {
    const checks = [...document.querySelectorAll("[data-places-metro-filter]")].map((i) => [
      i.getAttribute("data-places-metro-filter"),
      i.checked,
      i.offsetParent !== null,
    ]);
    const subs = [...document.querySelectorAll("[data-places-metro-sub]")].map((el) => ({
      hidden: el.hidden,
      display: getComputedStyle(el).display,
    }));
    const legend = document.querySelector("[data-places-legend]");
    const hint = document.querySelector("[data-places-hint]");
    const stationDots = document.querySelectorAll(".places-metro-station__dot").length;
    const lineLayers =
      window.__metroDebug && window.__metroDebug.lineCount != null
        ? window.__metroDebug.lineCount
        : null;
    const zoom = window.__metroDebug && window.__metroDebug.zoom;
    const loadState = window.__metroDebug && window.__metroDebug.loadState;
    const base = window.__metroDebug && window.__metroDebug.base;
    return {
      collapsed: legend && legend.classList.contains("is-collapsed"),
      checks,
      subs,
      hint: hint ? { text: hint.textContent.trim(), hidden: hint.hidden } : null,
      stationDots,
      lineLayers,
      zoom,
      loadState,
      base,
      ls: localStorage.getItem("korea-guide-places-type-filters"),
      filterOpen: localStorage.getItem("korea-guide-places-filter-open"),
      errors: window.__pageErrors || [],
    };
  });
}

async function injectDebug(page) {
  await page.evaluate(() => {
    window.__pageErrors = [];
    window.addEventListener("error", (e) => {
      window.__pageErrors.push(String(e.message || e));
    });
    // Hook into internals via DOM/Leaflet after load — expose via periodic poll
    const expose = () => {
      const mapEl = document.getElementById("places-map");
      // Walk leaflet map if available
      let map = null;
      if (mapEl && mapEl._leaflet_id != null) {
        // Leaflet stores maps in L.Map instances; find via panes
      }
      const overlay = document.querySelector(".leaflet-overlay-pane");
      const metroPane = document.querySelector(".leaflet-metroStations-pane");
      const lineCanvas = overlay && overlay.querySelector("canvas");
      const stationCanvas = metroPane && metroPane.querySelector("canvas");
      window.__metroDebug = {
        zoom: (function () {
          try {
            // Approximate from leaflet control label
            const z = document.querySelector(".leaflet-control-zoom-in");
            return z ? "unknown" : "unknown";
          } catch (e) {
            return null;
          }
        })(),
        hasOverlayCanvas: !!lineCanvas,
        hasStationCanvas: !!stationCanvas,
        stationDots: document.querySelectorAll(".places-metro-station__dot").length,
        metroPaneKids: metroPane ? metroPane.children.length : 0,
      };
    };
    setInterval(expose, 200);
  });
}

async function main() {
  let puppeteer;
  try {
    puppeteer = require("puppeteer");
  } catch (e) {
    // use npx cache path via dynamic import of puppeteer from global
    console.error("Need puppeteer locally");
    process.exit(1);
  }

  // Probe server
  await new Promise((resolve, reject) => {
    http
      .get(URL, (res) => {
        res.resume();
        resolve(res.statusCode);
      })
      .on("error", reject);
  });

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--window-size=1400,900"],
    defaultViewport: { width: 1400, height: 900 },
  });
  const page = await browser.newPage();
  const net = [];
  page.on("response", (res) => {
    const u = res.url();
    if (u.includes("/data/metro/") || u.includes("places-map.js")) {
      net.push({ url: u.split("/").pop(), status: res.status() });
    }
  });
  page.on("pageerror", (err) => {
    console.log("PAGEERROR", err.message);
  });
  page.on("console", (msg) => {
    if (msg.type() === "error") console.log("CONSOLE", msg.text());
  });

  const report = { scenarios: {} };

  // --- Scenario A: fresh user, collapsed filter ---
  await page.goto(URL, { waitUntil: "networkidle2", timeout: 60000 });
  await page.evaluate(() => {
    localStorage.removeItem("korea-guide-places-type-filters");
    localStorage.removeItem("korea-guide-places-filter-open");
  });
  await page.reload({ waitUntil: "networkidle2", timeout: 60000 });
  await wait(1500);
  await injectDebug(page);

  report.scenarios.freshCollapsed = await metroStats(page);

  // Open filter like a user
  await page.click("[data-places-filter-toggle]");
  await wait(400);
  report.scenarios.afterOpenFilter = await metroStats(page);

  // Check 지하철
  const metroCb = await page.$('[data-places-metro-filter="metro"]');
  if (!metroCb) {
    report.scenarios.metroCheckboxMissing = true;
  } else {
    await metroCb.click();
    await wait(3500);
    report.scenarios.afterCheckMetro = await metroStats(page);
    report.scenarios.afterCheckMetro.canvases = await countCanvasOpaque(page, "after-check");
    await page.screenshot({
      path: path.join(OUT, "metro-after-check.png"),
      fullPage: false,
    });
  }

  // --- Scenario B: localStorage metro already on, no toggle ---
  await page.evaluate(() => {
    localStorage.setItem(
      "korea-guide-places-type-filters",
      JSON.stringify({
        city: true,
        nature: true,
        heritage: true,
        airport: true,
        info: true,
        locker: true,
        port: true,
        metro: true,
        metroLines: true,
        metroStations: true,
      })
    );
    localStorage.setItem("korea-guide-places-filter-open", "1");
  });
  await page.reload({ waitUntil: "networkidle2", timeout: 60000 });
  await wait(3500);
  report.scenarios.bootWithMetroOnNoToggle = await metroStats(page);
  report.scenarios.bootWithMetroOnNoToggle.canvases = await countCanvasOpaque(
    page,
    "boot-metro-on"
  );
  await page.screenshot({
    path: path.join(OUT, "metro-boot-already-on.png"),
    fullPage: false,
  });

  // Toggle off/on to see if that restores
  await page.click('[data-places-metro-filter="metro"]');
  await wait(500);
  await page.click('[data-places-metro-filter="metro"]');
  await wait(3500);
  report.scenarios.afterRetoggle = await metroStats(page);
  report.scenarios.afterRetoggle.canvases = await countCanvasOpaque(page, "retoggle");
  await page.screenshot({
    path: path.join(OUT, "metro-after-retoggle.png"),
    fullPage: false,
  });

  // --- Scenario C: poisoned localStorage (lines+stations both false) ---
  await page.evaluate(() => {
    localStorage.setItem(
      "korea-guide-places-type-filters",
      JSON.stringify({
        city: true,
        nature: true,
        heritage: true,
        airport: true,
        info: true,
        locker: true,
        port: true,
        metro: true,
        metroLines: false,
        metroStations: false,
      })
    );
  });
  await page.reload({ waitUntil: "networkidle2", timeout: 60000 });
  await wait(2500);
  report.scenarios.poisonedBothOff = await metroStats(page);
  report.scenarios.poisonedBothOff.canvases = await countCanvasOpaque(page, "poison");

  // Check metro click when already checked (no change event)
  await page.evaluate(() => {
    const input = document.querySelector('[data-places-metro-filter="metro"]');
    // click when already checked → unchecks
  });

  report.net = net.slice(-30);
  fs.writeFileSync(path.join(OUT, "metro-repro-report.json"), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
