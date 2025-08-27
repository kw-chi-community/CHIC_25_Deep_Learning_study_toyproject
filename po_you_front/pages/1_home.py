import streamlit as st
from common import search_and_rank_posters
from PIL import Image
import base64
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Po-You — Home", page_icon="🏡", layout="wide")

# --- 페이지 이동 로직 ---
params = st.query_params
if "pid" in params:
    st.session_state["pid"] = params.get("pid")
    st.switch_page("pages/3_detail.py")

@st.cache_data(show_spinner=False)
def img_to_data_uri(path):
    try:
        with Image.open(path) as img:
            img = img.convert("RGBA")
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    except Exception:
        return ""

CSS = """
<style>
:root{ --primary-color: #067161;}
.h1{ font-size: 2.5rem; font-weight: 800; color: #111827; margin-bottom: 1rem; }
.catbar{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:1rem; }
.poster-card { position: relative; text-align: center; }
.poster-card .title{ font-weight: 700; font-size: 15px; color: #374151; }
.status-badge-wrapper { position: absolute; top: 8px; left: 8px; z-index: 10; }
.status-badge { padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; color: white; }
.status-open { background-color: var(--primary-color); }
.status-soon { background-color: #f59e0b; }
.status-closed { background-color: #6b7280; }
.status-tbd { background-color: #4b5563; }

.stExpander .stButton button {
    border: 1px solid #067161 !important;
    background-color: white !important;
    color: #067161 !important;
}

/* hover 상태 */
.stExpander .stButton button:hover {
    background-color: #e6f2ef !important; 
    border-color: #067161 !important;
    color: #067161 !important;
}

.stExpander .stButton button[kind="primary"] {
    background-color: #067161 !important;
    border-color: #067161 !important;
    color: white !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="h1">Home — 조건에 맞는 포스터를 찾아드립니다.</div>', unsafe_allow_html=True)

with st.expander("🔎 Search / Filter", expanded=True):
    c1, c2, c3 = st.columns([2.5, 2.5, 1])
    keyword = c1.text_input("Keyword (제목, 설명 등)")
    tag = c2.text_input("Tag contains (세부 태그)")
    sort_label = c3.selectbox("Sort by", ["Newest", "Title A–Z"], index=0)
    
    ref_date = st.date_input("기준 날짜 ", value=date.today())

    st.markdown("---")
    st.markdown("**카테고리**")
    CATEGORIES = ["전체", "대회", "모집", "자금", "진로", "행사", "기타"]
    selected_cats = {c.strip() for c in params.get("cats", "").split(",") if c.strip()}

    st.markdown('<div class="catbar">', unsafe_allow_html=True)
    cols = st.columns(len(CATEGORIES))
    for i, name in enumerate(CATEGORIES):
        is_selected = (name == "전체" and not selected_cats) or (name in selected_cats)
        if cols[i].button(name, key=f"cat_{name}", type="primary" if is_selected else "secondary"):
            if name == "전체": 
                selected_cats.clear()
            elif name in selected_cats: 
                selected_cats.remove(name)
            else: 
                selected_cats.add(name)
            st.query_params["cats"] = ",".join(sorted(list(selected_cats)))
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
if keyword or tag or selected_cats:
    rows = search_and_rank_posters(
        keyword=keyword or None, tag=tag or None,
        categories=selected_cats or None, sort_by=sort_label,
        ref_date=ref_date
    )
    if not rows:
        st.info("조건에 맞는 포스터가 없습니다.")
    else:
        st.success(f"{len(rows)}개의 포스터를 찾았습니다.")
        COLS = 5
        cols = st.columns(COLS, gap="medium")
        for idx, (pid, title, _, _, image_path, _, _, status) in enumerate(rows):
            with cols[idx % COLS]:
                with st.container(border=True):
                    st.markdown(f'<div class="poster-card">', unsafe_allow_html=True)
                    if status == "모집 중": status_class = "status-open"
                    elif status == "시작 전": status_class = "status-soon"
                    elif status == "모집 완료": status_class = "status-closed"
                    else: status_class = "status-tbd"
                    st.markdown(f'<div class="status-badge-wrapper"><span class="status-badge {status_class}">{status}</span></div>', unsafe_allow_html=True)
                    st.image(image_path)
                    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
                    if st.button("상세보기", key=f"btn_{pid}", use_container_width=True):
                        st.session_state.pid = pid
                        st.switch_page("pages/3_detail.py")
                    st.markdown(f'</div>', unsafe_allow_html=True)
else:
    st.info("☝️ 상단 필터나 검색어를 사용하여 포스터를 찾아보세요.")