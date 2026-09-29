from __future__ import annotations

import re
from pathlib import Path

_PATTERNS = [
    re.compile(r"Lowest Binding Energy\s*=\s*([-+]?\d+(?:\.\d+)?)", re.I),
    re.compile(r"Estimated Free Energy of Binding\s*=\s*([-+]?\d+(?:\.\d+)?)", re.I),
]


def parse_binding_energy(path: str | Path) -> float:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    values: list[float] = []
    for pattern in _PATTERNS:
        values.extend(float(match.group(1)) for match in pattern.finditer(text))
        if values:
            break
    if not values:
        raise ValueError(f"no recognizable binding-energy line in {path}")
    return min(values)
