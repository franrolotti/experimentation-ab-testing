from __future__ import annotations
import numpy as np
import pandas as pd


def assign_variants(
    users: pd.DataFrame,
    method: str = "bernoulli",
    p: float = 0.5,
    blocks: list[str] | None = None,
    seed: int | None = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = users.copy()
    if method == "bernoulli" or not blocks:
        df["variant"] = (rng.random(size=len(df)) < p).astype(int)
        return df
    # stratified by blocks
    df["variant"] = 0
    for _, g in df.groupby(blocks):
        idx = g.index.to_numpy()
        k = int(round(len(idx) * p))
        treat_idx = rng.choice(idx, size=k, replace=False)
        df.loc[treat_idx, "variant"] = 1
    return df

