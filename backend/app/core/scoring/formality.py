def formality_score(f1: float, f2: float) -> float:
    """Penalize mismatched formality levels according to project specification."""
    diff = abs(f1 - f2)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.7
    if diff == 2:
        return 0.4
    return 0.1
