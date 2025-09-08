# A/B Testing for Signup Funnel


**Goal**: Estimate the causal effect of a signup-flow variant on profile completion.


**Design**: Randomized A/B (50/50), stratified by device+geo. Primary metric: profile completion within 7 days. CUPED applied using pre-period activity. SRM + invariant checks included.


**Quick start**
```bash
make setup
make demo # simulate → analyze → report
```
Outputs in `reports/signup_v1/`.


