// Default artwork for "The Search": original flat illustrations, rendered to PNG/JPG.
// One recurring protagonist across eras, ten agent robots. No real logos or characters.
const fs = require("fs");
const path = require("path");
const OUT = process.argv[2] || "out";
fs.mkdirSync(OUT, { recursive: true });

const SKIN = "#c68e63", SKIN_D = "#a8724c", HAIR = "#2b211c";
// Walid's cartoon face, used by the protagonist and by every mini-me agent. Adjust here only.
const FACE = { skin: SKIN, skinDark: SKIN_D, hair: HAIR, greyStreak: true, glasses: true, beard: false, moustache: false };

// Face drawn around (0,0), about 150 x 200 px. mood: neutral | happy | worried | tired
function face({ mood = "happy", grey = FACE.greyStreak, glasses = FACE.glasses, beard = FACE.beard, hairless = false, hairColor = null } = {}) {
  const hair = hairColor || FACE.hair, sk = FACE.skin, skd = FACE.skinDark;
  const mouth = { neutral: "M-18,46 Q0,54 18,46", happy: "M-24,40 Q0,66 24,40", worried: "M-18,54 Q0,42 18,54", tired: "M-16,50 L16,50" }[mood];
  const brows = mood === "worried" || mood === "tired"
    ? `<path d="M-46,-14 L-18,-22 M18,-22 L46,-14" stroke="${hair}" stroke-width="7" stroke-linecap="round"/>`
    : `<path d="M-46,-20 Q-32,-28 -18,-22 M18,-22 Q32,-28 46,-20" stroke="${hair}" stroke-width="7" stroke-linecap="round" fill="none"/>`;
  const eyes = mood === "tired"
    ? `<path d="M-42,2 Q-32,8 -22,2 M22,2 Q32,8 42,2" stroke="#1d1d1d" stroke-width="6" fill="none" stroke-linecap="round"/>`
    : `<ellipse cx="-32" cy="2" rx="7" ry="9" fill="#1d1d1d"/><ellipse cx="32" cy="2" rx="7" ry="9" fill="#1d1d1d"/>`;
  return `<circle cx="-74" cy="6" r="16" fill="${skd}"/><circle cx="74" cy="6" r="16" fill="${skd}"/>
    <ellipse cx="0" cy="0" rx="74" ry="86" fill="${sk}"/>
    ${beard ? `<path d="M-70,10 Q-66,92 0,96 Q66,92 70,10 Q54,60 0,64 Q-54,60 -70,10Z" fill="${hair}" opacity=".85"/>` : ""}
    ${FACE.moustache ? `<path d="M-30,36 Q0,24 30,36 Q0,44 -30,36Z" fill="${hair}"/>` : ""}
    ${hairless ? "" : `<path d="M-76,-12 Q-84,-96 0,-98 Q84,-96 76,-12 Q70,-54 30,-60 Q-20,-46 -76,-12Z" fill="${hair}"/>`}
    ${grey && !hairless ? `<path d="M30,-60 Q60,-58 72,-30" stroke="#b9b4ae" stroke-width="10" fill="none"/>` : ""}
    ${brows}${eyes}
    ${glasses ? `<g fill="none" stroke="#222" stroke-width="5"><rect x="-56" y="-14" width="44" height="32" rx="10"/><rect x="12" y="-14" width="44" height="32" rx="10"/><path d="M-12,0 L12,0"/></g>` : ""}
    <path d="M0,4 Q-8,26 0,30" stroke="${skd}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="${mouth}" stroke="#5a2a20" stroke-width="7" fill="none" stroke-linecap="round"/>`;
}

