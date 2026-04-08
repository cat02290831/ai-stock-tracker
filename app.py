import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai

# --- ⚙️ 初始化 Gemini ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
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
    ticker = yf.Ticker(yf_symbol)
    return ticker.history(period="1y"), ticker.info

def call_gemini(prompt):
    """呼叫 Gemini 生成內容"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 暫時離線中... ({e})"

def draw_kline_chart(stock_name, df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.7])
    # ... (省略重複的繪圖邏輯以節省空間，與前版本一致)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線'), row=1, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False, height=450, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- 🌟 彈出視窗 ---
@st.dialog("🤖 AI 投資決策終端", width="large")
def show_stock_details(stock_name, cost_price):
    yf_symbol = yf_ticker_map.get(stock_name)
    df, info = fetch_yf_data(yf_symbol)
    stock_id = stock_name.split(" ")[0]
    
    st.markdown(f"### 🎯 {stock_name} 深度分析")
    
    # 建立功能頁籤
    tab_chart, tab_info, tab_ai = st.tabs(["📈 技術圖表", "🏢 公司簡介", "🧠 AI 策略分析"])
    
    with tab_chart:
        draw_kline_chart(stock_name, df)
        st.link_button("🔗 Yahoo 完整線圖", f"https://tw.stock.yahoo.com/quote/{stock_id}/technical-analysis")

    with tab_info:
        col_intro, col_segment = st.columns([1.5, 1])
        with col_intro:
            st.markdown("#### **【基本介紹】**")
            # 讓 Gemini 翻譯英文介紹
            raw_summary = info.get('longBusinessSummary', '無資料')
            chinese_summary = call_gemini(f"請將以下英文公司介紹翻譯並簡化為 150 字內的繁體中文：{raw_summary}")
            st.write(chinese_summary)
        with col_segment:
            st.markdown("#### **【業務比重估計】**")
            segments = call_gemini(f"請根據你的知識庫，列出 {stock_name} 的主要業務營收比重(如：手機30%, 伺服器40%等)，請用繁體中文列點顯示。")
            st.write(segments)

    with tab_ai:
        st.markdown("#### **【普林與索普整合建議】**")
        prompt = f"""你是資深分析師。針對 {stock_name}，目前的股價約 {df['Close'].iloc[-1]:.1f}，
        使用者的成本是 {cost_price}。請結合「普林動能」與「索普風險管理」給出建議。
        要求：
        1. 給出明確的進場/加碼價格區間。
        2. 說明理由。
        3. 請用繁體中文回覆。"""
        strategy = call_gemini(prompt)
        st.markdown(strategy)
        
        st.divider()
        st.markdown("#### 🎫 權證快篩")
        st.link_button(f"🚀 凱基權證搜尋 (請手動輸入代號)", "https://warrant.kgi.com/edwebsite/views/warrantsearch/warrantsearch.aspx")

# --- 網站主體 ---
st.title("📈 我的專屬 AI 操盤室")
t1, t2 = st.tabs(["📊 每日大盤摘要", "🎯 觀察股區域"])

with t1:
    st.header("今日國際情勢與大盤")
    if st.button("🔄 點此生成 AI 今日總結"):
        summary = call_gemini("請總結今日全球金融市場焦點與台股展望，包含美股收盤、重要經濟數據，約 300 字繁體中文。")
        st.success(summary)

with t2:
    # ... (新增與列表邏輯，與前版本一致)
    for i, row in enumerate(st.session_state.watch_list):
        if st.button(f"🎯 {row['stock']}", key=f"btn_{i}", type="tertiary"):
            show_stock_details(row['stock'], row['cost'])
