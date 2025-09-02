# pages/2_add_poster.py
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
  justify-content:flex-end !Important;
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

# --- 입력 폼(즉시 반영 위젯) ---
CATEGORIES = ["대회", "모집", "자금", "진로", "행사", "기타"]
st.markdown("### ➕ 새 포스터 추가")

title = st.text_input("제목 *", max_chars=120, key="title_input")
description = st.text_area("상세 설명", height=160, key="desc_input")

c1, c2 = st.columns(2)
no_period = st.checkbox("모집 기간 정보 없음", key="no_period_check")
start_date = c1.date_input("시작일", value=date.today(), disabled=no_period, key="start_date_input")
end_date   = c2.date_input("마감일", value=date.today(), disabled=no_period, key="end_date_input")

sub_categories = st.text_input("세부 카테고리 (쉼표로 구분)", placeholder="예: IT, AI, 스타트업", key="subcats_input")

st.markdown("---")
st.markdown("**대상 정보**")
c1, c2, c3 = st.columns(3)
target_age = c1.text_input("연령", placeholder="예: 대학생", key="age_input")
target_region = c2.text_input("지역", placeholder="예: 전국", key="region_input")
target_etc = c3.text_input("기타 조건 (쉼표로 구분)", placeholder="예: 휴학생 가능", key="etc_input")

hosts = st.text_input("주최 기관 (쉼표로 구분) *", placeholder="예: 코딩대학교", key="hosts_input")

# 모델 입력 데이터 구성
temp_form_data = {
    "제목": title,
    "설명": description,
    "세부카테고리": [s.strip() for s in (sub_categories or "").split(",") if s.strip()],
    "주최기관": [h.strip() for h in (hosts or "").split(",") if h.strip()],
    "대상": {
        "연령": target_age,
        "지역": target_region,
        "특이조건": [t.strip() for t in (target_etc or "").split(",") if t.strip()]
    }
}

# 모델 추천 자동 적용 여부
use_model = st.toggle("모델 추천 자동 적용", value=True, help="ON이면 입력이 바뀔 때마다 모델 예측값으로 카테고리를 자동 설정합니다.")

# 예측 시그널이 충분할 때만 모델 호출(불필요한 예측 남발 방지)
has_signal = any([
    (title and title.strip()),
    (description and description.strip()),
    temp_form_data["세부카테고리"],
    temp_form_data["주최기관"]
])

predicted_category = ""
if has_signal:
    try:
        predicted_category = predict_category(temp_form_data)
    except Exception as e:
        st.warning(f"카테고리 모델 예측 실패: {e}")

# 카테고리 선택 상태 유지/초기화 로직
if "selected_category" not in st.session_state:
    # 최초 렌더링 시 초기화
    st.session_state.selected_category = predicted_category if predicted_category in CATEGORIES else CATEGORIES[0]
else:
    # 사용자가 자동 적용을 켜두었고, 모델이 유효한 값을 주면 갱신
    if use_model and (predicted_category in CATEGORIES):
        st.session_state.selected_category = predicted_category
    # 자동 적용이 꺼져 있으면 사용자가 선택한 값을 유지

# 카테고리 선택 UI
category = st.selectbox(
    "주요 카테고리 *",
    CATEGORIES,
    index=CATEGORIES.index(st.session_state.selected_category),
    key="selected_category",
    help=(f"모델 추천: {predicted_category}" if predicted_category else "모델 추천값이 없어서 기본값으로 설정됩니다.")
)

file = st.file_uploader("포스터 이미지 파일 *", type=["png", "jpg", "jpeg", "webp"], key="file_input")

# --- 저장 버튼 ---
if st.button("포스터 저장하기", type="primary", use_container_width=False):
    # 필수 항목 검증
    if not (title and title.strip()) or not (hosts and hosts.strip()) or not file:
        st.error("필수 항목(*)을 모두 입력하거나 파일을 첨부해주세요.")
    else:
        _, extension = os.path.splitext(file.name)
        form_data = {
            "제목": title.strip(),
            "설명": (description or "").strip(),
            "카테고리": st.session_state.selected_category,
            "세부카테고리": [s.strip() for s in (sub_categories or "").split(",") if s.strip()],
            "대상": {
                "연령": (target_age or "").strip(),
                "지역": (target_region or "").strip(),
                "특이조건": [t.strip() for t in (target_etc or "").split(",") if t.strip()]
            },
            "기간": {
                "start": "" if no_period else start_date.isoformat(),
                "end":   "" if no_period else end_date.isoformat()
            },
            "주최기관": [h.strip() for h in (hosts or "").split(",") if h.strip()]
        }
        try:
            pid = add_poster_files(form_data, file.getvalue(), extension.lower())
            st.session_state.newly_added_pid = pid
            # 입력값 일부 초기화(원하면 전체 초기화로 변경 가능)
            for k in ["title_input","desc_input","subcats_input","age_input","region_input","etc_input","hosts_input","file_input"]:
                if k in st.session_state: del st.session_state[k]
            st.success("포스터가 성공적으로 저장되었습니다!")
        except Exception as e:
            st.error(f"저장에 실패했습니다: {e}")

# 저장 후 이동 옵션
if st.session_state.get("newly_added_pid"):
    st.page_link("pages/1_home.py", label="🏠 홈으로 가기")
    if st.button("🖼️ 방금 추가한 포스터 보기"):
        st.session_state.pid = st.session_state["newly_added_pid"]
        st.session_state["newly_added_pid"] = None
        st.switch_page("pages/3_detail.py")
