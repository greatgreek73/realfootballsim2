from __future__ import annotations

"""
Custom headers for WhiteNoise static files.

We set a long cache for font files under /static/fonts/* to avoid re-downloads
and visual flicker. ETag is added by WhiteNoise automatically.
"""

from typing import Dict


def add_headers(headers: Dict[str, str], path: str, url: str) -> None:
    u = url.replace("\\", "/")
    p = path.replace("\\", "/")

    if u.startswith("/static/fonts/") or "/static/fonts/" in u or "/static/fonts/" in p:
        headers["Cache-Control"] = "public, max-age=31536000, immutable"

