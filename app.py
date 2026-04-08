import streamlit as st
import pandas as pd

# 設定網頁標題與畫面寬度
st.set_page_config(page_title="AI 操盤室", layout="wide")

# 網站主標題
st.title("📈 我的專屬 AI 操盤室")

# 建立兩個主要功能區塊 (使用頁籤)
tab1, tab2 = st.tabs(["📊 每日大盤與國際情勢", "🎯 觀察股區域"])

with tab1:
    st.header("每日大盤與國際情勢")
    st.info("💡 這裡未來會自動抓取每日台/美股行情與國際新聞，並由 AI 總結。")

with tab2:
    st.header("我的觀察股清單")
    
    # --- 新增觀察股的輸入區塊 ---
    st.subheader("新增觀察股")
    
    # 把畫面分成四個欄位排版
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_ticker = st.text_input("股票代號 (如: 2330)")
    with col2:
        new_cost = st.number_input("成本價", min_value=0.0, step=0.1)
    with col3:
        new_qty = st.number_input("張數", min_value=1, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True) # 往下推一格對齊用
        add_button = st.button("➕ 加入清單")
    
    # 設定按鈕按下去後的動作
    if add_button:
        st.success(f"收到指令！準備將 {new_ticker} (成本: {new_cost}, {new_qty}張) 加入資料庫！(目前為測試版介面)")

    st.divider() # 畫一條分隔線

    # --- 觀察股列表 (展示區) ---
    st.subheader("目前的觀察股 (測試資料)")
    
    # 建立一個測試用的資料表 (DataFrame)
    mock_data = pd.DataFrame({
        "股票代號": ["3017 奇鋐", "4919 新唐", "3689 湧德"],
        "成本價": [2110.0, 108.0, 116.5],
        "持有張數": [2, 5, 3],
        "最新收盤價": [2215.0, 118.5, 126.5],
        "漲跌幅": ["+4.98%", "+3.50%", "+9.80%"],
        "股價變化原因": ["待 AI 生成...", "待 AI 生成...", "待 AI 生成..."],
        "建議策略 (普林與索普)": ["待 AI 分析...", "待 AI 分析...", "待 AI 分析..."]
    })
    
    # 將表格顯示在網頁上
    st.dataframe(mock_data, use_container_width=True)
