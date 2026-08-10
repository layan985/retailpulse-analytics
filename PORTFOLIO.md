# How to present RetailPulse

**CV bullet:** Built an end-to-end retail analytics stack over 30k orders: cleaned multi-table raw data, modeled a SQLite warehouse, wrote cohort/margin/retention SQL, shipped an Excel/Streamlit dashboard, and evaluated leakage-safe repeat-purchase classifiers against a prevalence baseline.

**Interview version:** I wanted one project that looked like ordinary analyst work rather than a research prototype. I created raw customers/products/orders/items/returns tables with deliberate quality issues, then built the warehouse and metrics layer before touching ML. The predictive task uses a historical feature window and a future 90-day purchase target, so the model cannot see the outcome period.

Do not describe the synthetic commercial outcomes as real company findings. Describe them as validation results from a reproducible portfolio environment.
