from __future__ import annotations
import os
from pathlib import Path
import typer

from .data.generator import GenParams, generate_users, simulate_funnel, outcomes_from_events
from .randomization.assignment import assign_variants
from .stats.power import sample_size_prop
from .analysis.pipeline import run_analysis
from .analysis.reporting import export_tables, export_plots

app = typer.Typer(add_completion=False, help="A/B testing CLI")

@app.command()
def power(
    baseline: float = typer.Option(..., help="Baseline conversion rate, e.g. 0.28"),
    mde: float = typer.Option(..., help="Minimum Detectable Effect (absolute), e.g. 0.02"),
    alpha: float = 0.05,
    power: float = 0.8,
):
    """Compute sample size for two-sample proportions."""
    n = sample_size_prop(baseline=baseline, mde=mde, alpha=alpha, power=power)
    typer.echo(f"Required sample per group: {n}")

@app.command()
def simulate(
    n_users: int = 50000,
    exp_id: str = "signup_v1",
    base_conv: float = 0.28,
    lift: float = 0.02,
    seed: int = 42,
    segments: str = "device,geo",
    out: str = "data/processed/signup_v1/",
):
    """Generate synthetic users, assignments, events, and outcomes."""
    Path(out).mkdir(parents=True, exist_ok=True)
    seg_cols = [s.strip() for s in segments.split(",") if s.strip()]

    users = generate_users(GenParams(n_users=n_users, seed=seed, segment_cols=seg_cols))
    assigned = assign_variants(users, method="stratified", blocks=seg_cols, seed=seed)

    # Simulate funnel with a treatment lift on completion
    events = simulate_funnel(assigned, base_conv=base_conv, lift=lift, seed=seed)
    outcomes = outcomes_from_events(events)

    users.to_csv(os.path.join(out, "users.csv"), index=False)
    assigned.to_csv(os.path.join(out, "assignments.csv"), index=False)
    events.to_csv(os.path.join(out, "events.csv"), index=False)
    outcomes.to_csv(os.path.join(out, "outcomes.csv"), index=False)

    typer.echo(f"Wrote synthetic data to {out}")

@app.command()
def analyze(
    input: str = typer.Option(..., help="Input dir with CSVs"),
    metric: str = typer.Option("completed_profile", help="Primary metric column in outcomes.csv"),
    cuped: bool = typer.Option(True, help="Apply CUPED adjustment"),
    segments: str = typer.Option("device,geo", help="Segment columns present in users.csv"),
    out: str = typer.Option("reports/signup_v1/", help="Output directory for results"),
):
    """Run end-to-end analysis (SRM, invariants, effect, CUPED, segments)."""
    Path(out).mkdir(parents=True, exist_ok=True)
    seg_cols = [s.strip() for s in segments.split(",") if s.strip()]
    results = run_analysis(Path(input), metric=metric, use_cuped=cuped, segments=seg_cols)
    export_tables(results, out)
    typer.echo(f"Analysis complete. Tables written to {out}")

@app.command()
def report(
    results: str = typer.Option(..., help="Directory with exported tables (results.csv, segments.csv)"),
):
    """Create plots for quick consumption."""
    export_plots({"results_dir": results}, results)
    typer.echo(f"Plots exported to {results}")

if __name__ == "__main__":
    app()
