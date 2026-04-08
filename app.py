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
    st.info("💡 這裡未來會透過爬蟲抓取每日台/美股行情與國際新聞，並由 Gemini AI 進行總結分析。")
    # 預留未來放新聞與大盤走勢圖的空間
    st.markdown("---")
    st.markdown("*(大盤圖表與 AI 摘要預留空間)*")

with tab2:
    st.header("我的觀察股清單")
    
    # --- 1. 新增觀察股的輸入區塊 ---
    st.subheader("新增觀察股")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # 這裡未來會串接台股全部上市櫃名單，目前先放幾檔測試
        # 你可以試著在這個框框輸入「奇」或「23」，它會自動篩選！
        stock_list = ["請選擇...", "2330 台積電", "3017 奇鋐", "4919 新唐", "3689 湧德", "2327 國巨", "4958 臻鼎-KY"]
        new_ticker = st.selectbox("🔍 搜尋股票 (支援代號或中文輸入)", stock_list)
    with col2:
        new_cost = st.number_input("成本價", min_value=0.0, step=0.1)
    with col3:
        new_qty = st.number_input("張數", min_value=1, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True) 
        add_button = st.button("➕ 加入清單")
    
    if add_button:
        if new_ticker != "請選擇...":
            st.success(f"【系統提示】未來會將 {new_ticker} 寫入資料庫！")
        else:
            st.warning("請先搜尋並選擇一檔股票！")

    st.divider() 

    # --- 2. 觀察股列表 (展示區) ---
    st.subheader("目前的觀察股列表")
    
    mock_data = pd.DataFrame({
        "股票代號": ["3017 奇鋐", "4919 新唐", "3689 湧德"],
        "成本價": [2110.0, 108.0, 116.5],
        "持有張數": [2, 5, 3],
        "最新收盤價": [2215.0, 118.5, 126.5],
        "漲跌幅": ["+4.98%", "+3.50%", "+9.80%"],
        "股價變化原因": ["待 AI 自動生成...", "待 AI 自動生成...", "待 AI 自動生成..."],
        "建議策略 (普林與索普)": ["請點選下方個股查看詳情", "請點選下方個股查看詳情", "請點選下方個股查看詳情"]
    })
    st.dataframe(mock_data, use_container_width=True)
    
    st.divider()

    # --- 3. 個股詳細分析與權證篩選區塊 ---
    st.subheader("🤖 AI 策略與權證分析站")
    st.markdown("*(由於網頁表格無法直接點擊，我們使用下拉選單來選擇你想看哪一檔觀察股的詳細資料)*")
    
    # 選擇要查看的股票
    selected_stock = st.selectbox("👉 請選擇要分析的觀察股：", ["3017 奇鋐", "4919 新唐", "3689 湧德"])
    
    # 把畫面切成左右兩半，左邊看 AI 策略，右邊看權證
    col_ai, col_warrant = st.columns([1, 1])
    
    with col_ai:
        st.markdown(f"#### 📊 {selected_stock} - 策略與風控")
        st.info("**📈 普林 (Pring) 動能指標分析：**\n\n*(未來將根據最新 K 線與量價，由 AI 生成動能波段與主力洗盤慣性分析)*")
        st.warning("**🛡️ 索普 (Tharp) 風險管理建議：**\n\n*(未來將讀取您的成本與張數，計算出 R 倍數、移動停利點與部位控管建議)*")
        
    with col_warrant:
        st.markdown(f"#### 🎫 {selected_stock} - 認購權證篩選")
        st.caption("條件自動設定為：到期日 90 天以上、價內外 10% 以內")
        warrant_button = st.button("🔍 點此透過 API 尋找符合條件的權證")
        
        if warrant_button:
            st.success("以下為模擬抓取結果，未來將串接真實報價：")
            mock_warrants = pd.DataFrame({
                "權證名稱": ["奇鋐群益XX購01", "奇鋐元大XX購02"],
                "履約價": [2200, 2300],
                "剩餘天數": [120, 95],
                "價內外": ["+2.5%", "-3.1%"]
            })
            st.dataframe(mock_warrants, use_container_width=True, hide_index=True)
