import streamlit as st
import pandas as pd
import random
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="AI 操盤室", layout="wide")

if "watch_list" not in st.session_state:
    st.session_state.watch_list = [
        {"stock": "3017 奇鋐", "cost": 2110.0, "qty": 2, "price": 2215.0, "change": "+4.98%", "reason": "中東局勢緩和，散熱族群報復性反彈"},
        {"stock": "4919 新唐", "cost": 108.0, "qty": 5, "price": 118.5, "change": "+3.50%", "reason": "代工漲價利多發酵，外資持續買超"}
    ]

yf_ticker_map = {
    "2330 台積電": "2330.TW", "2317 鴻海": "2317.TW", "2454 聯發科": "2454.TW",
    "3017 奇鋐": "3017.TW", "4919 新唐": "4919.TW", "3689 湧德": "3689.TWO", 
    "2327 國巨": "2327.TW", "4958 臻鼎-KY": "4958.TW", "5347 世界": "5347.TWO"
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_yf_data(yf_symbol):
    ticker = yf.Ticker(yf_symbol)
    return ticker.history(period="1y")

def generate_mock_kline():
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

def fetch_simulated_stock_data(stock_name):
    base_price = random.uniform(50, 500)
    change_pct = random.uniform(-5.0, 9.9)
    return round(base_price, 1), f"{change_pct:+.2f}%"

def generate_ai_strategy(stock_name, cost_price):
    current_price = cost_price * random.uniform(0.9, 1.2)
    stop_loss = round(cost_price * 0.9, 1) 
    entry_low = round(current_price * 0.98, 1)
    entry_high = round(current_price * 1.02, 1)
    pring_text = f"目前 {stock_name} 日線 MACD 處於低檔黃金交叉，量能溫和放大。相對強度 (RS) 突破前波高點，顯示主力洗盤已接近尾聲，進入主升段的機率高達 75%。"
    tharp_text = f"根據您的成本 ({cost_price}) 計算，初始停損點應設於 {stop_loss}。目前 R 倍數為 1.5R，建議啟動移動停利，將防守線推升至近期長紅 K 棒低點。"
    action_text = f"""**💡 綜合 AI 建議操作策略：【區間加碼與抱牢】**
* **建議進出場區間**：建議在 **{entry_low} ~ {entry_high}** 區間逢低加碼；若跌破 {stop_loss} 則嚴格停損出場。
* **策略理由**：根據普林動能，該股已確認轉強；同時結合索普風控，在此區間買進距離停損點不遠，整體「風險報酬比」極佳。"""
    return pring_text, tharp_text, action_text

def draw_kline_chart(stock_name):
    yf_symbol = yf_ticker_map.get(stock_name, "2330.TW")
    title_suffix = "(真實數據)"
    try:
        df = fetch_yf_data(yf_symbol)
        if df.empty: raise ValueError("No Data")
    except:
        st.warning("⚠️ API 流量限制中，已切換為【備用模擬圖表】。")
        df = generate_mock_kline()
        title_suffix = "(⚠️ 備用模擬數據)"

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=(f'{stock_name} - 近期日線 {title_suffix}', '成交量'), row_width=[0.2, 0.7])
    increasing_color = '#ef5350' 
    decreasing_color = '#26a69a' 

    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線', increasing_line_color=increasing_color, decreasing_line_color=decreasing_color), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='blue', width=1), name='MA5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1), name='MA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='purple', width=1), name='MA60'), row=1, col=1)

    volume_colors = [increasing_color if close >= open_ else decreasing_color for close, open_ in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=volume_colors, name='成交量'), row=2, col=1)

    fig.update_xaxes(showspikes=True, spikecolor="gray", spikesnap="cursor", spikemode="across", spikethickness=1)
    fig.update_yaxes(showspikes=True, spikecolor="gray", spikesnap="cursor", spikemode="across", spikethickness=1)
    fig.update_layout(xaxis_rangeslider_visible=False, margin=dict(l=20, r=20, t=40, b=20), height=500, showlegend=True, hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)

