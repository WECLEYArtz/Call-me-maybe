from ..errors import JsonDuplication


def duplicates_watcher(ordered_pairs: list[tuple[str, str]]) -> dict[str, str]:
    """Build a dictionary and reject duplicate keys.

    Args:
        ordered_pairs: JSON key-value pairs in their source order.

    Returns:
        A dictionary containing the unique pairs.

    Raises:
        JsonDuplication: If a key occurs more than once.
    """
    d: dict[str, str] = {}
    for k, v in ordered_pairs:
        if k in d:
            raise JsonDuplication(f"\nkey: '{k}',\nvalue: '{v}'")
        d[k] = v
    return d
