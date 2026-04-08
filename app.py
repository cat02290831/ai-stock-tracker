import streamlit as st
import pandas as pd

# 設定網頁標題與畫面寬度
st.set_page_config(page_title="AI 操盤室", layout="wide")

# --- 🌟 魔法核心：定義彈出視窗 (Pop-up Modal) 的功能 ---
# 只要加上 @st.dialog，這個區塊就會變成獨立彈出的懸浮視窗！
@st.dialog("🤖 AI 策略與權證分析站", width="large")
def show_stock_details(stock_name):
    st.markdown(f"### 🎯 正在分析：{stock_name}")
    
    # 把彈出視窗切成左右兩半
    col_ai, col_warrant = st.columns([1, 1])
    
    with col_ai:
        st.markdown("#### 📊 策略與風控")
        st.info("**📈 普林 (Pring) 動能指標分析：**\n\n*(未來將根據最新 K 線與量價，由 AI 生成動能波段與主力洗盤慣性分析)*")
        st.warning("**🛡️ 索普 (Tharp) 風險管理建議：**\n\n*(未來將讀取您的成本與張數，計算出R倍數與移動停利點)*")
        
    with col_warrant:
        st.markdown("#### 🎫 認購權證篩選")
        st.caption("條件自動設定為：到期日 90 天以上、價內外 10% 以內")
        
        # 注意：在彈出視窗裡面的按鈕，需要加一個獨立的 key 避免系統搞混
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

    # --- 2. 觀察股列表 (🌟 加入點擊觸發功能) ---
    st.subheader("目前的觀察股列表")
    st.markdown("💡 **操作提示：請點選下方表格「最左側的核取方塊」，專屬 AI 分析視窗就會彈出來！**")
    
    mock_data = pd.DataFrame({
        "股票代號": ["3017 奇鋐", "4919 新唐", "3689 湧德"],
        "成本價": [2110.0, 108.0, 116.5],
        "持有張數": [2, 5, 3],
        "最新收盤價": [2215.0, 118.5, 126.5],
        "漲跌幅": ["+4.98%", "+3.50%", "+9.80%"],
        "股價變化原因": ["待 AI 自動生成...", "待 AI 自動生成...", "待 AI 自動生成..."]
    })
    
    # 開啟 dataframe 的選取功能 (on_select="rerun")
    event = st.dataframe(
        mock_data, 
        use_container_width=True, 
        on_select="rerun",          # 點擊後重新執行程式以觸發動作
        selection_mode="single-row" # 限制一次只能單選一列
    )
    
    # 邏輯判斷：如果系統偵測到有「列」被點選了，就呼叫彈出視窗功能
    if len(event.selection.rows) > 0:
        # 抓出被點選的那一列的索引值
        selected_index = event.selection.rows[0]
        # 根據索引值，抓出該列的「股票代號」
        selected_stock = mock_data.iloc[selected_index]["股票代號"]
        # 呼叫彈出視窗，並把股票代號傳遞進去
        show_stock_details(selected_stock)
