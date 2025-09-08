from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd

@dataclass
class GenParams:
    n_users: int
    segment_cols: List[str]
    seed: int | None = 42

_DEVICES = ["mobile", "desktop"]
_GEOS = ["DE", "AT", "CH", "ES", "IT"]
_SOURCES = ["direct", "seo", "paid", "referral"]


def _sample_segments(rng: np.random.Generator, n: int) -> pd.DataFrame:
    device = rng.choice(_DEVICES, size=n, p=[0.65, 0.35])
    geo = rng.choice(_GEOS, size=n, p=[0.5, 0.15, 0.1, 0.15, 0.1])
    source = rng.choice(_SOURCES, size=n, p=[0.25, 0.4, 0.25, 0.1])
    return pd.DataFrame({"device": device, "geo": geo, "source": source})


def generate_users(params: GenParams) -> pd.DataFrame:
    rng = np.random.default_rng(params.seed)
    user_id = np.arange(params.n_users)
    seg = _sample_segments(rng, params.n_users)
    # Pre-period activity correlated with outcome (for CUPED)
    pre = rng.poisson(lam=2, size=params.n_users).astype(float)
    signup_ts = pd.Timestamp("2025-08-01") + pd.to_timedelta(rng.integers(0, 7, size=params.n_users), unit="D")
    users = pd.DataFrame({"user_id": user_id, "signup_ts": signup_ts, "preperiod_activity": pre})
    users = pd.concat([users, seg], axis=1)
    return users


def simulate_funnel(
    users: pd.DataFrame,
    base_conv: float = 0.28,
    lift: float = 0.02,
    seed: int | None = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # Base step completion probs
    p1, p2, p3, p4 = 0.9, 0.8, 0.75, 0.7
    # treatment effect applied at final completion only
    is_treat = users["variant"].eq(1).astype(int)
    conv = base_conv + lift * is_treat
    conv = np.clip(conv, 0.0, 1.0)

    rows = []
    for _, r in users.iterrows():
        uid = int(r.user_id)
        ts = pd.Timestamp(r.signup_ts)
        # Step-by-step progress
        reached = True
        for step, p in enumerate([p1, p2, p3, p4], start=1):
            reached = reached and (rng.random() < p)
            if reached:
                rows.append({"user_id": uid, "ts": ts + pd.to_timedelta(step, unit="m"), "event": "step", "step": step})
        # Final completion event
        if rng.random() < conv.iloc[_]:
            rows.append({"user_id": uid, "ts": ts + pd.to_timedelta(10, unit="m"), "event": "completed", "step": 5})
    return pd.DataFrame(rows)


def outcomes_from_events(events: pd.DataFrame) -> pd.DataFrame:
    grp = events.sort_values(["user_id", "ts"]).groupby("user_id")
    completed = grp["event"].apply(lambda s: int((s == "completed").any()))
    first = grp["ts"].min()
    last = grp["ts"].max()
    ttc = (last - first).dt.total_seconds().fillna(0)
    out = pd.DataFrame({"user_id": completed.index, "completed_profile": completed.values, "time_to_complete_s": ttc.values})
    return out
