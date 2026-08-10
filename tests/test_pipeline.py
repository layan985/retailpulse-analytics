import csv, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'results'/'retailpulse.db'
def test_orders_unique():
    con=sqlite3.connect(DB); a,b=con.execute('select count(*),count(distinct order_id) from fact_order').fetchone(); con.close(); assert a==b

def test_fk_integrity():
    con=sqlite3.connect(DB); n=con.execute('PRAGMA foreign_key_check').fetchall(); con.close(); assert n==[]

def test_revenue_nonnegative_for_completed():
    con=sqlite3.connect(DB); n=con.execute("select count(*) from v_order_financials where status='completed' and net_revenue<0").fetchone()[0]; con.close(); assert n==0

def test_qa_removed_duplicates():
    with (ROOT/'results'/'data_quality_report.csv').open() as f: d={r['check']:int(r['value']) for r in csv.DictReader(f)}
    assert d['duplicate_orders_removed']>0 and d['orphan_items']==0 and d['blank_channels_after_clean']==0

def test_ml_metrics_exist():
    with (ROOT/'results'/'ml'/'model_metrics.csv').open() as f: rows=list(csv.DictReader(f))
    assert any(r['model']=='random_forest' for r in rows)
