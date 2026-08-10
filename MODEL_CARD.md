# Repeat-purchase model card

**Task:** rank existing customers by probability of a completed purchase in the next 90 days.

**Feature cutoff:** 2025-02-28.  
**Target window:** 2025-03-01 through 2025-05-31.  
**Population:** customers with at least one completed historical order.

**Models:** prevalence baseline, balanced logistic regression, balanced random forest.

**Primary metrics:** ROC-AUC and average precision. Secondary metrics: precision, recall, F1, Brier score, and lift by score decile.

**Leakage controls:** all behavioral features are computed using orders on or before the cutoff. Future orders appear only in the label CTE.

**Limitations:** synthetic data; no causal interpretation; no marketing cost; no treatment assignment; random customer holdout after a common feature cutoff is not a substitute for later production-time validation.
