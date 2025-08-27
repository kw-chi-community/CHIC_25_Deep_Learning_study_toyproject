# pages/3_detail.py — Kyobo-style Detail (3컬럼) — 태그 단일/가로 배치
import os
import streamlit as st
from common import get_posters, get_one, delete_poster

st.set_page_config(page_title="Po-You — Detail", layout="wide")

# --- CSS (Kyobo 톤 / 스티키 우측 패널 / 배지 / 카드) ---
CSS = """
<style>
:root{ --wrap:1180px; --muted:#6b7280; --line:#e5e7eb; --primary:#0ea5e9; }
.wrap{ max-width:1180px; margin:0 auto; padding:10px 12px 12px; }
.breadcrumb{ color:#6b7280; font-size:12.5px; margin-bottom:6px; }
.h1{ font-size:35px; font-weight:800; margin:2px 0 10px; }
.meta{ color:var(--muted); font-size:12.5px; margin-bottom:10px; }
.card{
  background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:12px;
  box-shadow:0 1px 2px rgba(0,0,0,.04),0 6px 20px rgba(0,0,0,.06);
}
.media{ display:flex; justify-content:center; }
.media img{ border-radius:10px; box-shadow:0 10px 24px rgba(0,0,0,.08); }
.kv{ display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 6px; }
.kv .k{ min-width:88px; color:#6b7280; font-size:12.5px; }
.kv .v{ font-size:13.5px; }
.hr{ height:1px; background:var(--line); margin:10px 0; }
.sticky{ position:sticky; top:12px; }
.cta{ display:flex; gap:8px; }
.cta .btn{
  display:inline-block; padding:8px 12px; border-radius:10px; text-align:center; font-weight:700;
  border:1px solid #0284c7; color:#fff; background:#0ea5e9;
}
.cta .ghost{ border:1px solid #e5e7eb; background:#fff; color:#0f172a; }
.footer{ margin-top:18px; padding-top:12px; border-top:1px solid var(--line); }

/* 태그 바: 가로 배치(필요 시 줄바꿈) */
.tags{ display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 12px; }
.badge{ display:inline-block; padding:3px 8px; font-size:12px;
  color:#0f172a; background:#f1f5f9; border:1px solid #e2e8f0; border-radius:9999px; }

/* detail 본문에서 '둥근 긴 바' 유형 입력 위젯 숨김 */
.stTextInput, .stTextArea, .stNumberInput, .stDateInput, .stTimeInput,
.stSelectbox, .stMultiSelect, .stRadio, .stSlider,
div[data-baseweb="input"], div[data-baseweb="select"] { display:none !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="wrap">', unsafe_allow_html=True)

# --- 대상 포스터 선택 (detail_id 우선, 없으면 제목순 첫 항목) ---
pid = st.session_state.get("detail_id")
row = get_one(int(pid)) if pid is not None else None
if row is None:
    rows = get_posters(order="title")
    if rows:
        row = rows[0]
        st.session_state["detail_id"] = row[0]

if row is None:
    st.info("No posters found. Add one first.")
    st.page_link("pages/2_add_poster.py", label="➕ Add Poster")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

pid, title, desc, tags, image_path, created_at = row

# --- 상단 breadcrumb + 타이틀/메타 ---
st.markdown(f'<div class="h1">{title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="meta">Poster ID: {pid} · Created: {created_at}</div>', unsafe_allow_html=True)

# --- 3컬럼 ---
c1, c2, c3 = st.columns([0.32, 0.44, 0.24], gap="large")

# 좌: 미디어 (중앙정렬)
with c1:
    st.markdown('<div class="media">', unsafe_allow_html=True)
    st.image(image_path, width=520)  # use_container_width 금지
    st.markdown('</div>', unsafe_allow_html=True)

# 중: 정보/설명 + ✅ 태그 바(가로 배치, 단일 섹션)
with c2:
    # 태그 바 (있을 때만)
    if tags:
        tag_html = "".join(
            f"<span class='badge'>#{t.strip()}</span>"
            for t in tags.split(",") if t.strip()
        )
        st.markdown(f"<div class='tags'>{tag_html}</div>", unsafe_allow_html=True)

    tabs = st.tabs(["상세", "기록"])
    with tabs[0]:
        st.markdown(
            f"<div style='font-size:16.5px; line-height:1.62'>{(desc or '').replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )
    with tabs[1]:
        st.markdown("변경 이력이 없습니다.")

# 우: 스티키 액션 패널
with c3:
    st.markdown("**Quick Actions**")
    st.markdown('</div>', unsafe_allow_html=True)

    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        st.download_button("Download image", data=img_bytes, file_name=os.path.basename(image_path))
    except Exception:
        st.caption("이미지 파일을 읽을 수 없습니다.")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # 간단 추천
    recs, first_tag = [], None
    if tags:
        for t in [t.strip() for t in tags.split(",") if t.strip()]:
            first_tag = t; break
    if first_tag:
        for r in get_posters(tag=first_tag, order="new"):
            if r[0] != pid:
                recs.append(r)
            if len(recs) >= 3:
                break
    if recs:
        st.markdown("**Similar by tag**")
        for r in recs:
            rid, rtitle, _, rtags, rimg, rcreated = r
            if st.button(f"• {rtitle}", key=f"rec_{rid}"):
                st.session_state["detail_id"] = rid
                try:
                    st.switch_page("pages/3_detail.py")
                except Exception:
                    pass
    else:
        st.caption("유사 태그 포스터가 없습니다.")

# 하단: 삭제 컨트롤
st.markdown('<div class="footer">', unsafe_allow_html=True)
confirm = st.checkbox("Confirm delete")
if st.button("Delete Poster", type="primary", disabled=not confirm):
    try:
        delete_poster(pid)
        st.toast("Deleted.")
        if "detail_id" in st.session_state:
            del st.session_state["detail_id"]
        try:
            st.switch_page("pages/1_home.py")
        except Exception:
            st.success("Return to Home:")
            st.page_link("pages/1_home.py", label="🏠 Home")
    except Exception as e:
        st.error(f"Failed to delete: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # /.wrap
