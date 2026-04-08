import streamlit as st
import pandas as pd
import yfinance as yf
import google.generativeai as genai

# --- ⚙️ 初始化 Gemini API ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ 偵測不到 API Key，請在 Streamlit Secrets 中設定 GOOGLE_API_KEY")

st.set_page_config(page_title="AI 操盤室", layout="wide")

# --- 🥩 資料庫與對照表 ---
if "watch_list" not in st.session_state:
    st.session_state.watch_list = [
        {"stock": "3017 奇鋐", "cost": 2110.0, "qty": 2, "price": 2215.0},
        {"stock": "4919 新唐", "cost": 108.0, "qty": 5, "price": 118.5}
    ]

yf_ticker_map = {
    "2330 台積電": "2330.TW", "2317 鴻海": "2317.TW", "2454 聯發科": "2454.TW",
    "3017 奇鋐": "3017.TW", "4919 新唐": "4919.TW", "3689 湧德": "3689.TWO", 
    "2327 國巨": "2327.TW", "4958 臻鼎-KY": "4958.TW", "5347 世界": "5347.TWO"
}

# --- ⚡ 核心功能函數 ---
@st.cache_data(ttl=3600)
def fetch_yf_data(yf_symbol):
    """向 Yahoo 索取資料 (只抓最近幾天以取得最新收盤價，降低被擋機率)"""
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d")
        info = ticker.info
        return df, info
    except:
        return pd.DataFrame(), {}

def call_gemini(prompt):
    """鎖定呼叫最穩定且快速的 1.5 Flash 模型"""
    try:
        # 直接指定 1.5-flash，這是目前 API 支援度最高的字串
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 暫時離線中... (錯誤資訊: {str(e)})"

# --- 🌟 彈出視窗 ---
@st.dialog("🤖 AI 投資決策終端", width="large")
def show_stock_details(stock_name, cost_price):
    yf_symbol = yf_ticker_map.get(stock_name)
    stock_id = stock_name.split(" ")[0]
    
    df, info = fetch_yf_data(yf_symbol)

    st.markdown(f"### 🎯 {stock_name} 深度分析")
    
    tab_chart, tab_info, tab_ai = st.tabs(["📈 技術圖表", "🏢 公司簡介", "🧠 AI 策略分析"])
    
    with tab_chart:
        # 捨棄模擬圖表，直接提供 Yahoo 連結
        st.info("💡 為了確保您看到最正確、即時的技術線圖與指標，請點擊下方按鈕前往 Yahoo 股市原生介面查看。")
        st.link_button("🔗 開啟 Yahoo 完整技術線圖", f"https://tw.stock.yahoo.com/quote/{stock_id}/technical-analysis", use_container_width=True)

    with tab_info:
        col_intro, col_segment = st.columns([1.5, 1])
        with col_intro:
            st.markdown("#### **【基本介紹】**")
            raw_summary = info.get('longBusinessSummary', '')
            if raw_summary:
                chinese_summary = call_gemini(f"請將以下英文公司介紹翻譯並簡化為 150 字內的繁體中文：{raw_summary}")
                st.write(chinese_summary)
            else:
                st.warning("目前無法取得公司詳細資料 (可能遭遇 API 阻擋)。")
        with col_segment:
            st.markdown("#### **【業務比重估計】**")
            segments = call_gemini(f"請根據你的知識庫，列出台灣股市代號 {stock_name} 的主要業務營收比重(如：手機30%, 伺服器40%等)，請用繁體中文列點顯示，不要過多贅詞。")
            st.write(segments)

    with tab_ai:
        st.markdown("#### **【普林與索普整合建議】**")
        
        # 取得最新價格交給 AI
        current_price_text = "目前市價未知"
        if not df.empty and len(df) > 0:
            current_price_text = f"目前的股價約 {df['Close'].iloc[-1]:.1f}"

        prompt = f"""你是資深股票分析師。針對 {stock_name}，{current_price_text}，
        使用者的持股成本是 {cost_price}。請結合「普林動能 (Pring)」與「索普風險管理 (Tharp)」給出分析與建議。
        要求：
        1. 給出明確的進場/加碼價格區間。
        2. 根據成本與市價給出停損停利點。
        3. 說明策略理由。
        4. 請用繁體中文回覆，條理分明。"""
        
        with st.spinner("AI 策略運算中..."):
            strategy = call_gemini(prompt)
        st.markdown(strategy)
        
        st.divider()
        st.markdown("#### 🎫 權證快篩")
        st.info("🔥 推薦：點擊前往凱基權證網後，請手動輸入股票代號。")
        st.link_button(f"🚀 前往【凱基權證網】尋找 {stock_id} 權證", "https://warrant.kgi.com/edwebsite/views/warrantsearch/warrantsearch.aspx")

# --- 網站主體 ---
st.title("📈 我的專屬 AI 操盤室")
t1, t2 = st.tabs(["📊 每日大盤摘要", "🎯 觀察股區域"])

with t1:
    st.header("今日國際情勢與大盤")
    if st.button("🔄 點此生成 AI 今日總結"):
        with st.spinner("AI 正在為您彙整全球金融資訊..."):
            summary = call_gemini("請扮演資深總經分析師，總結今日全球金融市場焦點與台股展望，包含美股收盤狀況、重要經濟數據，約 300 字繁體中文。")
        st.success(summary)

with t2:
    st.header("我的觀察股清單")
    st.subheader("新增觀察股")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stock_list = ["請選擇...", "2330 台積電", "2317 鴻海", "2454 聯發科", "3017 奇鋐", "4919 新唐", "3689 湧德", "2327 國巨", "4958 臻鼎-KY", "5347 世界"]
        new_ticker = st.selectbox("🔍 搜尋股票", stock_list)
    with col2:
        new_cost = st.number_input("成本價", min_value=0.0, step=0.1)
    with col3:
        new_qty = st.number_input("張數", min_value=1, step=1)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True) 
        if st.button("➕ 加入清單"):
            if new_ticker != "請選擇...":
                st.session_state.watch_list.append({"stock": new_ticker, "cost": new_cost, "qty": new_qty})
                st.rerun()
            else:
                st.warning("請先搜尋並選擇一檔股票！")

    st.divider() 
    st.subheader("目前的觀察股列表")
    st.markdown("💡 **操作提示：請直接點擊下方的「股票代號」，專屬 AI 分析視窗就會彈出來！**")

    header_cols = st.columns([1.5, 1, 1])
    header_cols[0].markdown("**股票代號 (點擊分析)**")
    header_cols[1].markdown("**成本價**")
    header_cols[2].markdown("**持有張數**")
    st.markdown("---")

    for i, row in enumerate(st.session_state.watch_list):
        row_cols = st.columns([1.5, 1, 1])
        with row_cols[0]:
            if st.button(f"🎯 {row['stock']}", key=f"link_{i}_{row['stock']}", type="tertiary"):
                show_stock_details(row['stock'], row['cost'])
        row_cols[1].write(row['cost'])
        row_cols[2].write(row['qty'])