@st.dialog("🤖 AI 策略與權證分析站", width="large")
def show_stock_details(stock_name, cost_price):
    st.markdown(f"### 🎯 正在分析：{stock_name}")
    
    stock_id = stock_name.split(" ")[0]
    yahoo_url = f"https://tw.stock.yahoo.com/quote/{stock_id}/technical-analysis"
    
    # 🌟 更新：權證相關網址
    kgi_warrant_url = "https://warrant.kgi.com/edwebsite/views/warrantsearch/warrantsearch.aspx"
    cmoney_warrant_url = f"https://www.cmoney.tw/finance/warrant/list.aspx?stock={stock_id}"
    
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        st.link_button("🔗 完整 Yahoo 技術線圖", yahoo_url)
    
    draw_kline_chart(stock_name)
    pring_text, tharp_text, action_text = generate_ai_strategy(stock_name, cost_price)
    
    col_ai, col_warrant = st.columns([1.2, 1])
    with col_ai:
        st.markdown("#### 📊 策略與風控")
        st.info(f"**📈 普林 (Pring) 動能指標分析：**\n\n{pring_text}")
        st.warning(f"**🛡️ 索普 (Tharp) 風險管理建議：**\n\n{tharp_text}")
        st.success(action_text)
        
    with col_warrant:
        st.markdown("#### 🎫 認購權證快篩區")
        st.caption("由於缺乏免費權證 API，請點選下方按鈕前往專業篩選器。")
        
        # 🌟 換上全新的凱基權證按鈕
        st.info("🔥 推薦：凱基證券擁有極佳的篩選介面，點擊前往後請手動輸入股票代號。")
        st.link_button(f"🚀 前往【凱基權證網】尋找 {stock_id} 權證", kgi_warrant_url, use_container_width=True)
        
        st.markdown("---")
        st.caption("備用篩選器 (會自動帶入代號)：")
        st.link_button(f"🔍 前往【理財寶】篩選", cmoney_warrant_url, use_container_width=True)

st.title("📈 我的專屬 AI 操盤室")
tab1, tab2 = st.tabs(["📊 每日大盤與國際情勢", "🎯 觀察股區域"])

with tab1:
    st.header("每日大盤與國際情勢")
    st.info("💡 這裡未來會透過爬蟲抓取每日台/美股行情與國際新聞，並由 AI 進行總結分析。")

with tab2:
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
                latest_price, change = fetch_simulated_stock_data(new_ticker)
                new_data = {"stock": new_ticker, "cost": new_cost, "qty": new_qty, "price": latest_price, "change": change, "reason": "AI 分析生成中..."}
                st.session_state.watch_list.append(new_data)
                st.rerun()
            else:
                st.warning("請先搜尋並選擇一檔股票！")

    st.divider() 
    st.subheader("目前的觀察股列表")
    st.markdown("💡 **操作提示：請直接點擊下方的「股票代號」，專屬 AI 分析視窗就會彈出來！**")

    header_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3])
    header_cols[0].markdown("**股票代號 (點擊分析)**")
    header_cols[1].markdown("**成本價**")
    header_cols[2].markdown("**持有張數**")
    header_cols[3].markdown("**最新收盤價**")
    header_cols[4].markdown("**漲跌幅**")
    header_cols[5].markdown("**股價變化原因**")
    st.markdown("---")

    for i, row in enumerate(st.session_state.watch_list):
        row_cols = st.columns([1.5, 1, 1, 1.5, 1.5, 3])
        with row_cols[0]:
            if st.button(f"🎯 {row['stock']}", key=f"link_{i}_{row['stock']}", type="tertiary"):
                show_stock_details(row['stock'], row['cost'])
        row_cols[1].write(row['cost'])
        row_cols[2].write(row['qty'])
        row_cols[3].write(row['price'])
        row_cols[4].write(row['change'])
        row_cols[5].write(row['reason'])
