import streamlit as st
from common import get_one_poster, delete_poster_files, search_and_rank_posters, get_recommendation_model, get_poster_status
import os
import time
from datetime import date

st.set_page_config(page_title="Po-You — Detail", page_icon="📋", layout="wide")

# --- CSS ---
CSS = """
<style>
:root{ --primary-color: #067161;}
.h1{ font-size: 2.5rem; font-weight: 800; color: #111827; }
.meta{ color: #6b7280; font-size: 1rem; }
.badge{ color: #374151; background-color: #e5e7eb; border: none; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; }
.info-grid dt { font-weight: 600; color: #1f2937; }
.info-grid dd { color: #4b5563; }
.gallery-card .title { color: #374151;}
.status-badge-detail { display: inline-block; margin-left: 1rem; padding: 4px 12px; border-radius: 9999px; font-size: 1rem; font-weight: 700; color: white; vertical-align: middle;}
.status-open { background-color: var(--primary-color); }
.status-soon { background-color: #f59e0b; }
.status-closed { background-color: #6b7280; }
.status-tbd { background-color: #4b5563; }

/* ✅ --- 이 페이지의 버튼 스타일을 명확하게 재정의 --- ✅ */
/* 1. '자세히 보기' 등 일반 버튼: 녹색 배경, 흰 글씨 */
.stButton > button {
    background: var(--primary-color) !important;
    color: white !important;
    border: 1px solid var(--primary-color) !important;
}
.stButton > button:hover {
    background: #04574d !important;
    border-color: #04574d !important;
}

/* 2. '더보기/간략하게 보기' 버튼: 흰 배경, 녹색 글씨 */
.see-more-container .stButton > button {
    background: white !important;
    color: var(--primary-color) !important;
    border: 1px solid var(--primary-color) !important;
}
.see-more-container .stButton > button:hover {
    background: #e6f1f0 !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="wrap">', unsafe_allow_html=True)


pid = st.session_state.get("pid")

params = st.query_params
if "pid" in params and params.get("pid"):
    st.session_state["pid"] = str(params.get("pid"))

if pid:
    # --- 1. 특정 포스터 상세 보기 모드 ---
    poster = get_one_poster(pid)
    if poster is None:
        st.error("포스터를 찾을 수 없거나 ID가 유효하지 않습니다.")
        if st.button("⬅️ 전체 목록으로 돌아가기"):
            if "pid" in st.session_state: del st.session_state.pid
            st.rerun()
        st.stop()

    if st.button("⬅️ 전체 목록으로 돌아가기"):
        del st.session_state.pid
        st.rerun()

    c1, c2, c3 = st.columns([0.35, 0.40, 0.25], gap="large")
    with c1:
        st.image(poster['image_path'])
    with c2:
        ref_date = date.today()
        status = get_poster_status(poster.get('start_date_str'), poster.get('end_date_str'), ref_date)
        if status == "모집 중": status_class = "status-open"
        elif status == "시작 전": status_class = "status-soon"
        elif status == "모집 완료": status_class = "status-closed"
        else: status_class = "status-tbd"
        
        st.markdown(f"<div class='h1'>{poster['제목']}<span class='status-badge-detail {status_class}'>{status}</span></div>", unsafe_allow_html=True)
        created_str = poster['등록일'].strftime('%Y-%m-%d')
        st.markdown(f"<div class='meta'>Poster ID: {poster['pid']} · Created: {created_str}</div>", unsafe_allow_html=True)
        tags_list = [t.strip() for t in poster['tags'].split(',') if t.strip()]
        if tags_list:
            tag_html = "".join(f"<span class='badge'>#{t}</span>" for t in tags_list)
            st.markdown(f"<div class='tags'>{tag_html}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

        st.markdown("##### **핵심 정보**")
        
        기간 = poster.get('기간', {})
        if 기간 and 기간.get('start') and 기간.get('end'):
            st.markdown(f"""
            <div class="info-grid">
                <dt>🗓️ 기간</dt><dd>{기간.get('start')} ~ {기간.get('end')}</dd>
            </div>
            """, unsafe_allow_html=True)

        대상 = poster.get('대상', {})
        if 대상:
            연령 = 대상.get('연령', '정보 없음')
            지역 = 대상.get('지역', '정보 없음')
            특이조건 = ", ".join(대상.get('특이조건', [])) if 대상.get('특이조건') else "없음"
            st.markdown(f"""
            <div class="info-grid">
                <dt>👥 대상</dt><dd>{연령} / {지역}</dd>
                <dt>ㅤ</dt><dd><b>조건:</b> {특이조건}</dd>
            </div>
            """, unsafe_allow_html=True)

        주최기관 = poster.get('주최기관', [])
        if 주최기관:
            st.markdown(f"""
            <div class="info-grid">
                <dt>🏢 주최/주관</dt><dd>{", ".join(주최기관)}</dd>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
        
        if poster['설명']:
            with st.expander("원본 상세 설명 보기"):
                st.markdown(f"<div style='font-size:14.5px; line-height:1.7;'>{poster['설명'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    with c3:
        st.markdown("##### 퀵 액션")
        try:
            with open(poster['image_path'], "rb") as f:
                st.download_button("이미지 다운로드", data=f.read(), file_name=os.path.basename(poster['image_path']))
        except Exception:
            st.caption("이미지를 다운로드할 수 없습니다.")
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown("##### 유사한 포스터")
        recommendations = search_and_rank_posters(keyword=poster['제목'])
        recs_to_show = [rec for rec in recommendations if rec[0] != poster['pid']][:5]
        if recs_to_show:
            for rec_pid, rec_title, _, _, _, _, _, _ in recs_to_show:
                if st.button(f"• {rec_title}", key=f"rec_{rec_pid}", use_container_width=True):
                    st.session_state["pid"] = rec_pid
                    st.rerun()
    with st.expander("🗑️ 포스터 삭제"):
        st.warning("이 작업은 되돌릴 수 없습니다.")
        confirm = st.checkbox("이 포스터를 영구적으로 삭제합니다.", value=False)
        if st.button("영구 삭제", type="primary", disabled=not confirm):
            delete_poster_files(pid)
            del st.session_state.pid
            st.success("삭제 완료!")
            st.rerun()

else:
    # --- 2. 전체 포스터 갤러리 모드 ('더보기' 기능 추가) ---
    st.markdown("<div class='h1'>전체 포스터 둘러보기 </div>", unsafe_allow_html=True)
    st.markdown("카테고리별로 포스터 목록을 확인하세요. ")
    st.divider()

    df, _, _, _ = get_recommendation_model()

    if df.empty:
        st.info("현재 등록된 포스터가 없습니다.")
    else:
        grouped = df.sort_values(by='등록일', ascending=False).groupby('folder_name')
        INITIAL_DISPLAY_COUNT = 6

        for folder_name, group_df in grouped:
            display_name = folder_name.replace('_json', '')
            st.subheader(f"📂 {display_name} ({len(group_df)}개)")
            
            posters_in_group = group_df.to_dict('records')
            see_more_key = f"see_more_{folder_name}"
            is_expanded = st.session_state.get(see_more_key, False)
            posters_to_show = posters_in_group if is_expanded else posters_in_group[:INITIAL_DISPLAY_COUNT]

            COLS = 6
            cols = st.columns(COLS)
            for idx, poster_item in enumerate(posters_to_show):
                with cols[idx % COLS]:
                    st.markdown(f"<div class='gallery-card'>", unsafe_allow_html=True)
                    st.image(poster_item['image_path'])
                    st.markdown(f"<div class='title'>{poster_item['제목']}</div>", unsafe_allow_html=True)
                    if st.button("자세히 보기", key=f"gallery_{poster_item['pid']}", use_container_width=True):
                        st.session_state.pid = poster_item['pid']
                        st.rerun()
                    st.markdown(f"</div>", unsafe_allow_html=True)
            
            if len(posters_in_group) > INITIAL_DISPLAY_COUNT:
                st.write("") 
                if is_expanded:
                    if st.button("간략하게 보기 🔼", key=f"collapse_{folder_name}", use_container_width=True):
                        st.session_state[see_more_key] = False
                        st.rerun()
                else:
                    remaining_count = len(posters_in_group) - INITIAL_DISPLAY_COUNT
                    if st.button(f"더보기 ({remaining_count}개) 🔽", key=f"expand_{folder_name}", use_container_width=True):
                        st.session_state[see_more_key] = True
                        st.rerun()
            st.divider()

st.markdown('</div>', unsafe_allow_html=True)