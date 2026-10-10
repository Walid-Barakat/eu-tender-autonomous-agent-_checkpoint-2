"""Build final_presentation.js from final_presentation.src.js and version_b_scripts.json,
and regenerate VERSION_B_RECORDING_SCRIPTS.md. Run after editing either source."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = (HERE / "final_presentation.src.js").read_text(encoding="utf-8")
scripts = json.loads((HERE / "version_b_scripts.json").read_text(encoding="utf-8"))
marker = "/*__SCRIPTS_B__*/null"
if src.count(marker) != 1:
    sys.exit("placeholder for the Version B scripts not found exactly once")
out = src.replace(marker, json.dumps(scripts, ensure_ascii=False, separators=(",", ":")))
if "</script" in out.lower():
    sys.exit("built script contains a closing script tag")
(HERE / "final_presentation.js").write_text(out, encoding="utf-8")
subprocess.run([sys.executable, str(HERE / "build_scripts_doc.py")], check=True)
print(f"final_presentation.js written ({len(out) / 1024:.0f} KB)")
