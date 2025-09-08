from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def export_tables(results: dict, out_dir: str):
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([results["summary"]]).to_csv(p / "results.csv", index=False)
    if results.get("segments") is not None:
        results["segments"].to_csv(p / "segments.csv", index=False)
    # balance as simple key-value CSV
    bal = pd.DataFrame([results["balance"]])
    bal.to_csv(p / "balance.csv", index=False)


def export_plots(results: dict, out_dir: str):
    p = Path(out_dir)
    res = pd.read_csv(p / "results.csv")
    # Effect plot: lift with CI
    lift = float(res.loc[0, "lift"]) if "lift" in res.columns else 0.0
    ci_low, ci_high = eval(res.loc[0, "ci"]) if "ci" in res.columns else (0.0, 0.0)

    plt.figure()
    plt.errorbar([0], [lift], yerr=[[lift - ci_low], [ci_high - lift]], fmt="o")
    plt.xticks([0], ["Treatment vs Control"])
    plt.ylabel("Lift in conversion")
    plt.title("A/B Effect with 95% CI")
    plt.tight_layout()
    plt.savefig(p / "effect_ci.png")
    plt.close()