// ---------------------------------------------------------------- protagonist
// (x, y) = centre of feet. s = scale (1 => about 560 px tall). Options vary by era.
function person({ x, y, s = 1, shirt = "#3a7ca5", pants = "#33414f", fur = false, glasses = false, grey = false,
  beard = false, tie = null, mood = "neutral", arms = "down", hide = false, holding = "" }) {
  const head = `<g transform="translate(0,-470)">${face({ mood, grey, glasses, beard, hairColor: grey ? "#6b6560" : null })}</g>`;
  const torsoFill = fur ? "#b07a45" : shirt;
  const furSpots = fur ? `<g fill="#7c5230"><circle cx="-40" cy="-300" r="12"/><circle cx="30" cy="-260" r="14"/><circle cx="-10" cy="-210" r="10"/><circle cx="50" cy="-340" r="9"/></g>` : "";
  const armL = { down: "rotate(14 -78 -350)", up: "rotate(150 -78 -350)", forward: "rotate(-60 -78 -350)", shrug: "rotate(60 -78 -350)" }[arms];
  const armR = { down: "rotate(-14 78 -350)", up: "rotate(-150 78 -350)", forward: "rotate(60 78 -350)", shrug: "rotate(-60 78 -350)" }[arms];
  const sleeve = fur ? SKIN : torsoFill;
  const legs = hide ? "" : `<rect x="-62" y="-180" width="52" height="180" rx="20" fill="${fur ? SKIN : pants}"/><rect x="10" y="-180" width="52" height="180" rx="20" fill="${fur ? SKIN : pants}"/>
    <rect x="-72" y="-22" width="66" height="26" rx="12" fill="#2a2420"/><rect x="6" y="-22" width="66" height="26" rx="12" fill="#2a2420"/>`;
  const tieSvg = tie ? `<path d="M0,-372 L-14,-350 L0,-250 L14,-350Z" fill="${tie}"/>` : "";
  return `<g transform="translate(${x},${y}) scale(${s})">
    ${legs}
    <g transform="${armL}"><rect x="-100" y="-370" width="44" height="170" rx="22" fill="${sleeve}"/><circle cx="-78" cy="-196" r="24" fill="${SKIN}"/></g>
    <g transform="${armR}"><rect x="56" y="-370" width="44" height="170" rx="22" fill="${sleeve}"/><circle cx="78" cy="-196" r="24" fill="${SKIN}"/></g>
    <path d="M-92,-200 L-84,-360 Q0,-392 84,-360 L92,-200 Q0,-176 -92,-200Z" fill="${torsoFill}"/>
    ${fur ? `<path d="M-84,-360 L40,-200 L92,-200 L84,-360 Q0,-392 -84,-360Z" fill="#9a6838" opacity=".6"/>` : ""}
    ${furSpots}${tieSvg}
    <rect x="-26" y="-400" width="52" height="40" fill="${SKIN_D}"/>
    ${head}
    ${holding}
  </g>`;
}

// ---------------------------------------------------------------- agent robot
const AGENT_COLORS = ["#2f8fd6", "#22a39a", "#e0803a", "#8a63d2", "#d4a72c", "#d1495b", "#3c9a5f", "#3a5a98", "#e05a9a", "#f07f2a"];
function robot({ x, y, s = 1, color = "#2f8fd6", label = "", mood = "happy", prop = "" }) {
  return `<g transform="translate(${x},${y}) scale(${s})">
    <rect x="-70" y="-60" width="34" height="70" rx="16" fill="${color}" opacity=".9"/><rect x="36" y="-60" width="34" height="70" rx="16" fill="${color}" opacity=".9"/>
    <rect x="-90" y="-220" width="180" height="170" rx="40" fill="${color}"/>
    <rect x="-56" y="-180" width="112" height="78" rx="22" fill="#eaf6ff" opacity=".92"/>
    ${label ? `<text x="0" y="-128" text-anchor="middle" font-family="DejaVu Sans Mono, monospace" font-weight="700" font-size="34" fill="#0f2236">${label}</text>` : ""}
    <g transform="translate(0,-330)">
      <line x1="0" y1="-140" x2="0" y2="-172" stroke="#0f2236" stroke-width="8"/><circle cx="0" cy="-180" r="16" fill="#ffd34d"/>
      <rect x="-118" y="-140" width="236" height="230" rx="70" fill="${color}"/>
      <circle cx="0" cy="-22" r="96" fill="#dff3ff"/>
      <g transform="translate(0,-22) scale(.98)">${face({ mood })}</g>
      <circle cx="0" cy="-22" r="96" fill="none" stroke="#0f2236" stroke-width="7"/>
      <path d="M-60,-104 Q-30,-116 -6,-112" stroke="#fff" stroke-width="8" fill="none" opacity=".7" stroke-linecap="round"/>
      <rect x="-136" y="-50" width="22" height="64" rx="10" fill="${color}"/><rect x="114" y="-50" width="22" height="64" rx="10" fill="${color}"/>
    </g>
    <rect x="-128" y="-200" width="38" height="120" rx="19" fill="${color}" transform="rotate(16 -110 -200)"/>
    <rect x="90" y="-200" width="38" height="120" rx="19" fill="${color}" transform="rotate(-16 110 -200)"/>
    ${prop}
  </g>`;
}

