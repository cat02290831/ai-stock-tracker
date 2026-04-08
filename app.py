import streamlit as st
import pandas as pd
import random

# 設定網頁標題與畫面寬度
st.set_page_config(page_title="AI 操盤室", layout="wide")

# --- 🥩 肉 (資料庫區)：使用 Session State 讓資料可以被記憶與新增 ---
if "watch_list" not in st.session_state:
    st.session_state.watch_list = [
        {"stock": "3017 奇鋐", "cost": 2110.0, "qty": 2, "price": 2215.0, "change": "+4.98%", "reason": "中東局勢緩和，散熱族群報復性反彈"},
        {"stock": "4919 新唐", "cost": 108.0, "qty": 5, "price": 118.5, "change": "+3.50%", "reason": "代工漲價利多發酵，外資持續買超"}
    ]

# --- ⚡ 神經 (API 模擬區)：模擬向外部抓取真實報價與 AI 分析 ---
def fetch_simulated_stock_data(stock_name):
    """模擬從證交所或富果 API 抓取最新股價"""
    base_price = random.uniform(50, 500)
    change_pct = random.uniform(-5.0, 9.9)
    return round(base_price, 1), f"{change_pct:+.2f}%"

def generate_ai_strategy(stock_name, cost_price):
    """模擬 AI 根據普林與索普邏輯生成的具體策略"""
    current_price = cost_price * random.uniform(0.9, 1.2) # 模擬目前市價
    stop_loss = round(cost_price * 0.9, 1) # 停損設為成本下 10%
    target_price = round(cost_price * 1.3, 1) # 目標價設為成本上 30%
    entry_low = round(current_price * 0.98, 1)
    entry_high = round(current_price * 1.02, 1)
    
    pring_text = f"目前 {stock_name} 日線 MACD 處於低檔黃金交叉，量能溫和放大。相對強度 (RS) 突破前波高點，顯示主力洗盤已接近尾聲，進入主升段的機率高達 75%。"
    tharp_text = f"根據您的成本 ({cost_price}) 計算，初始停損點應設於 {stop_loss}。目前 R 倍數為 1.5R，建議啟動移動停利，將防守線推升至近期長紅 K 棒低點。"
    
    # 結合兩者給出具體區間與理由
    action_text = f"""**💡 綜合 AI 建議操作策略：【區間加碼與抱牢】**
* **建議進出場區間**：建議在 **{entry_low} ~ {entry_high}** 區間逢低加碼；若跌破 {stop_loss} 則嚴格停損出場。
* **策略理由**：根據普林動能，該股已確認轉強 (突破下降趨勢線)；同時結合索普風控，在此區間 ({entry_low}~{entry_high}) 買進，距離您的停損點不遠，整體的「風險報酬比」極佳。這是一筆勝率與賠率皆具備的交易。"""
    
    return pring_text, tharp_text, action_text

# --- 🌟 定義彈出視窗 (Pop-up Modal) ---
@st.dialog("🤖 AI 策略與權證分析站", width="large")
def show_stock_details(stock_name, cost_price):
    st.markdown(f"### 🎯 正在分析：{stock_name}")
    
    # 呼叫模擬的 AI 引擎生成動態報告
    pring_text, tharp_text, action_text = generate_ai_strategy(stock_name, cost_price)
    
    col_ai, col_warrant = st.columns([1.2, 1])
    
    with col_ai:
        st.markdown("#### 📊 策略與風控")
        st.info(f"**📈 普林 (Pring) 動能指標分析：**\n\n{pring_text}")
        st.warning(f"**🛡️ 索普 (Tharp) 風險管理建議：**\n\n{tharp_text}")
        st.success(action_text)
        
    with col_warrant:
        st.markdown("#### 🎫 認購權證篩選")
        st.caption("條件自動設定為：到期日 90 天以上、價內外 10% 以內")
        if st.button(f"🔍 尋找 {stock_name[:4]} 的權證", key=f"btn_{stock_name}"):
            st.success("API 抓取成功！")
            mock_warrants = pd.DataFrame({
                "權證名稱": [f"{stock_name[:4]}群益01", f"{stock_name[:4]}元大02", f"{stock_name[:4]}凱基03"],
                "履約價": [round(cost_price*1.1, 1), round(cost_price*1.2, 1), round(cost_price*1.05, 1)],
                "剩餘天數": [120, 95, 150],
                "價內外": ["+2.5%", "-3.1%", "+1.2%"]
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
        stock_list = ["請選擇...", "2330 台積電", "2317 鴻海", "2454 聯發科", "3689 湧德", "2327 國巨", "4958 臻鼎-KY"]
        new_ticker = st.selectbox("🔍 搜尋股票", stock_list)
    with col2:
        new_cost = st.number_input("成本價", min_value=0.0, step=0.1)
    with col3:
        new_qty = st.number_input("張數", min_value=1, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True) 
        # 綁定新增按鈕的功能
        if st.button("➕ 加入清單"):
            if new_ticker != "請選擇...":
                # 模擬呼叫 API 取得最新價格
                latest_price, change = fetch_simulated_stock_data(new_ticker)
                
                # 將新資料打包並寫入資料庫 (Session State)
                new_data = {
                    "stock": new_ticker,
                    "cost": new_cost,
                    "qty": new_qty,
                    "price": latest_price,
                    "change": change,
                    "reason": "AI 分析生成中..."
                }
                st.session_state.watch_list.append(new_data)
                
                # 重新整理網頁，讓表格更新
                st.rerun()
            else:
                st.warning("請先搜尋並選擇一檔股票！")

    st.divider() 

    # --- 2. 觀察股列表 (動態資料庫渲染) ---
    st.subheader("目前的觀察股列表")
    st.markdown("💡 **操作提示：請直接點擊下方的「股票代號」，專屬 AI 分析視窗就會彈出來！**")

    # 畫出表格的「標題列」
    header_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3])
    header_cols[0].markdown("**股票代號 (點擊分析)**")
    header_cols[1].markdown("**成本價**")
    header_cols[2].markdown("**持有張數**")
    header_cols[3].markdown("**最新收盤價**")
    header_cols[4].markdown("**漲跌幅**")
    header_cols[5].markdown("**股價變化原因**")
    st.markdown("---")

    # 畫出表格的「資料列」(從 Session State 中讀取真實/新增的資料)
    for i, row in enumerate(st.session_state.watch_list):
        row_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3])
        
        with row_cols[0]:
            # 點擊按鈕後，將該股名稱與成本價傳給 AI 分析引擎
            if st.button(f"🎯 {row['stock']}", key=f"link_{i}_{row['stock']}", type="tertiary"):
                show_stock_details(row['stock'], row['cost'])
        
        row_cols[1].write(row['cost'])
        row_cols[2].write(row['qty'])
        row_cols[3].write(row['price'])
        row_cols[4].write(row['change'])
        row_cols[5].write(row['reason'])
