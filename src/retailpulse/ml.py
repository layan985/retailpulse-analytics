from __future__ import annotations
import csv, sqlite3
from pathlib import Path
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, brier_score_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]; DB=ROOT/'results'/'retailpulse.db'; OUT=ROOT/'results'/'ml'; OUT.mkdir(parents=True,exist_ok=True)
CUTOFF='2025-02-28'; TARGET_END='2025-05-31'

def build_customer_table(con):
    q="""
    WITH hist AS (
      SELECT o.customer_id,
             COUNT(*) hist_orders,
             SUM(f.net_revenue) hist_revenue,
             AVG(f.net_revenue) hist_aov,
             AVG(o.discount_pct) avg_discount,
             SUM(f.returned) hist_returns,
             MAX(o.order_date) last_order_date
      FROM fact_order o JOIN v_order_financials f USING(order_id)
      WHERE o.status='completed' AND o.order_date <= ?
      GROUP BY o.customer_id
    ), future AS (
      SELECT customer_id,1 repeat_next_90
      FROM fact_order
      WHERE status='completed' AND order_date>? AND order_date<=?
      GROUP BY customer_id
    )
    SELECT h.customer_id,h.hist_orders,h.hist_revenue,h.hist_aov,h.avg_discount,h.hist_returns,
           CAST(julianday(?) - julianday(h.last_order_date) AS INTEGER) recency_days,
           c.country,c.acquisition_channel,c.customer_segment,
           COALESCE(f.repeat_next_90,0) target
    FROM hist h JOIN dim_customer c USING(customer_id) LEFT JOIN future f USING(customer_id)
    WHERE h.hist_orders>=1
    """
    return con.execute(q,(CUTOFF,CUTOFF,TARGET_END,CUTOFF)).fetchall()

def main():
    con=sqlite3.connect(DB); rows=build_customer_table(con); con.close()
    rng=np.random.default_rng(42); idx=np.arange(len(rows)); rng.shuffle(idx); split=int(.8*len(idx)); train_idx=idx[:split]; test_idx=idx[split:]
    X=[]; y=[]; ids=[]
    for r in rows:
        ids.append(r[0]); y.append(int(r[-1])); X.append({
          'hist_orders':float(r[1]),'hist_revenue':float(r[2]),'hist_aov':float(r[3]),'avg_discount':float(r[4]),'hist_returns':float(r[5]),'recency_days':float(r[6]),
          'country='+r[7]:1,'channel='+r[8]:1,'segment='+r[9]:1,
        })
    y=np.array(y)
    models={
      'logistic':make_pipeline(DictVectorizer(sparse=True),StandardScaler(with_mean=False),LogisticRegression(max_iter=2500,class_weight='balanced')),
      'random_forest':make_pipeline(DictVectorizer(sparse=False),RandomForestClassifier(n_estimators=250,min_samples_leaf=8,random_state=42,class_weight='balanced')),
    }
    metrics=[]; preds=[]
    base_rate=float(y[train_idx].mean())
    baseline_prob=np.full(len(test_idx),base_rate)
    metrics.append(['prevalence_baseline',roc_auc_score(y[test_idx],baseline_prob),average_precision_score(y[test_idx],baseline_prob),0,0,0,brier_score_loss(y[test_idx],baseline_prob)])
    for name,m in models.items():
        m.fit([X[i] for i in train_idx],y[train_idx]); prob=m.predict_proba([X[i] for i in test_idx])[:,1]; pred=(prob>=0.5).astype(int)
        metrics.append([name,roc_auc_score(y[test_idx],prob),average_precision_score(y[test_idx],prob),precision_score(y[test_idx],pred,zero_division=0),recall_score(y[test_idx],pred),f1_score(y[test_idx],pred),brier_score_loss(y[test_idx],prob)])
        for j,i in enumerate(test_idx): preds.append([ids[i],name,int(y[i]),float(prob[j])])
    with (OUT/'model_metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['model','roc_auc','avg_precision','precision','recall','f1','brier']); w.writerows(metrics)
    with (OUT/'predictions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['customer_id','model','actual','probability']); w.writerows(preds)
    score_by_name={r[0]:r[1] for r in metrics if r[0] != 'prevalence_baseline'}
    best=max(score_by_name,key=score_by_name.get); p=[r for r in preds if r[1]==best]; p.sort(key=lambda x:x[3],reverse=True); n=len(p); dec=[]
    for d in range(10):
        chunk=p[d*n//10:(d+1)*n//10]; rate=sum(r[2] for r in chunk)/len(chunk); dec.append([d+1,len(chunk),rate,rate/(sum(r[2] for r in p)/n)])
    with (OUT/'lift_by_decile.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['decile','customers','actual_repeat_rate','lift_vs_average']); w.writerows(dec)
    (OUT/'best_model.txt').write_text(best+'\n',encoding='utf-8')
    print('rows',len(rows),'target_rate',y.mean(),'metrics',metrics)
if __name__=='__main__': main()
