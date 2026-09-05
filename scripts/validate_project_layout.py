"""Verify preserved source bytes, local gallery links and readable Python scripts."""

import ast
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/original"
REPORTS = ROOT / "docs/validation"


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                url = urlsplit(value)
                if not url.scheme and not url.netloc and url.path:
                    self.links.append(unquote(url.path))


errors = []
references = json.loads(
    (REPORTS / "reference-preservation.json").read_text(encoding="utf-8-sig")
)
for row in references:
    path = SOURCE / row["path"]
    if not path.is_file():
        errors.append(f"Missing original: {row['path']}")
    elif hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        errors.append(f"Changed original: {row['path']}")

link_count = 0
for gallery in (SOURCE / "index.html", ROOT / "renders/index.html"):
    parser = LocalLinks()
    parser.feed(gallery.read_text(encoding="utf-8"))
    for link in parser.links:
        link_count += 1
        if not (gallery.parent / link).exists():
            errors.append(f"Broken link in {gallery.name}: {link}")

scripts = sorted((ROOT / "scripts").glob("*.py"))
for script in scripts:
    ast.parse(script.read_text(encoding="utf-8"), filename=str(script))

report = {
    "preserved_original_files": len(references),
    "gallery_links_checked": link_count,
    "python_scripts_parsed": len(scripts),
    "errors": errors,
    "passed": not errors,
}
(REPORTS / "project-layout-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report, indent=2))
if errors:
    raise SystemExit(1)
