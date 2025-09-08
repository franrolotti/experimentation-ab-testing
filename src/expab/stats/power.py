from __future__ import annotations
import math
from scipy.stats import norm


def sample_size_prop(baseline: float, mde: float, alpha: float, power: float) -> int:
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    p1, p2 = baseline, baseline + mde
    p_bar = (p1 + p2) / 2
    n = 2 * (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return int(math.ceil(n / 2))  # per group
