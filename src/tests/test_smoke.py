from pathlib import Path
from expab.data.generator import GenParams, generate_users
from expab.randomization.assignment import assign_variants
from expab.stats.tests import z_test_proportions


def test_pipeline_minimal():
    users = generate_users(GenParams(n_users=1000, segment_cols=["device", "geo"], seed=1))
    asg = assign_variants(users, method="stratified", blocks=["device", "geo"], seed=1)
    assert set([0, 1]).issubset(set(asg.variant.unique()))


res = z_test_proportions(280, 1000, 300, 1000)
assert "p_value" in res and 0 <= res["p_value"] <= 1