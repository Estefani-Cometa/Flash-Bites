"""Validate local file targets used by inline links in the root README."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))")


def main() -> int:
    if not README.is_file():
        print("README.md was not found at the repository root.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for line_number, line in enumerate(README.read_text(encoding="utf-8").splitlines(), start=1):
        for match in LINK_PATTERN.finditer(line):
            destination = match.group(1) or match.group(2) or ""
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue

            target = (README.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                errors.append(f"README.md:{line_number}: missing local target '{parsed.path}'")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("All local file links in README.md resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
