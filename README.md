# RetailPulse

A commercial analytics team rarely gets a clean modeling table. It gets customer records, order lines, returns, product costs, duplicated rows, inconsistent labels, and a request such as: **what is driving revenue, which customers come back, where are margins leaking, and can we identify likely repeat purchasers without leaking future information?**

> **Hiring manager:** start with [`HIRING_MANAGER_GUIDE.md`](HIRING_MANAGER_GUIDE.md) for a five-minute review path.

This repository is a deliberately company-shaped analytics case study. The raw data are **synthetic** so the full warehouse can be regenerated safely, but the work is designed to resemble an analyst handoff: raw tables → cleaning and QA → dimensional model → SQL → KPI layer → Excel/BI → predictive model → business memo.

## What it demonstrates

- Python data generation and reproducible ETL
- SQLite star schema with dimensions, facts, indexes, foreign keys, and a financial view
- SQL joins, CTEs, conditional aggregation, cohorts, and window functions
- data-quality checks and deduplication
- commercial KPIs: net revenue, AOV, margin, returns, repeat purchase, channel economics
- Excel dashboard and Power BI-ready tables/measures
- time-aware repeat-purchase target construction
- logistic-regression and random-forest baselines with ROC-AUC, PR-AUC, F1, Brier score, and lift deciles
- Streamlit dashboard
- tests and GitHub Actions

## Current reproducible snapshot

The deterministic synthetic build produces **30,000 clean orders and 70,439 line items**. On the future 90-day repeat-purchase task, logistic regression reaches **0.664 ROC-AUC**, compared with **0.653** for random forest and **0.500** for the prevalence baseline. The top scored decile has about **1.97×** the overall holdout repeat-purchase rate.

The simpler model winning is part of the point: complexity is not treated as a goal by itself.

## Run

```bash
pip install -r requirements.txt
make all
streamlit run dashboard/app.py
```

Generated raw/processed tables, the SQLite warehouse, large prediction files, figures, and workbook are reproducible build artifacts and are intentionally not required in git.

## Data model

`dim_customer` → `fact_order` → `fact_order_item` ← `dim_product`, with `fact_return` at the order grain.

The raw generator intentionally adds duplicate orders, inconsistent country casing, and missing acquisition-channel values. `pipeline.py` repairs those problems and records the checks in `results/data_quality_report.csv`.

## Modeling rule that matters

The target is whether an existing customer buys again in a future 90-day window. Features are constructed only from activity available before the cutoff. Post-contact or future information is excluded. This is the difference between a model that looks impressive in a notebook and one that could survive a real review.

## Limits

The data are synthetic and therefore **not evidence about a real retailer or causal effects**. The project is evidence of workflow competence: SQL, data modeling, QA, BI, statistical evaluation, and explaining business trade-offs.
