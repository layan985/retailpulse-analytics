# Data dictionary

- `dim_customer`: one row per customer; signup date, normalized country, acquisition channel, segment.
- `dim_product`: one row per product; category, subcategory, unit cost, list price.
- `fact_order`: one row per order; date, device, payment, discount, shipping, status.
- `fact_order_item`: one row per order-product line; quantity and realized unit price.
- `fact_return`: one row per order; return flag, reason, refund amount.
- `v_order_financials`: order-level derived layer with gross revenue, COGS, refunds, net revenue, margin, and units.
