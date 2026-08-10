from __future__ import annotations
import csv, math, random
from datetime import date, datetime, timedelta
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
SEED = 20260810
rng = np.random.default_rng(SEED)
random.seed(SEED)

START = date(2024,1,1)
END = date(2025,6,30)
N_CUSTOMERS = 12000
N_PRODUCTS = 120
N_ORDERS = 30000

countries = ["UK","Germany","France","Spain","Netherlands","Italy"]
country_p = [0.46,0.14,0.12,0.10,0.09,0.09]
channels = ["organic","paid_search","social","email","affiliate"]
channel_p = [0.29,0.24,0.18,0.17,0.12]
segments = ["consumer","small_business","pro"]
segment_p = [0.72,0.18,0.10]
categories = {
    "Home": ["Decor","Kitchen","Storage"],
    "Electronics": ["Accessories","Audio","Smart Home"],
    "Office": ["Stationery","Desk","Organization"],
    "Lifestyle": ["Travel","Fitness","Gifts"],
}
devices=["mobile","desktop","tablet"]
payments=["card","paypal","bank_transfer"]

cust_rows=[]
for i in range(1,N_CUSTOMERS+1):
    signup = START - timedelta(days=int(rng.integers(0, 365))) + timedelta(days=int(rng.integers(0, (END-START).days+1)))
    if signup > END: signup = END - timedelta(days=int(rng.integers(0,120)))
    c = str(rng.choice(countries,p=country_p))
    ch = str(rng.choice(channels,p=channel_p))
    seg = str(rng.choice(segments,p=segment_p))
    cust_rows.append([f"C{i:05d}",signup.isoformat(),c,ch,seg])

for idx in rng.choice(len(cust_rows), size=90, replace=False):
    cust_rows[idx][2] = cust_rows[idx][2].lower() if idx % 2 else cust_rows[idx][2].upper()
for idx in rng.choice(len(cust_rows), size=70, replace=False):
    cust_rows[idx][3] = ""

with (RAW/"customers.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["customer_id","signup_date","country","acquisition_channel","customer_segment"]); w.writerows(cust_rows)

product_rows=[]
product_meta={}
for i in range(1,N_PRODUCTS+1):
    cat = random.choice(list(categories))
    sub = random.choice(categories[cat])
    cost = round(float(rng.uniform(3,95)),2)
    markup = float(rng.uniform(1.35,2.6))
    price = round(cost*markup,2)
    pid=f"P{i:04d}"
    product_rows.append([pid,cat,sub,cost,price])
    product_meta[pid]=(cat,sub,cost,price)
with (RAW/"products.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["product_id","category","subcategory","unit_cost","list_price"]); w.writerows(product_rows)

base_weights = rng.lognormal(mean=0.0, sigma=0.9, size=N_CUSTOMERS)
seg_boost={"consumer":1.0,"small_business":1.6,"pro":2.4}
for i,row in enumerate(cust_rows):
    base_weights[i]*=seg_boost[row[4]]
base_weights=base_weights/base_weights.sum()

days=(END-START).days+1
dates=[START+timedelta(days=i) for i in range(days)]
date_weights=[]
for d in dates:
    seasonal=1.0 + (0.32 if d.month in (11,12) else 0) + (0.10 if d.month in (5,6) else 0)
    weekend=1.08 if d.weekday()>=5 else 1.0
    growth=1+0.00055*(d-START).days
    date_weights.append(seasonal*weekend*growth)
date_weights=np.array(date_weights); date_weights/=date_weights.sum()

orders=[]; items=[]; returns=[]
prod_ids=list(product_meta)
cat_boost={"Electronics":1.15,"Home":1.05,"Office":0.9,"Lifestyle":1.0}
prod_w=np.array([cat_boost[product_meta[p][0]]*rng.uniform(0.7,1.4) for p in prod_ids]); prod_w/=prod_w.sum()

for oid_num in range(1,N_ORDERS+1):
    cidx=int(rng.choice(N_CUSTOMERS,p=base_weights))
    cid=cust_rows[cidx][0]
    od=rng.choice(dates,p=date_weights)
    device=str(rng.choice(devices,p=[0.56,0.36,0.08]))
    payment=str(rng.choice(payments,p=[0.70,0.23,0.07]))
    discount=float(rng.choice([0,0.05,0.10,0.15,0.20,0.25],p=[0.50,0.14,0.15,0.10,0.07,0.04]))
    shipping=0.0 if rng.random()<0.62 else round(float(rng.uniform(3.5,9.5)),2)
    status="completed"
    if rng.random()<0.025: status="cancelled"
    oid=f"O{oid_num:07d}"
    orders.append([oid,cid,od.isoformat(),device,payment,round(discount,2),shipping,status])
    n_items=int(np.clip(rng.poisson(1.35)+1,1,6))
    order_total=0.0
    chosen=rng.choice(prod_ids,size=n_items,replace=False,p=prod_w)
    order_item_rows=[]
    for pid in chosen:
        qty=int(rng.choice([1,2,3,4],p=[0.74,0.19,0.055,0.015]))
        list_price=product_meta[pid][3]
        unit_price=round(list_price*(1-discount),2)
        order_total += qty*unit_price
        order_item_rows.append([oid,pid,qty,unit_price])
    items.extend(order_item_rows)
    if status=="completed":
        cats=[product_meta[r[1]][0] for r in order_item_rows]
        p_ret=0.045 + 0.10*discount + (0.025 if "Electronics" in cats else 0) + (0.012 if n_items>=4 else 0)
        returned = rng.random() < p_ret
        if returned:
            reason=str(rng.choice(["changed_mind","damaged","not_as_described","late_delivery"],p=[0.43,0.21,0.23,0.13]))
            ret_date=(od+timedelta(days=int(rng.integers(3,31)))).isoformat()
            refund=round(order_total*float(rng.uniform(0.55,1.0)),2)
            returns.append([oid,1,ret_date,reason,refund])
        else:
            returns.append([oid,0,"","",0.0])

dup_indices=rng.choice(len(orders),size=85,replace=False)
orders_raw=orders+[orders[int(i)].copy() for i in dup_indices]
rng.shuffle(orders_raw)

for name, hdr, rows in [
    ("orders.csv",["order_id","customer_id","order_date","device","payment_method","discount_pct","shipping_fee","status"],orders_raw),
    ("order_items.csv",["order_id","product_id","quantity","unit_price"],items),
    ("returns.csv",["order_id","returned","return_date","return_reason","refund_amount"],returns),
]:
    with (RAW/name).open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(hdr); w.writerows(rows)

print({"customers":len(cust_rows),"products":len(product_rows),"orders_clean":len(orders),"orders_raw":len(orders_raw),"items":len(items),"returns":len(returns)})
