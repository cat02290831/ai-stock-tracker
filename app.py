import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import random

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
    """向 Yahoo 索取資料 (可能會被擋)"""
    ticker = yf.Ticker(yf_symbol)
    return ticker.history(period="1y"), ticker.info

def generate_mock_kline():
    """當 Yahoo 擋住我們時，產生一組備用的 K 線資料維持畫面排版"""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=100)
    data = []
    price = 100
    for d in dates:
        open_p = price + random.uniform(-2, 2)
        close_p = open_p + random.uniform(-3, 3)
        high_p = max(open_p, close_p) + random.uniform(0, 2)
        low_p = min(open_p, close_p) - random.uniform(0, 2)
        vol = random.randint(1000, 10000)
        data.append([open_p, high_p, low_p, close_p, vol])
        price = close_p
    return pd.DataFrame(data, columns=['Open', 'High', 'Low', 'Close', 'Volume'], index=dates)

# 🌟 大腦多重備援機制
def call_gemini(prompt):
    models_to_try = ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest', 'gemini-pro']
    last_error = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue
    return f"AI 暫時離線中... (錯誤資訊: {last_error})"

def draw_kline_chart(stock_name, df, is_mock=False):
    title_suffix = "(⚠️ 備用模擬數據)" if is_mock else "(真實數據)"
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, 
                        subplot_titles=(f'{stock_name} - 近期日線 {title_suffix}', '成交量'), 
                        row_width=[0.2, 0.7])
    increasing_color = '#ef5350' 
    decreasing_color = '#26a69a' 

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線', increasing_line_color=increasing_color, decreasing_line_color=decreasing_color), row=1, col=1)
    
    if 'Volume' in df.columns:
        volume_colors = [increasing_color if close >= open_ else decreasing_color for close, open_ in zip(df['Close'], df['Open'])]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=volume_colors, name='成交量'), row=2, col=1)

    fig.update_xaxes(showspikes=True, spikecolor="gray", spikesnap="cursor", spikemode="across", spikethickness=1)
    fig.update_yaxes(showspikes=True, spikecolor="gray", spikesnap="cursor", spikemode="across", spikethickness=1)
    fig.update_layout(xaxis_rangeslider_visible=False, margin=dict(l=20, r=20, t=40, b=20), height=500, showlegend=True, hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)

# --- 🌟 彈出視窗 (加入絕對防禦) ---
@st.dialog("🤖 AI 投資決策終端", width="large")
def show_stock_details(stock_name, cost_price):
    yf_symbol = yf_ticker_map.get(stock_name)
    stock_id = stock_name.split(" ")[0]
    
    # 🛡️ 絕對防禦機制：攔截 Yahoo 的 RateLimitError
    is_mock = False
    try:
        df, info = fetch_yf_data(yf_symbol)
        if df.empty:
            raise ValueError("Data is empty")
    except Exception as e:
        # 如果失敗，立刻切換為備用模式
        is_mock = True
        df = generate_mock_kline()
        info = {'longBusinessSummary': '⚠️ Yahoo API 流量限制中，無法取得最新公司介紹。'}
        st.warning("⚠️ Yahoo 股市 API 目前遭遇流量限制，圖表與部分資料已自動切換為【備用模式】以維持系統運作。")

    st.markdown(f"### 🎯 {stock_name} 深度分析")
    
    tab_chart, tab_info, tab_ai = st.tabs(["📈 技術圖表", "🏢 公司簡介", "🧠 AI 策略分析"])
    
    with tab_chart:
        draw_kline_chart(stock_name, df, is_mock)
        st.link_button("🔗 Yahoo 完整線圖", f"https://tw.stock.yahoo.com/quote/{stock_id}/technical-analysis")

    with tab_info:
        col_intro, col_segment = st.columns([1.5, 1])
        with col_intro:
            st.markdown("#### **【基本介紹】**")
            raw_summary = info.get('longBusinessSummary', '目前無法取得公司詳細資料。')
            if "流量限制" not in raw_summary and raw_summary != '目前無法取得公司詳細資料。':
                chinese_summary = call_gemini(f"請將以下英文公司介紹翻譯並簡化為 150 字內的繁體中文：{raw_summary}")
                st.write(chinese_summary)
            else:
                st.write(raw_summary)
        with col_segment:
            st.markdown("#### **【業務比重估計】**")
            segments = call_gemini(f"請根據你的知識庫，列出台灣股市代號 {stock_name} 的主要業務營收比重(如：手機30%, 伺服器40%等)，請用繁體中文列點顯示，不要過多贅詞。")
            st.write(segments)

    with tab_ai:
        st.markdown("#### **【普林與索普整合建議】**")
        current_price = df['Close'].iloc[-1]
        prompt = f"""你是資深股票分析師。針對 {stock_name}，目前的股價約 {current_price:.1f}，
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
            # 👉 剛剛就是這裡被切斷了！確保貼上後這一行有被完整關閉括號
            if st.button(f"🎯 {row['stock']}", key=f"link_{i}_{row['stock']}", type="tertiary"):
                show_stock_details(row['stock'], row['cost'])
        row_cols[1].write(row['cost'])
        row_cols[2].write(row['qty'])
