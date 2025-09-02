import streamlit as st
from PIL import Image
import base64
from io import BytesIO

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
.stApp { background-color: #ffffff !important; }

/* 기본 텍스트 색상 */
html, body, [class*="css"] { color: #000000 !important; }

/* 제목/문단 색 */
h1, h2, h3, h4, h5, h6, p, span, div { color: #000000 !important; }

/* 사이드바 */
[data-testid="stSidebar"] { background-color: #111827 !important; color:#ffffff !important; }
[data-testid="stSidebar"] * { color:#ffffff !important; }

/* 사이드바 토글(문제되던 콤마 제거!) */
[data-testid="stSidebarCollapser"]::after { content:""; }
/* 필요 없으면 위 줄 자체를 삭제해도 됩니다 */

header[data-testid="stHeader"],
[data-testid="stToolbar"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    box-shadow: none !important;  /* 그림자 제거 */
}

/* ----- HERO ----- */
.hero {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 2px;
  margin: 8px 0 16px 0;
}

.hero-logo {
  width: 200px;
  display: block;
  margin-bottom: 2px;
}

.hero-title {
  color: #067161 !important;
  font-weight: 800;
  margin: 0;
  font-size: 3rem !important;
  line-height: 1.2;
}

.hero-sub {
  font-weight: 500;
  margin: 1rem 0 0.3rem !important;
  font-size: 1.5rem !important;
}

.hero-desc {
  margin-top: 0.2rem;
  color: #000000;
  font-size: 0.95rem;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

img = Image.open("po_you_logo.png")
buf = BytesIO()
img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
st.markdown(CSS, unsafe_allow_html=True)

# --- (2) 로고 data URI 준비 ---
img = Image.open("po_you_logo.png").convert("RGBA")
buf = BytesIO(); img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

# --- (3) 로고 + 텍스트를 하나의 hero 컨테이너로 ---
st.markdown(
    f"""
    <div class="hero">
        <img class="hero-logo" src="data:image/png;base64,{b64}" alt="po_you_logo" />
        <p class="hero-title">Po-You</p>
        <p class="hero-sub">당신에게 딱 맞는 포스터를 찾아드립니다</p>
        <p class="hero-desc">좌측 사이드바 또는 아래 빠른 링크로 이동하세요.</p>
    </div>
    """,
    unsafe_allow_html=True
)

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