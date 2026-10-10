// Render the default artwork: node art.js <dir> && node render.js <dir>
// Writes img-01.jpg … img-07.jpg (1920x1080) and ag-01.png … ag-10.png (1024x1024, transparent) into <dir>.
// Needs Playwright with a Chromium build (set CHROMIUM_PATH if it is not the default).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const dir = process.argv[2] || "out";
  const { frames, portraits } = JSON.parse(fs.readFileSync(path.join(dir, "frames.json"), "utf-8"));
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [name, svg] of Object.entries(frames)) {
    await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
    await page.screenshot({ path: path.join(dir, `${name}.jpg`), type: "jpeg", quality: 86 });
  }
  await page.setViewportSize({ width: 1024, height: 1024 });
  for (const [name, svg] of Object.entries(portraits)) {
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await page.screenshot({ path: path.join(dir, `${name}.png`), omitBackground: true });
  }
  await browser.close();
})();
