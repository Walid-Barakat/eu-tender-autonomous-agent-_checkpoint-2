"""Inline the optimiser and scenario data into one self-contained HTML page."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / "console_template.html").read_text(encoding="utf-8")
html = html.replace("__ENGINE__", (ROOT / "console_engine.js").read_text(encoding="utf-8"))
html = html.replace("__DATA__", (ROOT / "portfolio_data.json").read_text(encoding="utf-8"))
out = ROOT / "tender_portfolio_console.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")

# Standalone copy for the presentation (iframe inside the deck): a full HTML document.
deck_copy = ROOT.parent / "presentation" / "console.html"
deck_copy.write_text(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n</head>\n<body>\n'
    + html + "\n</body>\n</html>\n", encoding="utf-8")
print(f"wrote {deck_copy} ({deck_copy.stat().st_size / 1024:.0f} KB)")
