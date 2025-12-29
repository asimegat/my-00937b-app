import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 設定網頁標題
st.set_page_config(page_title="00937B 投資追蹤器", layout="wide")

# 加入快取機制，避免頻繁請求導致被 Yahoo 封鎖
@st.cache_data(ttl=3600)  # 每小時更新一次數據即可
def get_etf_data(ticker_symbol):
    try:
        etf = yf.Ticker(ticker_symbol)
        # 抓取歷史資料來取得最新市價
        hist = etf.history(period="1d")
        if hist.empty:
            return None, None
        current_price = hist['Close'].iloc[-1]
        divs = etf.actions['Dividends']
        return current_price, divs
    except Exception as e:
        return None, None

st.title("📊 00937B 投資損益自動計算機")

# 側邊欄輸入
with st.sidebar:
    st.header("⚙️ 投資參數設定")
    buy_price = st.number_input("買進單價 (NTD)", value=15.54, step=0.01)
    shares = st.number_input("持有張數 (張)", value=10, step=1)
    buy_date = st.date_input("買進日期", value=pd.to_datetime("2023-12-01"))
    st.info("提示：若遇到數據讀取錯誤，請稍候 10 分鐘再重新整理。")

# 執行計算
current_price, divs = get_etf_data("00937B.TW")

if current_price is None:
    st.error("⚠️ 無法從 Yahoo Finance 取得資料。這通常是暫時性的流量限制，請稍後再試。")
else:
    # 轉換日期格式以便比較
    buy_date_dt = pd.to_datetime(buy_date).tz_localize('UTC')
    my_divs = divs[divs.index >= buy_date_dt]
    
    # 核心計算
    total_shares = shares * 1000
    total_div_per_share = my_divs.sum()
    total_dividend_cash = total_div_per_share * total_shares
    total_investment = buy_price * total_shares
    price_gain = (current_price - buy_price) * total_shares
    total_return = total_dividend_cash + price_gain
    adj_cost = buy_price - total_div_per_share

    # 顯示核心指標
    col1, col2, col3 = st.columns(3)
    col1.metric("實質成本 (每股)", f"{adj_cost:.3f}")
    col2.metric("累計領息", f"${total_dividend_cash:,.0f}")
    col3.metric("總報酬率", f"{(total_return/total_investment)*100:.2f}%")

    # 視覺化圖表
    fig = go.Figure(data=[go.Pie(
        labels=['投入本金(剩餘)', '累計已領利息', '未實現價差'], 
        values=[max(0, total_investment - total_dividend_cash), total_dividend_cash, max(0, price_gain)],
        hole=.4,
        marker=dict(colors=['#1f77b4', '#2ca02c', '#ff7f0e'])
    )])
    fig.update_layout(title_text="資產結構分析")
    st.plotly_chart(fig, use_container_width=True)

    st.write(f"📅 **數據更新時間：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.write(f"📈 **目前市價：** {current_price:.2f} 元")
