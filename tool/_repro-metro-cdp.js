/**
 * Real-user metro repro via Chrome CDP (no local puppeteer package).
 */
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");
const ROOT = path.resolve(__dirname, "..");
const PORT = 3409;
const PAGE = `http://127.0.0.1:${PORT}/pages/transportation/index.html?lang=ko`;
const OUT = path.join(ROOT, "tool", "_tmp");
const CDP_PORT = 9229;
const CHROME =
  process.env.CHROME_PATH ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

fs.mkdirSync(OUT, { recursive: true });

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (res) => {
        let d = "";
        res.on("data", (c) => (d += c));
        res.on("end", () => {
          try {
            resolve(JSON.parse(d));
          } catch (e) {
            reject(e);
          }
        });
      })
      .on("error", reject);
  });
}

class Cdp {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(typeof ev.data === "string" ? ev.data : String(ev.data));
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result);
      }
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async eval(expression, awaitPromise = true) {
    const r = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise,
    });
    if (r.exceptionDetails) {
      throw new Error(JSON.stringify(r.exceptionDetails));
    }
    return r.result && r.result.value;
  }
}

async function waitForWs(url, tries = 40) {
  for (let i = 0; i < tries; i++) {
    try {
      const list = await fetchJson(url);
      const page = list.find((t) => t.type === "page") || list[0];
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch (_) {}
    await sleep(250);
  }
  throw new Error("CDP not ready");
}

async function main() {
  if (typeof globalThis.WebSocket !== "function") {
    console.error("Need Node WebSocket (Node 22+)");
    process.exit(1);
  }

  const userData = path.join(OUT, "chrome-metro-profile");
  fs.mkdirSync(userData, { recursive: true });
  const chrome = spawn(
    CHROME,
    [
      `--remote-debugging-port=${CDP_PORT}`,
      `--user-data-dir=${userData}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-extensions",
      "--window-size=1400,900",
      "about:blank",
    ],
    { stdio: "ignore" }
  );

  try {
    const wsUrl = await waitForWs(`http://127.0.0.1:${CDP_PORT}/json`);
    const ws = new globalThis.WebSocket(wsUrl);
    await new Promise((res, rej) => {
      ws.addEventListener("open", () => res());
      ws.addEventListener("error", (e) => rej(e));
    });
    const cdp = new Cdp(ws);
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Network.enable");

    const net = [];
    // Track metro fetches via evaluate polling of performance resource timing

    async function goto(url) {
      await cdp.send("Page.navigate", { url });
      await sleep(2500);
    }

    async function stats() {
      return cdp.eval(`(function(){
        const legend = document.querySelector('[data-places-legend]');
        const hint = document.querySelector('[data-places-hint]');
        const checks = [...document.querySelectorAll('[data-places-metro-filter]')].map(i => ({
          key: i.getAttribute('data-places-metro-filter'),
          checked: i.checked,
          visible: !!(i.offsetWidth || i.offsetHeight || i.getClientRects().length)
        }));
        const subs = [...document.querySelectorAll('[data-places-metro-sub]')].map(el => ({
          hiddenAttr: el.hidden,
          display: getComputedStyle(el).display
        }));
        const stationDots = document.querySelectorAll('.places-metro-station__dot').length;
        const metroPane = document.querySelector('.leaflet-metroStations-pane');
        const overlay = document.querySelector('.leaflet-overlay-pane');
        function opaque(canvas){
          if (!canvas) return null;
          try {
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            const w = canvas.width, h = canvas.height;
            if (!w || !h) return { opaque: 0, w, h };
            const data = ctx.getImageData(0,0,w,h).data;
            let o = 0;
            for (let i=3;i<data.length;i+=16) if (data[i] > 20) o++;
            return { opaque: o, w, h };
          } catch(e){ return { opaque: -1, err: String(e) }; }
        }
        const lineCanvas = overlay && overlay.querySelector('canvas');
        const stationCanvas = metroPane && metroPane.querySelector('canvas');
        const zoomLabel = document.querySelector('.leaflet-control-zoom');
        // Leaflet map zoom via internal if present
        let zoom = null;
        try {
          const mapDiv = document.getElementById('places-map');
          if (mapDiv && mapDiv._leaflet_id != null) {
            // find map object from Leaflet
            for (const k of Object.keys(window)) {}
          }
          // Heuristic: look at L DomUtil — use PlacesMap region
        } catch(e){}
        // Use leaflet pane transform as proxy — better: read from L
        try {
          if (window.L && L.Map) {
            const maps = [];
            document.querySelectorAll('.leaflet-container').forEach(el => {
              // Leaflet 1.x stores map in el
            });
          }
        } catch(e){}
        const resources = performance.getEntriesByType('resource')
          .filter(r => /metro|places-map/.test(r.name))
          .map(r => ({ name: r.name.split('/').pop(), dur: Math.round(r.duration) }));
        return {
          collapsed: !!(legend && legend.classList.contains('is-collapsed')),
          checks, subs,
          hint: hint ? { text: (hint.textContent||'').trim(), hidden: hint.hidden } : null,
          stationDots,
          metroPaneKids: metroPane ? metroPane.children.length : 0,
          lineOpaque: opaque(lineCanvas),
          stationOpaque: opaque(stationCanvas),
          ls: localStorage.getItem('korea-guide-places-type-filters'),
          filterOpen: localStorage.getItem('korea-guide-places-filter-open'),
          resources,
          href: location.href
        };
      })()`);
    }

    async function shot(name) {
      const r = await cdp.send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(OUT, name), Buffer.from(r.data, "base64"));
    }

    async function clickSel(sel) {
      await cdp.eval(`document.querySelector(${JSON.stringify(sel)}).click()`);
    }

    const report = {};

    // Seed welcome-hide, then fresh user
    await goto(PAGE);
    await cdp.eval(`localStorage.removeItem('korea-guide-places-type-filters');
      localStorage.removeItem('korea-guide-places-filter-open');
      localStorage.setItem('korea-guide-welcome-hide-date', new Date().toISOString().slice(0,10));`);
    await goto(PAGE);
    await sleep(1500);
    await cdp.eval(`(function(){ var b=document.querySelector('[data-welcome-confirm]'); if(b) b.click(); })()`);
    await sleep(300);
    report.freshCollapsed = await stats();
    await shot("01-fresh-collapsed.png");

    await clickSel("[data-places-filter-toggle]");
    await sleep(400);
    report.afterOpenFilter = await stats();
    await shot("02-filter-open.png");

    // Nested should be hidden until metro on
    report.nestedHiddenWhileMetroOff = report.afterOpenFilter.subs;

    await clickSel('[data-places-metro-filter="metro"]');
    await sleep(4500);
    report.afterCheckMetro = await stats();
    await shot("03-after-metro-check.png");

    // B: boot with metro already on in LS
    await cdp.eval(`localStorage.setItem('korea-guide-places-type-filters', JSON.stringify({
      city:true,nature:true,heritage:true,airport:true,info:true,locker:true,port:true,
      metro:true,metroLines:true,metroStations:true
    })); localStorage.setItem('korea-guide-places-filter-open','1');
    localStorage.setItem('korea-guide-welcome-hide-date', new Date().toISOString().slice(0,10));`);
    await goto(PAGE);
    await sleep(4500);
    report.bootMetroAlreadyOn = await stats();
    await shot("04-boot-metro-already-on.png");

    // C: poisoned both off — must heal
    await cdp.eval(`localStorage.setItem('korea-guide-places-type-filters', JSON.stringify({
      city:true,nature:true,heritage:true,airport:true,info:true,locker:true,port:true,
      metro:true,metroLines:false,metroStations:false
    }));
    localStorage.setItem('korea-guide-welcome-hide-date', new Date().toISOString().slice(0,10));`);
    await goto(PAGE);
    await sleep(4500);
    report.poisonedBothOffHealed = await stats();
    await shot("06-poisoned-healed.png");

    fs.writeFileSync(
      path.join(OUT, "metro-repro-report.json"),
      JSON.stringify(report, null, 2)
    );
    console.log(JSON.stringify(report, null, 2));
    ws.close();
  } finally {
    try {
      chrome.kill();
    } catch (_) {}
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
