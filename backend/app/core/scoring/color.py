import math
from typing import List, Optional


def hue_distance(h1: float, h2: float) -> float:
    """Calculate circular shortest angular distance between two hues on 360-deg wheel."""
    diff = abs(h1 - h2) % 360
    return min(diff, 360 - diff)


def complementary(h1: float, h2: float) -> bool:
    return abs(hue_distance(h1, h2) - 180) <= 25


def analogous(h1: float, h2: float) -> bool:
    return hue_distance(h1, h2) <= 30


def triadic(h1: float, h2: float) -> bool:
    return abs(hue_distance(h1, h2) - 120) <= 25


def color_theory_score(h1: float, h2: float) -> float:
    if complementary(h1, h2):
        return 1.0
    if analogous(h1, h2):
        return 0.8
    if triadic(h1, h2):
        return 0.7
    return 0.3


def color_similarity(vec1: List[float], vec2: List[float], norm1: Optional[float] = None, norm2: Optional[float] = None) -> float:
    """Direct numerical cosine similarity between two 3D RGB vectors."""
    dot = vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]
    if norm1 is None:
        norm1 = math.sqrt(vec1[0] ** 2 + vec1[1] ** 2 + vec1[2] ** 2)
    if norm2 is None:
        norm2 = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2 + vec2[2] ** 2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)
