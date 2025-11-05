from pathlib import Path, PurePath

def path_nonexistent_parent_exists(in_val: str) -> PurePath:
    res = Path(in_val)
    if res.exists():
        raise ValueError(f"The path {in_val} already exists")
    if not res.parent.is_dir():
        raise ValueError(f"The parent of the path {in_val} ({res.parent}) is not a directory")
    return res

def path_exists(in_val: str) -> PurePath:
    res = Path(in_val)
    if not res.exists():
        raise ValueError(f"The path {in_val} does not exist")

    return res