import streamlit as st
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

st.set_page_config(
    page_title="Po-You — Poster Exhibition",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="./po_you_logo.png"
)

# --- Global CSS ---
CSS = """
<style>
/* ----- 사이드바 토글 아이콘을 우리 식으로 교체 (단일 블록) ----- */

/* 세 버전 testid를 한 번에 타깃팅 */
[data-testid="stSidebarCollapser"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarNavCollapse"] {
    /* 버튼 안의 기존 텍스트를 보이지 않게 */
    font-size: 0 !important;
}

/* 기본 아이콘(svg 등) 완전 숨김 */
[data-testid="stSidebarCollapser"] svg,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarNavCollapse"] svg {
    display: none !important;
}

/* 필요 시, 기본 콘텐츠 박스(보조 텍스트)도 차단 */
[data-testid="stSidebarCollapser"] *:not(svg),
[data-testid="stSidebarCollapseButton"] *:not(svg),
[data-testid="stSidebarNavCollapse"] *:not(svg) {
    /* 글자 공간 차단을 위해 inline 텍스트는 줄여버림 */
    /* 구조상 다른 요소에 영향이 갈 수 있으므로 font-size:0 방식이 가장 안전 */
}

/* 우리가 보여줄 아이콘(문자)만 붙이기 */
[data-testid="stSidebarCollapser"]::after,
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.title("Po-You: 당신에게 딱 맞는 포스터를 찾아드립니다")
st.markdown("좌측 사이드바 또는 아래 빠른 링크로 이동하세요.")

st.divider()

# --- Quick Links ---
c1, c2, c3, c4= st.columns([1, 1, 1, 1])
with c1:
    st.page_link("pages/1_home.py", label="**🏠 Home**", use_container_width=True)
with c2:
    st.page_link("pages/2_add_poster.py", label="**➕ Add Poster**", use_container_width=True)
with c3:
    st.page_link("pages/3_detail.py", label="**🗒️ View All**", use_container_width=True)
with c4:
    st.page_link("pages/4_profile_recommend.py", label="**✨ Profile Recommend**", use_container_width=True)