import os
import math
from typing import List, Tuple, Dict, Any, Optional
from core.color_theory import color_theory_score


def color_similarity(vec1: List[float], vec2: List[float], norm1: Optional[float] = None, norm2: Optional[float] = None) -> float:
    """
    Direct numerical calculation of cosine similarity between two 3D RGB vectors.
    Replaces heavy sklearn cosine_similarity check_array and DataFrame overhead
    while guaranteeing mathematical equivalence.
    """
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]
    if norm1 is None:
        norm1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2 + vec1[2] ** 2)
    if norm2 is None:
        norm2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2 + vec2[2] ** 2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


def formality_score(f1: float, f2: float) -> float:
    """Penalize mismatched formality levels."""
    diff = abs(f1 - f2)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.7
    if diff == 2:
        return 0.4
    return 0.1


def _watch_representative_vec(item: Dict[str, Any]) -> List[float]:
    """
    For watches, return strap_color_vec as the primary compatibility vector.
    Falls back to the main color_vec if strap not available.
    """
    strap = item.get("strap_color_vec")
    if strap:
        return strap
    return item["color_vec"]


def _watch_hue(item: Dict[str, Any]) -> float:
    """Return strap hue for watches if available, else main hue."""
    if item.get("type") == "watch":
        h = item.get("strap_hue")
        if h is not None and str(h).strip() != "" and not (isinstance(h, float) and math.isnan(h)):
            return float(h)
    return float(item["hue"])


# In-memory pairwise score cache for the lifetime of the process/instance
_SCORE_CACHE: Dict[Tuple[str, str], float] = {}


def clear_score_cache():
    """Clear in-memory score cache."""
    global _SCORE_CACHE
    _SCORE_CACHE.clear()


def compatibility_score(item1: Dict[str, Any], item2: Dict[str, Any]) -> float:
    """
    Score compatibility between two wardrobe items.
    Preserves exact formula:
    0.35 * Color_Sim + 0.25 * Color_Theory + 0.25 * Vibe_Sim + 0.15 * Formality_Score
    """
    # Use canonical pair key for undirected caching if item_names/ids are present
    name1 = item1.get("item_name") or str(item1.get("id", ""))
    name2 = item2.get("item_name") or str(item2.get("id", ""))
    
    if name1 and name2:
        cache_key = (name1, name2) if name1 <= name2 else (name2, name1)
        if cache_key in _SCORE_CACHE:
            return _SCORE_CACHE[cache_key]
    else:
        cache_key = None

    vec1 = item1.get("_rep_vec") or (_watch_representative_vec(item1) if item1.get("type") == "watch" else item1["color_vec"])
    vec2 = item2.get("_rep_vec") or (_watch_representative_vec(item2) if item2.get("type") == "watch" else item2["color_vec"])
    norm1 = item1.get("_rep_norm")
    norm2 = item2.get("_rep_norm")

    hue1 = item1.get("_rep_hue") if "_rep_hue" in item1 else _watch_hue(item1)
    hue2 = item2.get("_rep_hue") if "_rep_hue" in item2 else _watch_hue(item2)

    color_sim = color_similarity(vec1, vec2, norm1, norm2)
    color_theory = color_theory_score(hue1, hue2)

    # Vibe similarity (optimized Jaccard on precomputed sets)
    vibe1 = item1.get("_vibe_set")
    vibe2 = item2.get("_vibe_set")
    if vibe1 is None:
        v1 = item1.get("vibe") or []
        vibe1 = frozenset(v1) if isinstance(v1, (list, set)) else frozenset()
    if vibe2 is None:
        v2 = item2.get("vibe") or []
        vibe2 = frozenset(v2) if isinstance(v2, (list, set)) else frozenset()

    if not vibe1 or not vibe2:
        vibe_sim = 0.0
    else:
        inter = len(vibe1 & vibe2)
        union = len(vibe1 | vibe2)
        vibe_sim = inter / union if union > 0 else 0.0

    f1 = item1.get("_formality", item1.get("formality", 0))
    f2 = item2.get("_formality", item2.get("formality", 0))
    form_score = formality_score(f1, f2)

    score = round(
        0.35 * color_sim +
        0.25 * color_theory +
        0.25 * vibe_sim +
        0.15 * form_score,
        3
    )

    if cache_key:
        _SCORE_CACHE[cache_key] = score

    return score