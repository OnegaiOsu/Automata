"""Build the static frontend bundle for Cloudflare Pages.

This copies the HTML/CSS/JS assets into `dist/` and injects the public
backend URL into the HTML shell.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
TOKEN = "__AUTOMATA_API_BASE__"


def copy_tree(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def build() -> None:
    api_base = os.environ.get("AUTOMATA_API_BASE", "").strip().rstrip("/")

    DIST.mkdir(exist_ok=True)

    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    html = html.replace(TOKEN, api_base)
    (DIST / "index.html").write_text(html, encoding="utf-8")

    static_src = ROOT / "static"
    static_dest = DIST / "static"
    if static_dest.exists():
        shutil.rmtree(static_dest)
    copy_tree(static_src, static_dest)


if __name__ == "__main__":
    build()