from __future__ import annotations
import csv, sqlite3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'results'/'retailpulse.db'; RES=ROOT/'results'; FIG=RES/'figures'; FIG.mkdir(parents=True,exist_ok=True)

QUERIES={
'monthly': """SELECT substr(order_date,1,7) month, COUNT(*) orders, ROUND(SUM(net_revenue),2) net_revenue, ROUND(AVG(CASE WHEN status='completed' THEN net_revenue END),2) aov, ROUND(SUM(gross_margin),2) gross_margin, ROUND(1.0*SUM(returned)/SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),4) return_rate FROM v_order_financials GROUP BY 1 ORDER BY 1""",
'channel': """SELECT c.acquisition_channel, COUNT(DISTINCT c.customer_id) customers, COUNT(DISTINCT f.order_id) orders, ROUND(SUM(f.net_revenue),2) net_revenue, ROUND(1.0*COUNT(DISTINCT f.order_id)/COUNT(DISTINCT c.customer_id),2) orders_per_customer, ROUND(SUM(f.net_revenue)/COUNT(DISTINCT c.customer_id),2) revenue_per_customer FROM dim_customer c LEFT JOIN v_order_financials f USING(customer_id) GROUP BY 1 ORDER BY net_revenue DESC""",
'category': """WITH cat AS (SELECT p.category,oi.order_id,SUM(oi.quantity*oi.unit_price) revenue,SUM(oi.quantity*p.unit_cost) cogs FROM fact_order_item oi JOIN dim_product p USING(product_id) GROUP BY p.category,oi.order_id) SELECT c.category,ROUND(SUM(c.revenue),2) item_revenue,ROUND(SUM(c.revenue-c.cogs),2) pre_refund_margin,COUNT(DISTINCT c.order_id) orders,ROUND(1.0*SUM(COALESCE(r.returned,0))/COUNT(DISTINCT c.order_id),4) order_return_rate FROM cat c LEFT JOIN fact_return r USING(order_id) GROUP BY 1 ORDER BY pre_refund_margin DESC""",
'discount': """SELECT printf('%.0f%%',discount_pct*100) discount_band, COUNT(*) orders, ROUND(AVG(net_revenue),2) avg_net_revenue, ROUND(AVG(gross_margin),2) avg_margin, ROUND(AVG(returned),4) return_rate FROM v_order_financials WHERE status='completed' GROUP BY discount_pct ORDER BY discount_pct""",
'cohort': """WITH first_order AS (SELECT customer_id,MIN(order_date) first_order_date FROM fact_order WHERE status='completed' GROUP BY customer_id), counts AS (SELECT customer_id,COUNT(*) n_orders FROM fact_order WHERE status='completed' GROUP BY customer_id) SELECT substr(f.first_order_date,1,7) cohort_month,COUNT(*) customers,SUM(CASE WHEN c.n_orders>=2 THEN 1 ELSE 0 END) repeat_customers,ROUND(1.0*SUM(CASE WHEN c.n_orders>=2 THEN 1 ELSE 0 END)/COUNT(*),4) repeat_rate FROM first_order f JOIN counts c USING(customer_id) GROUP BY 1 ORDER BY 1"""
}

def export(cur,name,q):
    cur.execute(q); rows=cur.fetchall(); hdr=[d[0] for d in cur.description]
    with (RES/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(hdr); w.writerows(rows)
    return hdr,rows

def main():
    con=sqlite3.connect(DB); cur=con.cursor(); outputs={}
    for n,q in QUERIES.items(): outputs[n]=export(cur,n,q)
    cur.execute("""SELECT COUNT(*) orders, COUNT(DISTINCT customer_id) active_customers, ROUND(SUM(net_revenue),2) net_revenue, ROUND(AVG(CASE WHEN status='completed' THEN net_revenue END),2) aov, ROUND(SUM(gross_margin),2) gross_margin, ROUND(1.0*SUM(returned)/SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),4) return_rate FROM v_order_financials""")
    vals=cur.fetchone(); hdr=[d[0] for d in cur.description]
    with (RES/'kpis.csv').open('w',newline='',encoding='utf-8') as f: csv.writer(f).writerows([hdr,vals])
    cur.execute("""WITH x AS (SELECT customer_id,COUNT(*) n FROM fact_order WHERE status='completed' GROUP BY customer_id) SELECT ROUND(1.0*SUM(CASE WHEN n>=2 THEN 1 ELSE 0 END)/COUNT(*),4) FROM x""")
    repeat=cur.fetchone()[0]
    with (RES/'headline_metrics.txt').open('w',encoding='utf-8') as f:
        f.write(f'orders={vals[0]}\nactive_customers={vals[1]}\nnet_revenue={vals[2]}\naov={vals[3]}\ngross_margin={vals[4]}\nreturn_rate={vals[5]}\nrepeat_purchase_rate={repeat}\n')
    con.close()
    monthly=outputs['monthly'][1]
    months=[r[0] for r in monthly]; rev=[r[2] for r in monthly]
    plt.figure(figsize=(9,4.5)); plt.plot(months,rev,marker='o'); plt.xticks(rotation=45,ha='right'); plt.title('Monthly net revenue'); plt.ylabel('Net revenue'); plt.tight_layout(); plt.savefig(FIG/'monthly_net_revenue.png',dpi=160); plt.close()
    ch=outputs['channel'][1]; labels=[r[0] for r in ch]; rpc=[r[5] for r in ch]
    plt.figure(figsize=(7,4.5)); plt.bar(labels,rpc); plt.xticks(rotation=25,ha='right'); plt.title('Revenue per customer by acquisition channel'); plt.ylabel('Revenue per customer'); plt.tight_layout(); plt.savefig(FIG/'channel_rpc.png',dpi=160); plt.close()
    print(dict(zip(hdr,vals)), 'repeat_purchase_rate', repeat)
if __name__=='__main__': main()
