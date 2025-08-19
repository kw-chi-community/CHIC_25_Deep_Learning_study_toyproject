# pages/2_add_poster.py — 고정폭 960px, 좌우 여백, Save 버튼 오른쪽 붙이기
import streamlit as st
from common import add_poster

st.set_page_config(page_title="Po-You — Add Poster", page_icon="➕", layout="wide")

# ===== 핵심 CSS: Streamlit 기본 컨테이너를 '진짜' 고정폭 + 패딩, 버튼 우측 정렬 =====
st.markdown("""
<style>
/* 1) 메인 컨테이너 고정폭 + 가운데 정렬 + 좌우 여백 */
main .block-container{
  width:960px !important;          /* ← 고정폭 (max-width 아님) */
  max-width:960px !important;
  margin-left:auto !important;
  margin-right:auto !important;
  padding-left:32px !important;    /* 넉넉한 좌우 여백 */
  padding-right:32px !important;
}

/* 2) 폰트 살짝 확대 */
div.stTextInput label, div.stTextArea label, div.stMultiSelect label, div.stFileUploader label{
  font-size:1.1rem; font-weight:600;
}
div.stTextInput input, div.stTextArea textarea, div.stMultiSelect div, div.stFileUploader{
  font-size:1.05rem;
}

/* 3) Save 버튼 오른쪽 붙이기: 래퍼를 flex-end */
div.stForm div.stFormSubmitButton,
div[data-testid="stFormSubmitButton"]{
  display:flex !important;
  justify-content:flex-end !important;   /* ← 오른쪽 끝 */
}

/* 버튼 스타일 + hover */
div[data-testid="stFormSubmitButton"] button{
  background:#4F8BF9 !important;
  color:#fff !important;
  font-weight:700 !important;
  font-size:1rem !important;
  padding:.5rem 1.2rem !important;
  border:none !important;
  border-radius:8px !important;
  transition:background-color .2s ease-in-out !important;
}
div[data-testid="stFormSubmitButton"] button:hover{
  background:#1E6FE1 !important;
}
</style>
""", unsafe_allow_html=True)

CATEGORIES = ["대회", "모집", "자금", "진로", "행사", "기타"]

st.markdown("### Add Poster")

with st.form("add_form", clear_on_submit=False):
    title = st.text_input("Title * (≤120)", max_chars=120)
    desc  = st.text_area("Description", height=160)

    sel_cats   = st.multiselect("Categories (multi-select)", CATEGORIES, help="대회/모집/자금/진로/행사/기타 중 복수 선택 가능")
    tags_input = st.text_input("Tags (comma-separated: contest, seminar, festival)")
    file = st.file_uploader("Poster Image * (png/jpg/jpeg/webp, ≤2MB)", type=["png","jpg","jpeg","webp"])

    submitted = st.form_submit_button("Save Poster")   # ← 이제 오른쪽에 붙음

def _merge_tags(tags_text: str, selected: list) -> str:
    base = [t.strip() for t in (tags_text or "").split(",") if t.strip()]
    for c in selected or []:
        if c not in base:
            base.append(c)
    return ", ".join(base)

if submitted:
    if not title:
        st.error("Title is required."); st.stop()
    if not file:
        st.error("Poster image is required."); st.stop()

    # 2MB 제한
    try:
        size_ok = getattr(file, "size", None)
    except Exception:
        size_ok = None
    if size_ok is not None and size_ok > 2 * 1024 * 1024:
        st.error("File too large (max 2MB)."); st.stop()

    # 확장자
    suffix = None
    try:
        if getattr(file, "type", ""):
            suffix = file.type.split("/")[-1].lower()
        if (not suffix or suffix not in {"png","jpg","jpeg","webp"}) and getattr(file, "name", ""):
            name = file.name.lower()
            for ext in ("png","jpg","jpeg","webp"):
                if name.endswith("." + ext):
                    suffix = ext; break
    except Exception:
        pass
    if suffix not in {"png","jpg","jpeg","webp"}:
        st.error("Unsupported image format. Use png/jpg/jpeg/webp."); st.stop()

    tags_final = _merge_tags(tags_input, sel_cats)

    try:
        pid = add_poster(title, desc, tags_final, file.read(), suffix)
        st.session_state["detail_id"] = pid
        st.success("Poster saved successfully!")
        st.page_link("pages/1_home.py",  label="🏠 Go to Home")
        st.page_link("pages/3_detail.py", label="🖼️ Open Detail Page")
    except Exception as e:
        st.error(f"Failed to save poster: {e}")
