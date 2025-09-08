from __future__ import annotations
import numpy as np


def cuped_transform(y: np.ndarray, x_cov: np.ndarray):
    x_centered = x_cov - x_cov.mean()
    theta = np.cov(y, x_cov, ddof=1)[0, 1] / np.var(x_cov, ddof=1)
    y_adj = y - theta * x_centered
    return y_adj, float(theta)