// Props for the portraits, drawn in the robot's local coordinates (right-hand side).
const PROPS = [
  // 1 sieve
  `<g transform="translate(170,-150)"><ellipse cx="0" cy="0" rx="90" ry="30" fill="#c9d3dc"/><path d="M-90,0 Q0,110 90,0" fill="#9fb0bf"/><g stroke="#5f7383" stroke-width="3">${Array.from({ length: 7 }, (_, i) => `<line x1="${-60 + i * 20}" y1="8" x2="${-50 + i * 17}" y2="58"/>`).join("")}</g><rect x="88" y="-8" width="80" height="16" rx="8" fill="#5f7383"/></g>`,
  // 2 three trays
  `<g transform="translate(180,-260)">${[0, 1, 2].map(i => `<g transform="translate(0,${i * 70})"><path d="M-80,0 L80,0 L66,46 L-66,46Z" fill="${["#9aa5b1", "#f2c14e", "#4caf7a"][i]}"/><text x="0" y="34" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="22" fill="#0f2236">${["ARCHIVE", "WATCH", "ADVANCE"][i]}</text></g>`).join("")}</g>`,
  // 3 tool belt with wrench
  `<g><rect x="-100" y="-120" width="200" height="34" rx="10" fill="#6b4b2e"/><g transform="translate(150,-210) rotate(30)"><rect x="-12" y="-80" width="24" height="150" rx="10" fill="#9aa5b1"/><path d="M-40,-90 a40,40 0 1,1 80,0 l-22,0 l0,26 l-36,0 l0,-26Z" fill="#9aa5b1"/></g></g>`,
  // 4 scissors and paper
  `<g transform="translate(170,-200)"><rect x="-70" y="-90" width="120" height="160" fill="#fff" stroke="#c9d3dc" stroke-width="4"/><g stroke="#c9d3dc" stroke-width="6">${[0, 1, 2, 3, 4].map(i => `<line x1="-54" y1="${-60 + i * 26}" x2="34" y2="${-60 + i * 26}"/>`).join("")}</g><g transform="translate(60,40) rotate(-30)"><circle cx="-30" cy="40" r="22" fill="none" stroke="#e0803a" stroke-width="10"/><circle cx="30" cy="40" r="22" fill="none" stroke="#e0803a" stroke-width="10"/><path d="M-18,22 L40,-70 M18,22 L-40,-70" stroke="#9aa5b1" stroke-width="12" stroke-linecap="round"/></g></g>`,
  // 5 card catalogue
  `<g transform="translate(180,-200)"><rect x="-90" y="-100" width="180" height="200" rx="10" fill="#8b5e34"/>${[0, 1, 2].map(r => [0, 1].map(c => `<rect x="${-78 + c * 84}" y="${-88 + r * 64}" width="72" height="52" rx="6" fill="#b07a45"/><rect x="${-52 + c * 84}" y="${-66 + r * 64}" width="20" height="8" rx="4" fill="#f2d8b0"/>`).join("")).join("")}</g>`,
  // 6 gate and key
  `<g transform="translate(180,-200)"><rect x="-90" y="-110" width="18" height="220" fill="#5f7383"/><rect x="72" y="-110" width="18" height="220" fill="#5f7383"/>${[0, 1, 2, 3].map(i => `<rect x="${-62 + i * 36}" y="-90" width="12" height="190" fill="#9aa5b1"/>`).join("")}<rect x="-90" y="-110" width="180" height="16" fill="#5f7383"/><g transform="translate(20,140) rotate(-20)"><circle cx="-40" cy="0" r="26" fill="none" stroke="#d4a72c" stroke-width="12"/><rect x="-16" y="-7" width="100" height="14" fill="#d4a72c"/><rect x="60" y="0" width="12" height="26" fill="#d4a72c"/></g></g>`,
  // 7 three small helpers
  `<g transform="translate(190,-120)">${[[-70, "#3c9a5f"], [0, "#2f8fd6"], [70, "#e0803a"]].map(([dx, c]) => `<g transform="translate(${dx},0)"><rect x="-30" y="-70" width="60" height="60" rx="16" fill="${c}"/><rect x="-20" y="-58" width="40" height="22" rx="8" fill="#0f2236"/><circle cx="-8" cy="-47" r="5" fill="#7ef0ff"/><circle cx="8" cy="-47" r="5" fill="#7ef0ff"/><rect x="-22" y="-10" width="44" height="40" rx="10" fill="${c}"/></g>`).join("")}</g>`,
  // 8 compass
  `<g transform="translate(180,-200)"><circle r="90" fill="#f4efe6" stroke="#3a5a98" stroke-width="14"/><path d="M0,-70 L18,0 L0,70 L-18,0Z" fill="#d1495b"/><path d="M0,0 L18,0 L0,70 L-18,0Z" fill="#3a5a98"/><circle r="10" fill="#0f2236"/><text x="0" y="-48" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="24" fill="#0f2236">N</text></g>`,
  // 9 megaphone
  `<g transform="translate(160,-230) rotate(-18)"><path d="M0,-30 L120,-90 L120,90 L0,30Z" fill="#f4efe6" stroke="#e05a9a" stroke-width="10"/><rect x="-40" y="-30" width="44" height="60" rx="8" fill="#e05a9a"/><path d="M150,-40 Q175,0 150,40 M170,-70 Q210,0 170,70" stroke="#e05a9a" stroke-width="8" fill="none" stroke-linecap="round"/></g>`,
  // 10 dice and scales
  `<g transform="translate(190,-220)"><line x1="0" y1="-90" x2="0" y2="70" stroke="#5f7383" stroke-width="10"/><line x1="-90" y1="-70" x2="90" y2="-70" stroke="#5f7383" stroke-width="10"/><path d="M-120,10 L-60,10 L-90,-70Z M60,10 L120,10 L90,-70Z" fill="none" stroke="#5f7383" stroke-width="5"/><path d="M-120,10 Q-90,40 -60,10Z M60,10 Q90,40 120,10Z" fill="#d4a72c"/><rect x="-40" y="70" width="80" height="16" rx="6" fill="#5f7383"/><g transform="translate(-40,150) rotate(-12)"><rect x="-34" y="-34" width="68" height="68" rx="12" fill="#fff" stroke="#0f2236" stroke-width="5"/><circle cx="-14" cy="-14" r="7" fill="#0f2236"/><circle cx="14" cy="14" r="7" fill="#0f2236"/><circle r="7" fill="#0f2236"/></g><g transform="translate(50,150) rotate(14)"><rect x="-34" y="-34" width="68" height="68" rx="12" fill="#fff" stroke="#0f2236" stroke-width="5"/><circle cx="-14" cy="-14" r="7" fill="#0f2236"/><circle cx="14" cy="14" r="7" fill="#0f2236"/><circle cx="14" cy="-14" r="7" fill="#0f2236"/><circle cx="-14" cy="14" r="7" fill="#0f2236"/></g></g>`,
];

