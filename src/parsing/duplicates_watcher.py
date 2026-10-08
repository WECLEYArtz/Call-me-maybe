from ..errors import JsonDuplication


def duplicates_watcher(ordered_pairs: list[tuple[str, str]]) -> dict[str, str]:
    d: dict[str, str] = {}
    for k, v in ordered_pairs:
        if k in d:
            raise JsonDuplication(f"\nkey: '{k}',\nvalue: '{v}'")
        d[k] = v
    return d
