"""Regenerate the assembly files and run the interference check on the home pose and every pose.

python design/v1/check_all.py [pose ...]
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
subprocess.run([sys.executable, str(HERE / "make_assembly.py")], check=True, capture_output=True)
poses = sys.argv[1:] or ["home"] + sorted(p.name for p in (HERE / "poses").iterdir() if p.is_dir())
out = {}
for p in poses:
    variant = "v1" if p == "home" else f"v1/poses/{p}"
    r = subprocess.run([sys.executable, "-m", "mechy.design_tools", "check", variant, "--project", str(ROOT)],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    out[p] = {k: d[k] for k in ("interferences", "clearance_issues", "unverified_contacts", "ok")}
    print(f"== {p}: ok={d['ok']}")
    for k in ("interferences", "clearance_issues", "unverified_contacts"):
        for i in d[k]:
            print(f"   {k[:-1]}: {i}")
(HERE / "check_results.json").write_text(json.dumps(out, indent=1))
