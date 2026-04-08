import streamlit as st

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
    st.info("💡 這裡未來可以新增觀察股，並點擊查看普林/索普策略建議與權證資訊。")
