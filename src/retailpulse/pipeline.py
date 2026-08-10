from __future__ import annotations
import csv, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data'/'raw'; PROC=ROOT/'data'/'processed'; RESULTS=ROOT/'results'
PROC.mkdir(parents=True,exist_ok=True); RESULTS.mkdir(parents=True,exist_ok=True)
DB=RESULTS/'retailpulse.db'

CANON_COUNTRY={'uk':'UK','germany':'Germany','france':'France','spain':'Spain','netherlands':'Netherlands','italy':'Italy'}

def read_csv(name):
    with (RAW/name).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write_csv(path, fieldnames, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

def build():
    customers=read_csv('customers.csv')
    products=read_csv('products.csv')
    orders=read_csv('orders.csv')
    items=read_csv('order_items.csv')
    returns=read_csv('returns.csv')

    for r in customers:
        r['country']=CANON_COUNTRY.get(r['country'].strip().lower(),r['country'].strip().title())
        if not r['acquisition_channel'].strip(): r['acquisition_channel']='unknown'

    seen=set(); clean_orders=[]; duplicate_count=0
    for r in orders:
        if r['order_id'] in seen:
            duplicate_count += 1; continue
        seen.add(r['order_id']); clean_orders.append(r)
    order_ids={r['order_id'] for r in clean_orders}
    clean_items=[r for r in items if r['order_id'] in order_ids]
    clean_returns=[r for r in returns if r['order_id'] in order_ids]

    write_csv(PROC/'dim_customer.csv',customers[0].keys(),customers)
    write_csv(PROC/'dim_product.csv',products[0].keys(),products)
    write_csv(PROC/'fact_order.csv',clean_orders[0].keys(),clean_orders)
    write_csv(PROC/'fact_order_item.csv',clean_items[0].keys(),clean_items)
    write_csv(PROC/'fact_return.csv',clean_returns[0].keys(),clean_returns)

    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.executescript('''
    PRAGMA foreign_keys=ON;
    CREATE TABLE dim_customer(customer_id TEXT PRIMARY KEY, signup_date TEXT, country TEXT, acquisition_channel TEXT, customer_segment TEXT);
    CREATE TABLE dim_product(product_id TEXT PRIMARY KEY, category TEXT, subcategory TEXT, unit_cost REAL, list_price REAL);
    CREATE TABLE fact_order(order_id TEXT PRIMARY KEY, customer_id TEXT, order_date TEXT, device TEXT, payment_method TEXT, discount_pct REAL, shipping_fee REAL, status TEXT,
      FOREIGN KEY(customer_id) REFERENCES dim_customer(customer_id));
    CREATE TABLE fact_order_item(order_id TEXT, product_id TEXT, quantity INTEGER, unit_price REAL,
      FOREIGN KEY(order_id) REFERENCES fact_order(order_id), FOREIGN KEY(product_id) REFERENCES dim_product(product_id));
    CREATE TABLE fact_return(order_id TEXT PRIMARY KEY, returned INTEGER, return_date TEXT, return_reason TEXT, refund_amount REAL,
      FOREIGN KEY(order_id) REFERENCES fact_order(order_id));
    CREATE INDEX idx_order_customer ON fact_order(customer_id);
    CREATE INDEX idx_order_date ON fact_order(order_date);
    CREATE INDEX idx_item_product ON fact_order_item(product_id);
    ''')
    cur.executemany('INSERT INTO dim_customer VALUES (?,?,?,?,?)',[(r['customer_id'],r['signup_date'],r['country'],r['acquisition_channel'],r['customer_segment']) for r in customers])
    cur.executemany('INSERT INTO dim_product VALUES (?,?,?,?,?)',[(r['product_id'],r['category'],r['subcategory'],float(r['unit_cost']),float(r['list_price'])) for r in products])
    cur.executemany('INSERT INTO fact_order VALUES (?,?,?,?,?,?,?,?)',[(r['order_id'],r['customer_id'],r['order_date'],r['device'],r['payment_method'],float(r['discount_pct']),float(r['shipping_fee']),r['status']) for r in clean_orders])
    cur.executemany('INSERT INTO fact_order_item VALUES (?,?,?,?)',[(r['order_id'],r['product_id'],int(r['quantity']),float(r['unit_price'])) for r in clean_items])
    cur.executemany('INSERT INTO fact_return VALUES (?,?,?,?,?)',[(r['order_id'],int(r['returned']),r['return_date'],r['return_reason'],float(r['refund_amount'])) for r in clean_returns])
    cur.executescript('''
    CREATE VIEW v_order_financials AS
    WITH item_rollup AS (
      SELECT oi.order_id,
             SUM(oi.quantity*oi.unit_price) AS gross_revenue,
             SUM(oi.quantity*p.unit_cost) AS cogs,
             SUM(oi.quantity) AS units
      FROM fact_order_item oi JOIN dim_product p USING(product_id)
      GROUP BY oi.order_id
    )
    SELECT o.order_id,o.customer_id,o.order_date,o.device,o.payment_method,o.discount_pct,o.shipping_fee,o.status,
           COALESCE(i.gross_revenue,0) gross_revenue, COALESCE(i.cogs,0) cogs, COALESCE(i.units,0) units,
           COALESCE(r.returned,0) returned, COALESCE(r.refund_amount,0) refund_amount,
           CASE WHEN o.status='completed' THEN COALESCE(i.gross_revenue,0)+o.shipping_fee-COALESCE(r.refund_amount,0) ELSE 0 END AS net_revenue,
           CASE WHEN o.status='completed' THEN COALESCE(i.gross_revenue,0)-COALESCE(i.cogs,0)-COALESCE(r.refund_amount,0) ELSE 0 END AS gross_margin
    FROM fact_order o LEFT JOIN item_rollup i USING(order_id) LEFT JOIN fact_return r USING(order_id);
    ''')
    con.commit()

    qa=[]
    qa.append(['raw_order_rows',len(orders)])
    qa.append(['duplicate_orders_removed',duplicate_count])
    qa.append(['clean_orders',len(clean_orders)])
    qa.append(['blank_channels_after_clean',sum(1 for r in customers if not r['acquisition_channel'])])
    qa.append(['orphan_items',sum(1 for r in clean_items if r['order_id'] not in order_ids)])
    qa.append(['unique_customers',len({r['customer_id'] for r in customers})])
    with (RESULTS/'data_quality_report.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['check','value']); w.writerows(qa)
    con.close()
    print(dict(qa))

if __name__=='__main__': build()
