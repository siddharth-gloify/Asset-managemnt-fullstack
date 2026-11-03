"""Enforce the preline-ui rules on templates. Exit 0 when clean, 1 otherwise."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"
MACROS = TEMPLATES / "macros"
APP_JS = ROOT / "app" / "static" / "js"

RAW_TAGS = re.compile(r"<(button|input|select|textarea|table)\b", re.I)
RULES = [
    (re.compile(r"<style\b", re.I), "inline <style> block"),
    (re.compile(r"\sstyle\s*=", re.I), 'inline style=""'),
    (re.compile(r"(?:src|href)=[\"']https?://", re.I), "external CDN/URL asset"),
    (re.compile(r"jquery|bootstrap", re.I), "jQuery/Bootstrap reference"),
    (re.compile(r"class=[\"'][^\"']*\b(btn-primary|btn-secondary|col-md-\d+|navbar-expand)\b", re.I), "Bootstrap class"),
    (re.compile(r"<i\s+class=[\"'](?:fa|bi|material-icons)", re.I), "icon font"),
]


def main() -> int:
    problems: list[str] = []
    for path in sorted(TEMPLATES.rglob("*.html")):
        rel = path.relative_to(ROOT)
        in_macros = MACROS in path.parents
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            if not in_macros and RAW_TAGS.search(line):
                problems.append(f"{rel}:{lineno}: raw <{RAW_TAGS.search(line).group(1)}> outside macros/")
            for pattern, label in RULES:
                if pattern.search(line):
                    problems.append(f"{rel}:{lineno}: {label}")
    for path in sorted(APP_JS.glob("*.js")):
        if path.name in ("preline.js", "htmx.min.js"):
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"\.style\.display|classList\.(add|remove|toggle)\(['\"]hidden", text):
            problems.append(f"{path.relative_to(ROOT)}: toggles visibility by hand (use Preline plugins)")
    css = ROOT / "app" / "static" / "css" / "app.css"
    if not css.exists() or css.stat().st_size < 10_000:
        problems.append("app/static/css/app.css missing or empty: run the CSS build")
    for needed in ("macros/ui.html", "macros/icons.html"):
        if not (TEMPLATES / needed).exists():
            problems.append(f"missing app/templates/{needed}")

    if problems:
        print(f"check_ui: {len(problems)} problem(s)")
        for p in problems:
            print("  -", p)
        return 1
    print("check_ui: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
