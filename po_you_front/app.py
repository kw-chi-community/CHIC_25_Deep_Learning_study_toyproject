import streamlit as st
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

st.set_page_config(
    page_title="Po-You — Poster Exhibition",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📌"
)

# --- Global CSS ---
CSS = """
<style>
/* 기본 폰트 및 배경색 설정 */
html, body, [class*="st-"], [class*="css-"] {
    font-family: 'Pretendard', sans-serif;
    color: #0d1a2f;
}
[data-testid="stAppViewContainer"] > .main {
    background-color: #f0f2f6;
}
.main .block-container {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 2rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
/* 사이드바 스타일 */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebar"] a { color: #314159; }
[data-testid="stSidebar"] a[aria-current="page"] { background-color: #e6f1f0; }

/* 모든 버튼에 대한 최소한의 공통 스타일만 남깁니다. */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.title("Po-You: 당신에게 딱 맞는 포스터를 찾아드립니다")
st.markdown("좌측 사이드바 또는 아래 빠른 링크로 이동하세요.")

st.divider()

# --- Quick Links ---
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.page_link("pages/1_home.py", label="**🏠 Home**", use_container_width=True)
with c2:
    st.page_link("pages/2_add_poster.py", label="**➕ Add Poster**", use_container_width=True)
with c3:
    st.page_link("pages/3_detail.py", label="**🗒️ View All**", use_container_width=True)