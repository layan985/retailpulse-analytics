# Power BI measures
Import the five generated CSVs in `data/processed/` and create relationships on `customer_id`, `product_id`, and `order_id`.

```DAX
Net Revenue = SUMX(fact_order_item, fact_order_item[quantity] * fact_order_item[unit_price]) - SUM(fact_return[refund_amount])
Orders = DISTINCTCOUNT(fact_order[order_id])
Customers = DISTINCTCOUNT(fact_order[customer_id])
AOV = DIVIDE([Net Revenue], [Orders])
Return Rate = DIVIDE(SUM(fact_return[returned]), CALCULATE([Orders], fact_order[status] = "completed"))
Repeat Customers = COUNTROWS(FILTER(VALUES(fact_order[customer_id]), CALCULATE([Orders]) >= 2))
Repeat Rate = DIVIDE([Repeat Customers], [Customers])
```

Suggested pages: Executive Overview; Customer & Channel; Product & Margin; Returns; Retention.
