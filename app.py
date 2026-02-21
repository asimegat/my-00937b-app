import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# 頁面基本設定
st.set_page_config(page_title="00937B 成本計算機", layout="wide")

# 1. 直接內建配息數據 (保證 100% 正確)
def get_dividend_history():
    div_data = {
        'Date': [
            '2024-02-27', '2024-03-18', '2024-04-18', '2024-05-17', '2024-06-18', '2024-07-16',
            '2024-08-16', '2024-09-18', '2024-10-18', '2024-11-18', '2024-12-16',
            '2025-01-16', '2025-02-18', '2025-03-18', '2025-04-16', '2025-05-16', '2025-06-16',
            '2025-07-16', '2025-08-18', '2025-09-16', '2025-10-16', '2025-11-18', '2025-12-16'，
            '2026-01-16'，'2026-02-16'
        ],
        'Amount': [
            0.084, 0.084, 0.084, 0.084, 0.084, 0.084,
            0.082, 0.082, 0.082, 0.082, 0.082,
            0.082, 0.082, 0.080, 0.080, 0.077, 0.077,
            0.072, 0.072, 0.072, 0.072, 0.072, 0.072，
            0.072，0.072
        ]
    }
    df = pd.DataFrame(div_data)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

st.title("📈 00937B 投資損益追蹤")

# 參數輸入區
with st.container():
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        buy_p = st.number_input("買進單價", value=15.54)
    with col_in2:
        shares = st.number_input("持有張數", value=10)
    with col_in3:
        buy_d = st.date_input("買進日期", value=datetime(2023, 12, 1))

    curr_p = st.slider("目前市場價格調整", 14.0, 17.0, 15.10, 0.01)

# 計算邏輯
df_divs = get_dividend_history()
my_divs = df_divs[df_divs['Date'] >= pd.to_datetime(buy_d)]
total_div_per_share = my_divs['Amount'].sum()

total_shares = shares * 1000
invested_amt = buy_p * total_shares
div_cash = total_div_per_share * total_shares
real_cost_per_share = buy_p - total_div_per_share
current_value = curr_p * total_shares
total_profit = (current_value - invested_amt) + div_cash
roi = (total_profit / invested_amt) * 100 if invested_amt != 0 else 0

# 結果顯示
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("實質成本 (每股)", f"{real_cost_per_share:.3f}")
c2.metric("累積領息總額", f"${div_cash:,.0f}")
c3.metric("總報酬率", f"{roi:.2f}%")

# 圓餅圖
fig = go.Figure(data=[go.Pie(
    labels=['剩餘本金', '已領息收', '價差損益'], 
    values=[max(0, invested_amt - div_cash), div_cash, max(0, current_value - invested_amt)],
    hole=.4
)])
st.plotly_chart(fig, use_container_width=True)


