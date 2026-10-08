"""Build the site and zip the files that go on the web server (for uploading to HostGator's public_html)."""
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
SKIP = {".git", "_build", ".gitignore", "README.md", "notes.md", "_redirects"}

subprocess.run([sys.executable, str(HERE / "build.py")], check=True)
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "independentclaimsconsultants-site.zip"
count = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in SKIP or path.is_dir() or path == out or path.suffix == ".zip":
            continue
        z.write(path, rel.as_posix())
        count += 1
print(f"Wrote {out} ({count} files, {out.stat().st_size / 1e6:.1f} MB)")
