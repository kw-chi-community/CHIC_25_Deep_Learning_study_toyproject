# pages/1_home.py — Grid (행 시작 높이 통일: 고정 썸네일 높이 + 제목 고정 높이)
import streamlit as st
from common import get_posters
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Po-You — Home", page_icon="🏠", layout="wide")

# --- 유틸 ---
@st.cache_data(show_spinner=False)
def img_to_data_uri(path, max_width_px=180):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    if w > max_width_px:
        new_h = int(h * (max_width_px / w))
        img = img.resize((max_width_px, new_h))
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

# --- Query Param: detail 이동 ---
params = st.query_params
if "detail_id" in params:
    try:
        st.session_state["detail_id"] = int(params.get("detail_id"))
    except Exception:
        pass
    try:
        st.switch_page("pages/3_detail.py")
    except Exception:
        pass

# --- CSS ---
CSS = """
<style>
:root{ --wrap:960px; --muted:#6b7280; --line:#e5e7eb; }

.wrap{ max-width:var(--wrap); margin:0 auto; padding:12px 32px; }
.h1{ font-size:26px; font-weight:800; margin:2px 0 8px; }

/* 카테고리 바 */
.catbar{ display:flex; flex-wrap:nowrap; gap:8px; overflow-x:auto; padding-bottom:4px; }
.catbar .stButton{ margin:0; }
.catbar .stButton > button{
  padding:6px 12px; border-radius:9999px; border:1px solid #e5e7eb;
  background:#fff; color:#0f172a; text-decoration:none; white-space:nowrap;
}
.catbar .stButton > button:hover{ border-color:#cbd5e1; }

/* 카드: 행 정렬을 위해 이미지/제목 높이 고정 */
.item{ width:180px; margin-bottom:24px; }  /* 행 간격 */
.card{ display:block; text-decoration:none; padding:0; margin:0; }

/* 포스터: 180×260 고정 박스 + contain(크롭 없음) */
.card .thumb{
  width:180px; height:260px;
  object-fit:contain; object-position:center;
  display:block; margin:0 auto; background:#0b0b0b10;  /* 레터박스 배경(옅게) */
  border-radius:0; box-shadow:0 1px 3px rgba(0,0,0,.06);
}

/* 제목: 2줄 클램프 + 고정 높이 → 다음 행 침범 방지 */
.title{
  font-weight:700; font-size:15px; line-height:1.35;
  max-width:180px; margin:6px auto 0; text-align:left;
  display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow:hidden; text-overflow:ellipsis;
  min-height: calc(1.35em * 2);  /* 두 줄 높이 확보 */
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- 카테고리 설정 ---
CATEGORIES = ["전체", "대회", "모집", "자금", "진로", "행사", "기타"]
cats_qs_raw = params.get("cats")
selected_cats = set()
if cats_qs_raw:
    selected_cats = {c.strip() for c in cats_qs_raw.split(",") if c.strip() in CATEGORIES and c != "전체"}

st.markdown('<div class="wrap">', unsafe_allow_html=True)
st.markdown('<div class="h1">Home — Posters</div>', unsafe_allow_html=True)

with st.expander("🔎 Search / Filter", expanded=False):
    c1, c2, c3 = st.columns([2.2, 2.2, 1.2])
    keyword = c1.text_input("Keyword (제목/설명/태그)", "")
    tag = c2.text_input("Tag contains", "")
    sort_label = c3.selectbox("Sort by", ["Newest", "Title A–Z"], index=0)

    # 카테고리 버튼 바
    st.markdown('<div class="catbar">', unsafe_allow_html=True)
    btn_cols = st.columns(len(CATEGORIES), gap="small")
    for i, name in enumerate(CATEGORIES):
        is_sel = (name != "전체" and name in selected_cats) or (name == "전체" and not selected_cats)
        if btn_cols[i].button(name, key=f"cat_{name}", type=("primary" if is_sel else "secondary")):
            if name == "전체":
                selected_cats.clear()
            else:
                if is_sel: selected_cats.discard(name)
                else:      selected_cats.add(name)
            cats_value = ",".join(sorted(selected_cats)) if selected_cats else None
            if cats_value:
                st.query_params.update({"cats": cats_value})
            else:
                q = dict(st.query_params); q.pop("cats", None)
                st.query_params.clear()
                if q: st.query_params.update(q)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 데이터 조회 & 카테고리 필터 ---
order = "title" if sort_label.startswith("Title") else "new"
rows = get_posters(keyword=keyword or None, tag=tag or None, order=order)

if selected_cats:
    keys = {k.lower() for k in selected_cats}
    filtered = []
    for r in rows:
        _pid, _title, _desc, _tags, _img, _created = r
        t = (_tags or "").lower()
        tags_list = [x.strip() for x in t.split(",") if x.strip()]
        if any((k in tags_list) or (k in t) for k in keys):
            filtered.append(r)
    rows = filtered

if not rows:
    st.info("No posters match current filters. Try different categories or keyword.")
    st.page_link("pages/2_add_poster.py", label="➕ Add Poster")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 6-column grid (columns로, 하지만 카드 높이는 고정이라 행 시작선이 일치) ---
COLS = 6
cols = st.columns(COLS, gap="large")

for idx, row in enumerate(rows):
    pid, title, desc, tags, image_path, created_at = row
    col = cols[idx % COLS]
    with col:
        data_uri = img_to_data_uri(image_path, max_width_px=180)
        href = f"?detail_id={pid}"
        html = f"""
            <div class="item">
              <a class="card" href="{href}">
                <img class="thumb" src="{data_uri}" alt="{title}">
              </a>
              <div class="title">{title}</div>
            </div>
        """
        st.markdown(html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