// ---------------------------------------------------------------- frames
const W = 1920, H = 1080;
const svg = (body, defs = "") => `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><defs>${defs}</defs>${body}</svg>`;
const lg = (id, stops, x2 = 0, y2 = 1) => `<linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">${stops.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join("")}</linearGradient>`;
const rg = (id, stops) => `<radialGradient id="${id}">${stops.map(([o, c, a = 1]) => `<stop offset="${o}" stop-color="${c}" stop-opacity="${a}"/>`).join("")}</radialGradient>`;

const frames = {};

// IMG-01 Stone Age
frames["img-01"] = svg(`
  <rect width="${W}" height="${H}" fill="url(#cave)"/>
  <path d="M1380,1080 L1380,420 Q1600,180 1920,260 L1920,1080Z" fill="url(#sky)"/>
  <circle cx="1720" cy="380" r="70" fill="#ffe2a8"/>
  <path d="M1380,1080 L1380,420 Q1600,180 1920,260 L1920,0 L1340,0Z" fill="#2a1c13" opacity=".0"/>
  <path d="M0,0 L1920,0 L1920,260 Q1600,180 1380,420 L1380,1080 L0,1080Z" fill="url(#rock)" opacity=".55"/>
  <g stroke="#7a4a2a" stroke-width="7" fill="none" stroke-linecap="round" opacity=".8">
    <path d="M220,250 q40,-40 90,0 q30,20 60,0 M250,250 l-10,50 M300,250 l0,50 M350,250 l10,50"/>
    <path d="M520,190 q50,-50 110,0 M540,190 l-10,46 M610,190 l10,46"/>
    <path d="M420,330 l40,-60 l40,60 M440,300 l40,0"/>
  </g>
  <rect y="880" width="${W}" height="200" fill="#3a271a"/>
  <g transform="translate(300,900)">
    <rect x="-90" y="-20" width="180" height="30" rx="14" fill="#5a3a22" transform="rotate(12)"/><rect x="-90" y="-20" width="180" height="30" rx="14" fill="#6b4529" transform="rotate(-12)"/>
    <path d="M-70,-20 Q-80,-150 0,-260 Q30,-170 70,-160 Q90,-80 70,-20Z" fill="#f08a24"/>
    <path d="M-40,-20 Q-50,-110 0,-190 Q20,-120 45,-110 Q60,-60 40,-20Z" fill="#ffd34d"/>
  </g>
  <circle cx="300" cy="760" r="320" fill="url(#glow)"/>
  <g transform="translate(1050,900)">
    <path d="M-260,0 L-230,-80 L230,-80 L260,0Z" fill="#6f6862"/>
    <path d="M-300,-80 L-280,-560 Q0,-600 280,-560 L300,-80Z" fill="#8a8580"/>
    <path d="M-230,-140 L-215,-500 Q0,-530 215,-500 L230,-140Z" fill="#5d5853"/>
    <text x="0" y="-250" text-anchor="middle" font-family="DejaVu Serif, serif" font-weight="700" font-size="260" fill="#c9c2b8">?</text>
    <g stroke="#c9c2b8" stroke-width="10" stroke-linecap="round"><line x1="-170" y1="-190" x2="-170" y2="-150"/><line x1="-140" y1="-190" x2="-140" y2="-150"/><line x1="-110" y1="-190" x2="-110" y2="-150"/><line x1="-185" y1="-180" x2="-95" y2="-160"/></g>
  </g>
  ${person({ x: 640, y: 1000, s: 1.02, fur: true, beard: true, arms: "forward", mood: "worried",
    holding: `<g transform="translate(150,-330) rotate(-30)"><rect x="-10" y="-80" width="20" height="120" rx="8" fill="#6b4529"/><path d="M-30,-110 L30,-110 L20,-70 L-20,-70Z" fill="#9a948d"/></g>` })}
  <g opacity=".95">${person({ x: 1560, y: 980, s: 0.62, fur: true, beard: true, grey: true, arms: "shrug", mood: "neutral" })}${person({ x: 1760, y: 990, s: 0.58, fur: true, grey: true, arms: "shrug", mood: "worried" })}</g>
`, lg("cave", [[0, "#4a3426"], [1, "#1c130d"]]) + lg("sky", [[0, "#f4b26b"], [1, "#d9744a"]]) + lg("rock", [[0, "#5a4030"], [1, "#2a1c13"]], 1, 1) + rg("glow", [[0, "#ffb347", 0.35], [1, "#ffb347", 0]]));

