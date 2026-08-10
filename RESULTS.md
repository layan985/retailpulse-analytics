# Results from the synthetic validation run

These numbers come from the deterministic synthetic commerce generator. They validate the pipeline; they are **not claims about a real retailer**.

## Executive layer

- 30,000 cleaned orders after removing 85 duplicate raw order rows.
- 8,861 customers placed at least one order.
- Net revenue: 8,162,749.32 synthetic currency units.
- Average completed-order value: 279.09.
- Return rate: 6.84%.
- Repeat-purchase rate among active customers: 67.23%.

## Commercial analysis

The discount table behaves in a way that creates a useful analyst decision problem. Average gross margin falls from 138.25 at 0% discount to 60.07 at 25% discount. Return rates do not fall enough to offset that margin compression. The correct takeaway is not "never discount"; it is that discount performance should be evaluated on incremental demand and contribution, not gross revenue alone.

Affiliate customers have the highest revenue per customer in this simulation (697.90), while organic contributes the most total revenue because it contains the largest customer base. This is exactly why volume and unit economics should be reported separately.

Electronics has the highest category return rate at 8.04% in the synthetic run, despite also contributing the highest pre-refund margin. A real analyst would investigate reason codes, SKU concentration, and operational costs before recommending any category action.

## Predictive analysis

The feature window ends on 2025-02-28 and the target asks whether the customer makes a completed purchase during the following 90 days.

| Model | ROC-AUC | Avg precision | F1 | Brier |
|---|---:|---:|---:|---:|
| prevalence baseline | 0.500 | 0.365 | 0.000 | 0.232 |
| logistic regression | 0.664 | 0.565 | 0.514 | 0.223 |
| random forest | 0.653 | 0.549 | 0.472 | 0.222 |

Logistic regression wins on discrimination in this run. Its highest-scored decile has a realized repeat rate of 71.7%, roughly 1.97× the overall holdout repeat rate. That is a better portfolio story than choosing the more complicated model by default.

## What I would change with real company data

Use actual acquisition cost and contribution-margin definitions; define the prediction timestamp around a real decision; hold out a later calendar period; add drift monitoring; and test outreach policies experimentally rather than interpreting prediction scores as causal treatment effects.
