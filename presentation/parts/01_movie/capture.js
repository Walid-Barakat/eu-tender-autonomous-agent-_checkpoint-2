// Render every frame of movie.html deterministically and encode the film with its soundtrack.
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs');
(async () => {
  const TL = JSON.parse(fs.readFileSync('timeline.json')); const fps = TL.fps, n = Math.round(TL.duration * fps);
  const out = process.argv[2] || 'movie.mp4';
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-i', 'soundtrack.m4a',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('http://localhost:8770/movie.html?capture=1'); await p.waitForFunction(() => window.renderAt);
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const d = await p.evaluate(t => { window.renderAt(t); return window.frameJPEG(.9); }, i / fps + 0.0001);
    if (!ff.stdin.write(Buffer.from(d.slice(d.indexOf(',') + 1), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 250 === 0) console.log(`frame ${i}/${n} ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0), 's');
})();
