-- 1. Executive monthly trend
SELECT substr(order_date,1,7) AS month,
       COUNT(*) AS orders,
       ROUND(SUM(net_revenue),2) AS net_revenue,
       ROUND(AVG(CASE WHEN status='completed' THEN net_revenue END),2) AS aov,
       ROUND(SUM(gross_margin),2) AS gross_margin,
       ROUND(1.0*SUM(returned)/SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),4) AS return_rate
FROM v_order_financials
GROUP BY 1 ORDER BY 1;

-- 2. Acquisition-channel customer economics
SELECT c.acquisition_channel,
       COUNT(DISTINCT c.customer_id) AS customers,
       COUNT(DISTINCT f.order_id) AS orders,
       ROUND(SUM(f.net_revenue),2) AS net_revenue,
       ROUND(1.0*COUNT(DISTINCT f.order_id)/COUNT(DISTINCT c.customer_id),2) AS orders_per_customer,
       ROUND(SUM(f.net_revenue)/COUNT(DISTINCT c.customer_id),2) AS revenue_per_customer
FROM dim_customer c LEFT JOIN v_order_financials f USING(customer_id)
GROUP BY 1 ORDER BY net_revenue DESC;

-- 3. Product-category margin and returns
WITH cat AS (
  SELECT p.category, oi.order_id,
         SUM(oi.quantity*oi.unit_price) revenue,
         SUM(oi.quantity*p.unit_cost) cogs
  FROM fact_order_item oi JOIN dim_product p USING(product_id)
  GROUP BY p.category, oi.order_id
)
SELECT c.category,
       ROUND(SUM(c.revenue),2) AS item_revenue,
       ROUND(SUM(c.revenue-c.cogs),2) AS pre_refund_margin,
       COUNT(DISTINCT c.order_id) AS orders,
       ROUND(1.0*SUM(COALESCE(r.returned,0))/COUNT(DISTINCT c.order_id),4) AS order_return_rate
FROM cat c LEFT JOIN fact_return r USING(order_id)
GROUP BY 1 ORDER BY pre_refund_margin DESC;

-- 4. Repeat-purchase rate by cohort month
WITH first_order AS (
  SELECT customer_id, MIN(order_date) first_order_date FROM fact_order WHERE status='completed' GROUP BY customer_id
), counts AS (
  SELECT o.customer_id, COUNT(*) n_orders FROM fact_order o WHERE o.status='completed' GROUP BY o.customer_id
)
SELECT substr(f.first_order_date,1,7) cohort_month,
       COUNT(*) customers,
       SUM(CASE WHEN c.n_orders>=2 THEN 1 ELSE 0 END) repeat_customers,
       ROUND(1.0*SUM(CASE WHEN c.n_orders>=2 THEN 1 ELSE 0 END)/COUNT(*),4) repeat_rate
FROM first_order f JOIN counts c USING(customer_id)
GROUP BY 1 ORDER BY 1;

-- 5. Discount efficiency
SELECT printf('%.0f%%',discount_pct*100) discount_band,
       COUNT(*) orders,
       ROUND(AVG(net_revenue),2) avg_net_revenue,
       ROUND(AVG(gross_margin),2) avg_margin,
       ROUND(AVG(returned),4) return_rate
FROM v_order_financials WHERE status='completed'
GROUP BY discount_pct ORDER BY discount_pct;

-- 6. High-value customer ranking with window function
WITH spend AS (
 SELECT customer_id, COUNT(*) orders, SUM(net_revenue) net_revenue
 FROM v_order_financials WHERE status='completed' GROUP BY customer_id
)
SELECT customer_id,orders,ROUND(net_revenue,2) net_revenue,
       DENSE_RANK() OVER(ORDER BY net_revenue DESC) revenue_rank
FROM spend ORDER BY revenue_rank LIMIT 50;
