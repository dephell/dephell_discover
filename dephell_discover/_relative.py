from pathlib import Path
from typing import Optional


def get_relative_path(path: Path, *, root: Optional[Path] = None, sep: str = '.') -> str:
    parts = path.parts[len(root.parts):]
    return sep.join(parts)
