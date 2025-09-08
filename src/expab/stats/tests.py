from __future__ import annotations
import math
from typing import Literal


def z_test_proportions(
    x_a: int,
    n_a: int,
    x_b: int,
    n_b: int,
    alternative: Literal["two-sided", "larger", "smaller"] = "two-sided",
):
    """Two-sample z-test for proportions (pooled SE). Returns z, p_value, lift, se, ci."""
    p_a = x_a / n_a
    p_b = x_b / n_b
    lift = p_b - p_a
    p_pool = (x_a + x_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = 0.0 if se == 0 else lift / se
    from math import erf, sqrt

    def phi(z):
        return 0.5 * (1 + erf(z / sqrt(2)))

    if alternative == "two-sided":
        p = 2 * (1 - phi(abs(z)))
    elif alternative == "larger":
        p = 1 - phi(z)
    else:
        p = phi(z)
    # 95% Wald CI
    ci_low = lift - 1.96 * se
    ci_high = lift + 1.96 * se
    return {"z": z, "p_value": p, "lift": lift, "se": se, "ci": (ci_low, ci_high)}
