from pathlib import Path
from typing import Any
from yaml import safe_load


def get_conf(filepath: Path) -> dict[str, Any]:
    if not filepath.exists() or not filepath.read_text():
        return {}

    return safe_load(filepath.read_text())
