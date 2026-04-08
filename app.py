import streamlit as st
import pandas as pd

# 設定網頁標題與畫面寬度
st.set_page_config(page_title="AI 操盤室", layout="wide")

# --- 🌟 魔法核心：定義彈出視窗 (Pop-up Modal) 的功能 ---
@st.dialog("🤖 AI 策略與權證分析站", width="large")
def show_stock_details(stock_name):
    st.markdown(f"### 🎯 正在分析：{stock_name}")
    
    col_ai, col_warrant = st.columns([1.2, 1]) # 左邊 AI 區稍微寬一點
    
    with col_ai:
        st.markdown("#### 📊 策略與風控")
        st.info("**📈 普林 (Pring) 動能指標分析：**\n\n*(未來將根據最新 K 線與量價，由 AI 生成動能波段與主力洗盤慣性分析)*")
        st.warning("**🛡️ 索普 (Tharp) 風險管理建議：**\n\n*(未來將讀取您的成本與張數，計算出R倍數與移動停利點)*")
        
        # --- 新增的總結操作策略區塊 ---
        st.success("**💡 綜合 AI 建議操作策略 (普林 + 索普)：**\n\n*(未來將綜合上述動能與風控數據，給出明確的「進場/加碼/出場/觀望」建議，以及資金配置比例)*")
        
    with col_warrant:
        st.markdown("#### 🎫 認購權證篩選")
        st.caption("條件自動設定為：到期日 90 天以上、價內外 10% 以內")
        
        if st.button(f"🔍 尋找 {stock_name[:4]} 的權證", key=f"btn_{stock_name}"):
            st.success("抓取成功！(以下為測試資料)")
            mock_warrants = pd.DataFrame({
                "權證名稱": [f"{stock_name[:4]}群益01", f"{stock_name[:4]}元大02"],
                "履約價": [2200, 2300],
                "剩餘天數": [120, 95],
                "價內外": ["+2.5%", "-3.1%"]
            })
            st.dataframe(mock_warrants, use_container_width=True, hide_index=True)


# --- 網站主體開始 ---
st.title("📈 我的專屬 AI 操盤室")

tab1, tab2 = st.tabs(["📊 每日大盤與國際情勢", "🎯 觀察股區域"])

with tab1:
    st.header("每日大盤與國際情勢")
    st.info("💡 這裡未來會透過爬蟲抓取每日台/美股行情與國際新聞，並由 AI 進行總結分析。")

with tab2:
    st.header("我的觀察股清單")
    
    # --- 1. 新增觀察股區塊 ---
    st.subheader("新增觀察股")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stock_list = ["請選擇...", "2330 台積電", "3017 奇鋐", "4919 新唐", "3689 湧德", "2327 國巨", "4958 臻鼎-KY"]
        new_ticker = st.selectbox("🔍 搜尋股票", stock_list)
    with col2:
        new_cost = st.number_input("成本價", min_value=0.0, step=0.1)
    with col3:
        new_qty = st.number_input("張數", min_value=1, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True) 
        if st.button("➕ 加入清單"):
            if new_ticker != "請選擇...":
                st.success(f"收到指令！未來將 {new_ticker} 寫入資料庫！")
            else:
                st.warning("請先搜尋並選擇一檔股票！")

    st.divider() 

    # --- 2. 觀察股列表 (🌟 手工打造的專屬互動表格) ---
    st.subheader("目前的觀察股列表")
    st.markdown("💡 **操作提示：請直接點擊下方的「股票代號」，專屬 AI 分析視窗就會彈出來！**")
    
    # 定義表格資料
    mock_data = [
        {"stock": "3017 奇鋐", "cost": 2110.0, "qty": 2, "price": 2215.0, "change": "+4.98%", "reason": "待 AI 生成..."},
        {"stock": "4919 新唐", "cost": 108.0, "qty": 5, "price": 118.5, "change": "+3.50%", "reason": "待 AI 生成..."},
        {"stock": "3689 湧德", "cost": 116.5, "qty": 3, "price": 126.5, "change": "+9.80%", "reason": "待 AI 生成..."}
    ]

    # 畫出表格的「標題列」
    header_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3]) # 設定每一欄的寬度比例
    header_cols[0].markdown("**股票代號 (點擊分析)**")
    header_cols[1].markdown("**成本價**")
    header_cols[2].markdown("**持有張數**")
    header_cols[3].markdown("**最新收盤價**")
    header_cols[4].markdown("**漲跌幅**")
    header_cols[5].markdown("**股價變化原因**")
    st.markdown("---") # 標題底下的分隔線

    # 畫出表格的「資料列」
    for row in mock_data:
        row_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3])
        
        # 第一欄：使用 tertiary 屬性，把按鈕偽裝成文字超連結
        with row_cols[0]:
            if st.button(f"🎯 {row['stock']}", key=f"link_{row['stock']}", type="tertiary"):
                show_stock_details(row['stock'])
        
        # 其他欄位：正常顯示文字
        row_cols[1].write(row['cost'])
        row_cols[2].write(row['qty'])
        row_cols[3].write(row['price'])
        row_cols[4].write(row['change'])
        row_cols[5].write(row['reason'])
