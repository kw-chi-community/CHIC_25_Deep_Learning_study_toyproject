import streamlit as st
from common import add_poster_files, predict_category
import os
from datetime import date

st.set_page_config(page_title="Po-You — Add Poster", page_icon="➕", layout="wide")

# --- CSS ---
st.markdown("""
<style>
:root{ --primary-color: #067161; }

main .block-container {
  width:960px !important;
  max-width:960px !important;
  margin:auto !important;
  padding:0 32px !important;
}

div.stTextInput label,
div.stTextArea label,
div.stFileUploader label,
div.stDateInput label,
div.stSelectbox label,
div.stCheckbox label {
  font-size:1.1rem;
  font-weight:600;
}

div[data-testid="stFormSubmitButton"] {
  display:flex !important;
  justify-content:flex-end !important;
}

div[data-testid="stFormSubmitButton"] button {
  background: var(--primary-color) !important;
  color:#fff !important;
  font-weight:700 !important;
  font-size:1rem !important;
  padding:.5rem 1.2rem !important;
  border:none !important;
  border-radius:8px !important;
}

/* 비활성화된 날짜 입력창 스타일 */
div[data-testid="stDateInput"][disabled] {
  cursor: not-allowed;
}
div[data-testid="stDateInput"][disabled] label,
div[data-testid="stDateInput"][disabled] input {
  opacity: 0.5;
}
</style>

""", unsafe_allow_html=True)

# --- 입력 폼 ---
CATEGORIES = ["대회", "모집", "자금", "진로", "행사", "기타"]
st.markdown("### ➕ 새 포스터 추가")

with st.form("add_form", clear_on_submit=True):
    title = st.text_input("제목 *", max_chars=120)
    description = st.text_area("상세 설명", height=160)
    
    c1, c2 = st.columns(2)
    
    is_disabled = st.session_state.get('no_period_check', False)
    
    start_date = c1.date_input("시작일", value=date.today(), disabled=is_disabled)
    end_date = c2.date_input("마감일", value=date.today(), disabled=is_disabled)
    
    no_period = st.checkbox("모집 기간 정보 없음", key='no_period_check')
    
    sub_categories = st.text_input("세부 카테고리 (쉼표로 구분)", placeholder="예: IT, AI, 스타트업")
    st.markdown("---")
    st.markdown("**대상 정보**")
    c1, c2, c3 = st.columns(3)
    target_age = c1.text_input("연령", placeholder="예: 대학생")
    target_region = c2.text_input("지역", placeholder="예: 전국")
    target_etc = c3.text_input("기타 조건 (쉼표로 구분)", placeholder="예: 휴학생 가능")
    hosts = st.text_input("주최 기관 (쉼표로 구분)", placeholder="예: 코딩대학교")
    
    temp_form_data = { "제목": title, "설명": description, "세부카테고리": sub_categories.split(','), "주최기관": hosts.split(','), "대상": {"연령":target_age, "지역":target_region, "특이조건":target_etc.split(',')}}
    predicted_category = predict_category(temp_form_data)
    category_index = CATEGORIES.index(predicted_category) if predicted_category in CATEGORIES else 0
    # category = st.selectbox("주요 카테고리 * ", CATEGORIES, index=category_index)
    
    file = st.file_uploader("포스터 이미지 파일 *", type=["png", "jpg", "jpeg", "webp"])
    submitted = st.form_submit_button("포스터 저장하기")

# --- 폼 제출 후 로직 ---
if 'newly_added_pid' not in st.session_state: st.session_state.newly_added_pid = None

if submitted:
    if not all([title, category, hosts, file]):
        st.error("필수 항목(*)을 모두 입력하거나 파일을 첨부해주세요.")
    else:
        _, extension = os.path.splitext(file.name)
        form_data = {
            "제목": title, "설명": description, "카테고리": category,
            "세부카테고리": [s.strip() for s in sub_categories.split(',') if s.strip()],
            "대상": {"연령": target_age, "지역": target_region, "특이조건": [t.strip() for t in target_etc.split(',') if t.strip()]},
            "기간": {"start": "" if no_period else start_date.isoformat(), "end": "" if no_period else end_date.isoformat()},
            "주최기관": [h.strip() for h in hosts.split(',') if h.strip()]
        }
        try:
            pid = add_poster_files(form_data, file.getvalue(), extension.lower())
            st.session_state.newly_added_pid = pid
            st.rerun()
        except Exception as e:
            st.error(f"저장에 실패했습니다: {e}")

if st.session_state.newly_added_pid:
    st.success(f"포스터가 성공적으로 저장되었습니다!")
    st.page_link("pages/1_home.py", label="🏠 홈으로 가기")
    if st.button("🖼️ 방금 추가한 포스터 보기"):
        st.session_state.pid = st.session_state.newly_added_pid
        st.session_state.newly_added_pid = None
        st.switch_page("pages/3_detail.py")