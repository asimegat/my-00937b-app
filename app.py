import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="00937B 投資追蹤器", layout="wide")

st.title("📊 00937B 投資損益自動計算機")

# 側邊欄輸入
with st.sidebar:
    st.header("輸入投資參數")
    buy_price = st.number_input("買進單價", value=15.54, step=0.01)
    shares = st.number_input("持有張數", value=10, step=1)
    buy_date = st.date_input("買進日期", value=pd.to_datetime("2023-12-01"))

if st.button("立即計算損益"):
    # 抓取資料
    ticker = yf.Ticker("00937B.TW")
    current_price = ticker.fast_info['last_price']
    divs = ticker.actions['Dividends']
    
    # 過濾配息
    buy_date_dt = pd.to_datetime(buy_date).tz_localize('UTC')
    my_divs = divs[divs.index >= buy_date_dt]
    
    # 計算邏輯
    total_shares = shares * 1000
    total_div_per_share = my_divs.sum()
    total_dividend_cash = total_div_per_share * total_shares
    total_investment = buy_price * total_shares
    current_value = current_price * total_shares
    price_gain = (current_price - buy_price) * total_shares
    total_return = total_dividend_cash + price_gain
    adj_cost = buy_price - total_div_per_share

    # 顯示核心指標
    col1, col2, col3 = st.columns(3)
    col1.metric("實質成本 (每股)", f"{adj_cost:.3f}")
    col2.metric("累積領息", f"${total_dividend_cash:,.0f}")
    col3.metric("總報酬率", f"{(total_return/total_investment)*100:.2f}%")

    # 製作損益結構圓餅圖
    fig = go.Figure(data=[go.Pie(labels=['原始本金', '累計息收', '價差損益'], 
                                 values=[total_investment, total_dividend_cash, max(0, price_gain)],
                                 hole=.3)])
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"目前市價: {current_price} 元")
