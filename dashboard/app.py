from pathlib import Path
import csv
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title='RetailPulse',layout='wide')
st.title('RetailPulse — Revenue & Retention Analytics')
st.caption('Synthetic commerce environment built to demonstrate analyst and junior data-science workflows.')
with (ROOT/'results'/'kpis.csv').open() as f:
    rows=list(csv.DictReader(f)); k=rows[0]
cols=st.columns(5)
cols[0].metric('Orders',f"{int(k['orders']):,}")
cols[1].metric('Active customers',f"{int(k['active_customers']):,}")
cols[2].metric('Net revenue',f"{float(k['net_revenue']):,.0f}")
cols[3].metric('AOV',f"{float(k['aov']):,.2f}")
cols[4].metric('Return rate',f"{100*float(k['return_rate']):.1f}%")
st.subheader('SQL-backed monthly performance')
with (ROOT/'results'/'monthly.csv').open() as f: st.dataframe(list(csv.DictReader(f)),use_container_width=True)
st.subheader('Acquisition channel economics')
with (ROOT/'results'/'channel.csv').open() as f: st.dataframe(list(csv.DictReader(f)),use_container_width=True)
st.subheader('Repeat-purchase model')
with (ROOT/'results'/'ml'/'model_metrics.csv').open() as f: st.dataframe(list(csv.DictReader(f)),use_container_width=True)
