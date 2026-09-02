from typing import Set, Sequence, Any


def vibe_similarity(v1: Any, v2: Any) -> float:
    """Jaccard similarity between two sets of vibes."""
    if not v1 or not v2:
        return 0.0

    s1 = v1 if isinstance(v1, (set, frozenset)) else set(v1)
    s2 = v2 if isinstance(v2, (set, frozenset)) else set(v2)

    if not s1 or not s2:
        return 0.0

    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union if union > 0 else 0.0