// IMG-02 1996 dial-up
frames["img-02"] = svg(`
  <rect width="${W}" height="${H}" fill="#d9cbb0"/>
  <rect y="620" width="${W}" height="460" fill="#a8835c"/>${Array.from({ length: 24 }, (_, i) => `<rect x="${i * 80}" y="620" width="6" height="460" fill="#8f6c48"/>`).join("")}
  <g transform="translate(220,120)"><rect width="360" height="300" fill="#f3ead6" stroke="#b8a888" stroke-width="10"/>${Array.from({ length: 12 }, (_, i) => `<rect x="10" y="${12 + i * 24}" width="340" height="12" fill="#e2d6bc"/>`).join("")}</g>
  <g transform="translate(1640,200)"><circle r="92" fill="#fff" stroke="#6b5a44" stroke-width="12"/><line x1="0" y1="0" x2="0" y2="-60" stroke="#222" stroke-width="10" stroke-linecap="round"/><line x1="0" y1="0" x2="46" y2="16" stroke="#222" stroke-width="8" stroke-linecap="round"/></g>
  ${person({ x: 1260, y: 1060, s: 1.05, shirt: "#2f8f8a", glasses: true, arms: "forward", mood: "tired" })}
  <rect x="160" y="760" width="1600" height="60" fill="#7a5a3a"/><rect x="160" y="820" width="1600" height="260" fill="#6a4c30"/>
  <g transform="translate(520,330)">
    <path d="M-40,420 L440,420 L400,470 L0,470Z" fill="#cfc6b2"/>
    <rect x="-60" y="0" width="560" height="430" rx="26" fill="#e3dccb"/>
    <rect x="-20" y="36" width="480" height="340" rx="10" fill="#1d3f6e"/>
    <rect x="10" y="60" width="420" height="290" fill="#c0c0c0"/>
    <rect x="10" y="60" width="420" height="30" fill="#1f3b88"/><text x="22" y="82" font-family="DejaVu Sans" font-size="18" fill="#fff" font-weight="700">Web Browser</text>
    <rect x="24" y="102" width="392" height="26" fill="#fff" stroke="#808080" stroke-width="2"/><text x="32" y="121" font-family="DejaVu Sans Mono" font-size="15" fill="#333">http://www.tenders.example/energy</text>
    <text x="220" y="210" text-anchor="middle" font-family="DejaVu Sans" font-size="22" fill="#333">Connecting...</text>
    <rect x="70" y="240" width="300" height="26" fill="#fff" stroke="#808080" stroke-width="2"/><rect x="74" y="244" width="86" height="18" fill="#1f3b88"/>
    <text x="220" y="300" text-anchor="middle" font-family="DejaVu Sans" font-size="16" fill="#555">Document: 3% of 412 KB</text>
  </g>
  <g transform="translate(1180,700)"><rect width="300" height="70" rx="12" fill="#3b3b3b"/>${["#4cff6a", "#4cff6a", "#ffb02e", "#ff4c4c", "#4cff6a"].map((c, i) => `<circle cx="${50 + i * 50}" cy="35" r="10" fill="${c}"/>`).join("")}<text x="150" y="-14" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="26" fill="#3b3b3b" font-weight="700">56k</text></g>
  <g transform="translate(260,600)"><rect width="180" height="170" rx="10" fill="#e3dccb"/><rect x="20" y="30" width="140" height="16" fill="#9a9483"/><circle cx="140" cy="130" r="12" fill="#4cff6a"/></g>
  <g transform="translate(1560,700)">${[0, 1, 2].map(i => `<rect x="${i * 14}" y="${-i * 14}" width="110" height="110" rx="6" fill="${["#2a2a2a", "#3d5a80", "#8b1e3f"][i]}"/><rect x="${i * 14 + 26}" y="${-i * 14}" width="58" height="34" fill="#c0c0c0"/>`).join("")}</g>
`);

// IMG-03 2006 information overload
frames["img-03"] = svg(`
  <rect width="${W}" height="${H}" fill="#b9c6d2"/>
  <rect x="0" y="0" width="${W}" height="80" fill="#a3b2c0"/>
  <g transform="translate(1500,160)"><rect width="260" height="220" fill="#f6f6f6"/><rect x="20" y="20" width="220" height="120" fill="#7fa8c9"/><text x="130" y="190" text-anchor="middle" font-family="DejaVu Sans" font-size="26" fill="#3a4a5a">Q3 TARGETS</text></g>
  ${person({ x: 470, y: 1050, s: 1.0, shirt: "#f4f4f4", tie: "#3a5a98", glasses: true, arms: "up", mood: "worried",
    holding: `<g transform="translate(-200,-640) rotate(-14)"><rect width="120" height="160" fill="#fff" stroke="#999" stroke-width="3"/></g><g transform="translate(110,-660) rotate(12)"><rect width="120" height="160" fill="#fff" stroke="#999" stroke-width="3"/></g>` })}
  <rect x="100" y="760" width="1720" height="60" fill="#e9e9e9"/><rect x="100" y="820" width="1720" height="260" fill="#cfd5db"/>
  <g transform="translate(1180,330)">
    <rect x="-10" y="420" width="60" height="70" fill="#222"/><rect x="-90" y="480" width="220" height="20" rx="8" fill="#222"/>
    <rect x="-380" y="0" width="800" height="440" rx="16" fill="#1d1d1d"/><rect x="-360" y="20" width="760" height="400" fill="#fff"/>
    ${Array.from({ length: 14 }, (_, i) => `<rect x="${-358 + i * 54}" y="22" width="50" height="26" rx="5" fill="${i === 13 ? "#fff" : "#dfe5ea"}" stroke="#b9c3cc"/>`).join("")}
    <rect x="-200" y="76" width="440" height="40" rx="20" fill="#fff" stroke="#9aa5b1" stroke-width="3"/><circle cx="212" cy="96" r="10" fill="none" stroke="#5f7383" stroke-width="4"/><line x1="219" y1="103" x2="230" y2="114" stroke="#5f7383" stroke-width="4"/>
    ${Array.from({ length: 10 }, (_, i) => `<rect x="-320" y="${140 + i * 27}" width="${300 + (i * 53) % 220}" height="9" rx="4" fill="#1a4fd6"/><rect x="-320" y="${152 + i * 27}" width="${420 - (i * 37) % 160}" height="5" rx="2" fill="#c3c9cf"/>`).join("")}
  </g>
  ${[[140, 640], [700, 620], [1620, 640], [1760, 600], [820, 650]].map(([x, y], k) => Array.from({ length: 6 + k }, (_, i) => `<rect x="${x + (i % 2) * 6}" y="${y + 140 - i * 16}" width="150" height="20" fill="#fff" stroke="#c8c8c8" stroke-width="2"/>`).join("")).join("")}
  ${[[1600, 420, -6], [1620, 520, 5], [700, 250, 4]].map(([x, y, r], i) => `<g transform="translate(${x},${y}) rotate(${r})"><rect width="130" height="120" fill="#ffe46b"/><text x="65" y="70" text-anchor="middle" font-family="DejaVu Sans" font-size="22" fill="#3a3a3a">${["deadline?", "which one?", "call back"][i]}</text></g>`).join("")}
`);

// IMG-04 2026 night
frames["img-04"] = svg(`
  <rect width="${W}" height="${H}" fill="#0f1c2e"/>
  <g transform="translate(1320,80)"><rect width="520" height="520" fill="#14324f"/><circle cx="400" cy="110" r="46" fill="#f1ecd6"/>
    ${[[0, 300, 90], [90, 240, 70], [160, 330, 80], [240, 200, 100], [340, 280, 90], [430, 230, 90]].map(([x, h, w]) => `<rect x="${x}" y="${520 - h}" width="${w}" height="${h}" fill="#0b1726"/>` + Array.from({ length: Math.floor(h / 40) }, (_, r) => Array.from({ length: 3 }, (_, c) => ((r + c + x) % 3 ? `<rect x="${x + 12 + c * 24}" y="${520 - h + 16 + r * 36}" width="12" height="16" fill="#ffd27a"/>` : "")).join("")).join("")).join("")}
    <rect width="520" height="520" fill="none" stroke="#2b4562" stroke-width="20"/></g>
  <g transform="translate(120,90)"><rect width="1060" height="560" rx="10" fill="#8b6b4a"/><rect x="16" y="16" width="1028" height="528" fill="#b48a5a"/>
    ${Array.from({ length: 25 }, (_, i) => { const c = i % 5, r = Math.floor(i / 5); const closed = [1, 4, 7, 11, 13, 17, 22].includes(i); const x = 40 + c * 200, y = 34 + r * 102, rot = ((i * 37) % 9) - 4;
      return `<g transform="translate(${x},${y}) rotate(${rot})"><rect width="170" height="88" fill="#f8f6f0"/><rect x="12" y="12" width="110" height="10" fill="#1d3f6e"/><rect x="12" y="32" width="146" height="6" fill="#b8b3a8"/><rect x="12" y="46" width="130" height="6" fill="#b8b3a8"/><rect x="12" y="60" width="90" height="6" fill="#b8b3a8"/><circle cx="85" cy="-2" r="7" fill="#d1495b"/>${closed ? `<g transform="translate(85,50) rotate(-14)"><rect x="-66" y="-20" width="132" height="40" fill="none" stroke="#d1495b" stroke-width="5"/><text x="0" y="12" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="28" fill="#d1495b">CLOSED</text></g>` : ""}</g>`; }).join("")}
  </g>
  <g transform="translate(1580,720)"><circle r="80" fill="#f1ecd6" stroke="#2b4562" stroke-width="10"/><line x1="0" y1="0" x2="-6" y2="-54" stroke="#0f1c2e" stroke-width="9" stroke-linecap="round"/><line x1="0" y1="0" x2="-30" y2="-58" stroke="#0f1c2e" stroke-width="5" stroke-linecap="round" transform="rotate(-8)"/><text x="0" y="40" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="20" fill="#0f1c2e">23:47</text></g>
  <path d="M640,300 L380,1080 L1180,1080 L900,300Z" fill="#ffe7a3" opacity=".08"/>
  ${person({ x: 760, y: 1080, s: 1.08, shirt: "#5a6b7d", glasses: true, grey: true, arms: "down", mood: "tired", hide: true })}
  <rect x="80" y="820" width="1500" height="50" fill="#3a2a1c"/><rect x="80" y="870" width="1500" height="210" fill="#2a1e14"/>
  <g transform="translate(620,700)"><rect width="300" height="130" rx="8" fill="#c9d3dc"/><rect x="12" y="12" width="276" height="106" fill="#5ab0e6" opacity=".85"/><path d="M-30,130 L330,130 L350,150 L-50,150Z" fill="#9aa5b1"/></g>
  ${[[1060, 760], [1150, 780], [1240, 770]].map(([x, y]) => `<g transform="translate(${x},${y})"><rect width="64" height="70" rx="8" fill="#f1ecd6"/><path d="M64,18 q30,0 30,22 q0,22 -30,22" stroke="#f1ecd6" stroke-width="8" fill="none"/><rect x="8" y="8" width="48" height="10" fill="#5a3a22"/></g>`).join("")}
`);

// IMG-05 the agents arrive
const AG_NAMES = ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"];
frames["img-05"] = svg(`
  <rect width="${W}" height="${H}" fill="url(#bright)"/>
  <rect y="820" width="${W}" height="260" fill="#e8eef3"/>
  <g transform="translate(330,830)"><path d="M-170,0 L170,0 L140,-150 L-140,-150Z" fill="#3c9a5f"/><text x="0" y="-60" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="64" fill="#fff">BID</text></g>
  <g transform="translate(1000,830)"><path d="M-170,0 L170,0 L140,-150 L-140,-150Z" fill="#7d8a97"/><text x="0" y="-60" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="56" fill="#fff">NO BID</text></g>
  ${AG_NAMES.map((n, i) => { const x = i > 4 ? [80, 610, 760, 1240, 1390][i - 5] : 170 + i * 260, y = i > 4 ? 900 : 560, s = i > 4 ? 0.46 : 0.42;
    return robot({ x, y, s, color: AGENT_COLORS[i], label: n, prop: `<g transform="translate(110,-420) rotate(${(i * 17) % 30 - 15})"><rect width="140" height="100" fill="#fff" stroke="#9aa5b1" stroke-width="5"/><rect x="18" y="20" width="90" height="12" fill="#1d3f6e"/><rect x="18" y="46" width="104" height="8" fill="#c3c9cf"/></g>` }); }).join("")}
  ${person({ x: 1600, y: 1000, s: 1.0, shirt: "#1f6fb2", glasses: true, grey: true, arms: "up", mood: "happy",
    holding: `<g transform="translate(-130,-760)"><rect x="-20" y="-60" width="40" height="80" rx="10" fill="#6b4529"/><rect x="-110" y="20" width="220" height="70" rx="12" fill="#d1495b"/><text x="0" y="68" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="34" fill="#fff">APPROVED</text></g>` })}
`, lg("bright", [[0, "#7fd3f0"], [0.6, "#c8ecf7"], [1, "#ffe8c2"]]));

// IMG-06 team line-up
frames["img-06"] = svg(`
  <rect width="${W}" height="${H}" fill="#14324f"/>
  <ellipse cx="960" cy="900" rx="900" ry="120" fill="#1f4a70"/>
  ${AG_NAMES.map((n, i) => `<ellipse cx="${150 + i * 180}" cy="300" rx="120" ry="600" fill="#fff" opacity=".04"/>`).join("")}
  ${AG_NAMES.map((n, i) => robot({ x: 150 + i * 180, y: 880 - (i % 2) * 30, s: 0.6, color: AGENT_COLORS[i], label: n })).join("")}
  <text x="960" y="140" text-anchor="middle" font-family="DejaVu Sans" font-weight="700" font-size="64" fill="#eaf6ff">THE TEAM</text>
`);

// IMG-07 closing
frames["img-07"] = svg(`
  <rect width="${W}" height="${H}" fill="url(#sunset)"/>
  <circle cx="960" cy="640" r="260" fill="#ffd27a" opacity=".55"/>
  <rect y="860" width="${W}" height="220" fill="#3b2f4a"/>
  ${AG_NAMES.slice(0, 9).map((n, i) => robot({ x: 260 + i * 175 + (i > 3 ? 360 : 0), y: 900 - (i % 2) * 20, s: 0.42, color: AGENT_COLORS[i], label: n })).join("")}
  ${person({ x: 860, y: 960, s: 0.95, shirt: "#1f6fb2", glasses: true, grey: true, arms: "forward", mood: "happy" })}
  ${robot({ x: 1080, y: 960, s: 0.62, color: AGENT_COLORS[9], label: "A10" })}
`, lg("sunset", [[0, "#2b3a67"], [0.55, "#e2725b"], [1, "#ffcf8a"]]));

// ---------------------------------------------------------------- portraits
const portraits = {};
AG_NAMES.forEach((n, i) => {
  portraits[`ag-${String(i + 1).padStart(2, "0")}`] = `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
    <circle cx="512" cy="512" r="480" fill="${AGENT_COLORS[i]}" opacity=".14"/>
    ${robot({ x: 430, y: 930, s: 1.3, color: AGENT_COLORS[i], label: n, prop: PROPS[i] })}
  </svg>`;
});

fs.writeFileSync(path.join(OUT, "frames.json"), JSON.stringify({ frames, portraits }));
console.log("frames", Object.keys(frames).length, "portraits", Object.keys(portraits).length);
