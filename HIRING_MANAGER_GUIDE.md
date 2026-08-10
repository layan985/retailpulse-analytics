# RetailPulse — five-minute review path

This repository is meant to answer one hiring question: can I take ordinary, messy business data from ingestion to a defensible decision rather than stopping at a notebook?

## Minute 1 — business result

Read `RESULTS.md`.

The deterministic synthetic run contains 30,000 cleaned orders and 70,439 order lines. It reports revenue, margin, returns, repeat purchase, channel economics, discount effects, and a future-repeat-purchase model. The synthetic-data label is deliberate: these are pipeline validation results, not claims about a real company.

## Minute 2 — SQL

Open `sql/analysis.sql`.

Look for the grain of each query, the join paths, cohort construction, conditional aggregation, and window functions. The point is not query count; it is whether the denominator and row grain remain controlled.

## Minute 3 — data quality + dimensional model

Open `src/retailpulse/pipeline.py` and `tests/test_pipeline.py`.

The generator deliberately injects duplicate orders, inconsistent country labels, and blank acquisition channels. The pipeline repairs them, builds fact/dimension tables, turns on foreign-key checks, and exposes a financial view used by downstream analyses.

## Minute 4 — predictive modeling

Open `src/retailpulse/ml.py` and `MODEL_CARD.md`.

The prediction timestamp is 2025-02-28. Features use history available by that date; the target is completed purchase in the following 90 days. The model comparison includes a prevalence baseline. In the current deterministic run, logistic regression reaches ROC-AUC 0.664 vs 0.500 for the baseline and 0.653 for random forest.

## Minute 5 — communication

Read `docs/BUSINESS_MEMO.md`.

The recommendations keep revenue, margin, returns, and customer behavior separate. Prediction scores are not presented as causal treatment effects.

## What this project does not prove

It does not prove production impact, live-company deployment, or real-customer model performance. It proves the workflow can be reproduced and inspected end to end.
