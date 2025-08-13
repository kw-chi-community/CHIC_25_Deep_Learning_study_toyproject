# app.py — Landing (환영/안내, 검색/그리드 로직 없음)
import streamlit as st

st.set_page_config(
    page_title="Po-You — Poster Exhibition",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS (라이트 톤 크롬 + 카드/레이아웃) ---
CSS = """
<style>
:root{ --wrap:1180px; --muted:#6b7280; --line:#e5e7eb; }

/* light chrome */
div[data-testid="stHeader"],
section[data-testid="stSidebar"],
section[data-testid="stSidebar"]>div,
div[data-testid="stAppViewContainer"]{
  background:#000 !important;
}

/* wrapper */
.wrap{ max-width:var(--wrap); margin:0 auto; padding:10px 12px 14px; }
.title{ font-size:29px; font-weight:800; margin:4px 0 6px; }
.lead{ color:var(--muted); font-size:16.5px; margin-bottom:12px; }

/* card base */
.card{
  background:#353535; border:1px solid #e5e7eb; border-radius:12px; padding:14px;
  box-shadow:0 1px 2px rgba(0,0,0,.04), 0 6px 20px rgba(0,0,0,.06);
}

/* (Detail용) 불필요한 '둥근 긴 바' 입력 위젯 숨김 */
.stTextInput, .stTextArea, .stNumberInput, .stDateInput, .stTimeInput,
.stSelectbox, .stMultiSelect, .stRadio, .stSlider,
div[data-baseweb="input"], div[data-baseweb="select"] { display:none !important; }

.links a{ margin-right:8px; }
.small{ color:var(--muted); font-size:12.5px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="wrap">', unsafe_allow_html=True)

# --- Hero ---
st.markdown(
    """
<div class="title">Po-You: 대학 포스터 전시</div>
<div class="lead">Kyobo 서가 톤의 전시/탐색 데모입니다. 좌측 사이드바 또는 아래 빠른 링크로 이동하세요.</div>
""",
    unsafe_allow_html=True,
)

# --- Quick Links ---
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.page_link("pages/1_home.py", label="Open Home")
with c2:
    st.page_link("pages/2_add_poster.py", label="Add Poster")
with c3:
    st.page_link("pages/3_detail.py", label="View Detail")

st.divider()

# --- Tips / 안내 카드 ---
st.markdown(
    """
<div class="card">
  <b>Tips</b>
  <ul>
    <li>첫 업로드는 <i>Add Poster</i>에서 진행합니다.</li>
    <li>Home 카드의 <i>Open Detail</i> 버튼으로 세션 상태(<code>detail_id</code>)가 설정됩니다.</li>
    <li>Detail 페이지는 3컬럼 고정폭(중앙 520px)으로 포스터가 터지지 않게 표시됩니다.</li>
  </ul>
  <div class="small">Run: <code>streamlit run app.py</code> · Theme: light only · Folder: <code>po_you_front/</code></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
