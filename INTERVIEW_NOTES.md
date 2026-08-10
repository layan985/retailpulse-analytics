# Interview notes

Be ready to answer these without opening the code:

1. **Why a star schema?** It keeps customer/product attributes separate from transactional facts, makes grain explicit, and makes BI joins predictable.
2. **What was dirty?** Duplicate order IDs, inconsistent country casing, and missing acquisition channels. The pipeline fixes them and exports a QA report.
3. **Why net revenue instead of gross sales?** Cancelled orders and refunds change the economics. Revenue without those adjustments can mislead.
4. **Why not use accuracy for repeat purchase?** The target is imbalanced; ROC-AUC, average precision, calibration/Brier score, and top-decile lift are more informative.
5. **What is leakage here?** Using any orders after the feature cutoff when predicting whether the customer purchases in the future target window.
6. **Why include a logistic model?** It is an interpretable linear baseline. Complexity has to beat a meaningful baseline, not merely produce a score.
7. **What would you do with real data?** Rebuild the target against actual campaign/business timing, add acquisition cost and contribution margin, use a temporal holdout, assess drift, and validate recommendations with experiments rather than treating model scores as causal.
