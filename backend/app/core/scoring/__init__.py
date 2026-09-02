import math
from typing import Dict, Any, List, Optional, Tuple

from app.core.scoring.color import color_similarity, color_theory_score
from app.core.scoring.vibe import vibe_similarity
from app.core.scoring.formality import formality_score


def watch_representative_vec(item: Dict[str, Any]) -> List[float]:
    """For watches, return strap_color_vec as prominent visual vector, falling back to color_vec."""
    strap = item.get("strap_color_vec")
    if strap:
        return strap
    return item.get("color_vec", [0.0, 0.0, 0.0])


def watch_hue(item: Dict[str, Any]) -> float:
    """Return strap hue for watches if available, else main hue."""
    if item.get("type") == "watch":
        h = item.get("strap_hue")
        if h is not None and str(h).strip() != "" and not (isinstance(h, float) and math.isnan(h)):
            return float(h)
    return float(item.get("hue", 0.0))


_IN_MEMORY_SCORE_CACHE: Dict[Tuple[str, str], float] = {}


def clear_score_cache():
    global _IN_MEMORY_SCORE_CACHE
    _IN_MEMORY_SCORE_CACHE.clear()


def compatibility_score(item1: Dict[str, Any], item2: Dict[str, Any]) -> float:
    """
    Score compatibility between two wardrobe items.
    Preserves exact formula:
    0.35 * Color_Sim + 0.25 * Color_Theory + 0.25 * Vibe_Sim + 0.15 * Formality_Score
    """
    name1 = str(item1.get("id") or item1.get("item_name") or "")
    name2 = str(item2.get("id") or item2.get("item_name") or "")

    cache_key = None
    if name1 and name2:
        cache_key = (name1, name2) if name1 <= name2 else (name2, name1)
        if cache_key in _IN_MEMORY_SCORE_CACHE:
            return _IN_MEMORY_SCORE_CACHE[cache_key]

    vec1 = item1.get("_rep_vec") or (watch_representative_vec(item1) if item1.get("type") == "watch" else item1.get("color_vec", [0, 0, 0]))
    vec2 = item2.get("_rep_vec") or (watch_representative_vec(item2) if item2.get("type") == "watch" else item2.get("color_vec", [0, 0, 0]))
    norm1 = item1.get("_rep_norm")
    norm2 = item2.get("_rep_norm")

    hue1 = item1.get("_rep_hue") if "_rep_hue" in item1 else watch_hue(item1)
    hue2 = item2.get("_rep_hue") if "_rep_hue" in item2 else watch_hue(item2)

    col_sim = color_similarity(vec1, vec2, norm1, norm2)
    col_theory = color_theory_score(hue1, hue2)

    vibe1 = item1.get("_vibe_set", item1.get("vibe", []))
    vibe2 = item2.get("_vibe_set", item2.get("vibe", []))
    v_sim = vibe_similarity(vibe1, vibe2)

    f1 = item1.get("_formality", item1.get("formality", 0))
    f2 = item2.get("_formality", item2.get("formality", 0))
    f_score = formality_score(float(f1), float(f2))

    score = round(
        0.35 * col_sim +
        0.25 * col_theory +
        0.25 * v_sim +
        0.15 * f_score,
        3
    )

    if cache_key:
        _IN_MEMORY_SCORE_CACHE[cache_key] = score

    return score
