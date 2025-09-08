from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

from ..stats.tests import z_test_proportions
from ..stats.cuped import cuped_transform


def run_analysis(input_path: Path, metric: str, use_cuped: bool, segments: list[str]):
    users = pd.read_csv(input_path / "users.csv")
    asg = pd.read_csv(input_path / "assignments.csv")
    out = pd.read_csv(input_path / "outcomes.csv")

    df = users.merge(asg[["user_id", "variant"]], on="user_id").merge(out[["user_id", metric]], on="user_id")

    # SRM check
    counts = df["variant"].value_counts()
    n_a, n_b = int(counts.get(0, 0)), int(counts.get(1, 0))
    expected = (n_a + n_b) / 2
    srm_chi2 = ((n_a - expected) ** 2 / expected) + ((n_b - expected) ** 2 / expected)

    # Invariants (balance in segments) → standardized diff
    balance = {}
    for col in segments:
        prop_t = df[df.variant == 1][col].value_counts(normalize=True)
        prop_c = df[df.variant == 0][col].value_counts(normalize=True)
        balance[col] = (prop_t - prop_c).abs().sum()

    # Primary effect
    x_a = int(df.loc[df.variant == 0, metric].sum())
    n_a = int((df.variant == 0).sum())
    x_b = int(df.loc[df.variant == 1, metric].sum())
    n_b = int((df.variant == 1).sum())
    res = z_test_proportions(x_a, n_a, x_b, n_b)

    # CUPED adjustment
    cuped = None
    if use_cuped and "preperiod_activity" in df.columns:
        y = df[metric].to_numpy(float)
        x = df["preperiod_activity"].to_numpy(float)
        y_adj, theta = cuped_transform(y, x)
        df_adj = df.copy()
        df_adj[metric + "_adj"] = y_adj
        x_a2 = float(df_adj.loc[df_adj.variant == 0, metric + "_adj"].mean())
        x_b2 = float(df_adj.loc[df_adj.variant == 1, metric + "_adj"].mean())
        lift_adj = x_b2 - x_a2
        cuped = {"theta": theta, "lift_adj": lift_adj}

    # Segment effects
    seg_rows = []
    for col in segments:
        for val, g in df.groupby(col):
            x_a = int(g.loc[g.variant == 0, metric].sum())
            n_a = int((g.variant == 0).sum())
            x_b = int(g.loc[g.variant == 1, metric].sum())
            n_b = int((g.variant == 1).sum())
            if n_a > 0 and n_b > 0:
                r = z_test_proportions(x_a, n_a, x_b, n_b)
                seg_rows.append({"segment": col, "value": val, **r})
    seg_df = pd.DataFrame(seg_rows)

    return {
        "summary": {
            "n_control": n_a,
            "n_treatment": n_b,
            "srm_chi2": float(srm_chi2),
            **res,
        },
        "balance": balance,
        "segments": seg_df,
    }
