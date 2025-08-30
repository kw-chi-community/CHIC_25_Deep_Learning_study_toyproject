# pages/4_profile_recommend.py
import os
import json
import joblib
from datetime import date
import streamlit as st
from common import search_and_rank_posters, predict_category as predict_category_builtin

st.set_page_config(page_title="Po-You — Profile Recommend", page_icon="✨", layout="wide")

# URL 쿼리파라미터로 pid가 오면 detail로 즉시 이동 (세션도 세팅)
params = st.query_params
if params.get("pid"):
    st.session_state["pid"] = str(params.get("pid"))
    print(f"[DEBUG 4_] query pid detected → {st.session_state['pid']}")
    st.switch_page("pages/3_detail.py")

# poster_rec 아티팩트 로더
ART_DIR = os.getenv("POSTER_REC_DIR", "artifacts")

@st.cache_resource(show_spinner=False)
def load_posterrec():
    clf_path = os.path.join(ART_DIR, "clf.joblib")
    vec_path = os.path.join(ART_DIR, "vectorizer.joblib")
    le_path  = os.path.join(ART_DIR, "label_encoder.json")

    if not (os.path.exists(clf_path) and os.path.exists(vec_path) and os.path.exists(le_path)):
        print(f"[DEBUG 4_] artifacts not found in {ART_DIR}")
        return None, None, None

    try:
        clf = joblib.load(clf_path)
        vectorizer = joblib.load(vec_path)
        with open(le_path, "r", encoding="utf-8") as f:
            label_encoder = json.load(f)  # {"classes":[...]} or {"idx2label":[...]}
        print(f"[DEBUG 4_] artifacts loaded from {ART_DIR}")
        return clf, vectorizer, label_encoder
    except Exception as e:
        st.warning(f"poster_rec 아티팩트 로딩 실패: {e}")
        print(f"[DEBUG 4_] artifact load error: {e}")
        return None, None, None

# ──────────────────────────────────────────────────────────────────────────────
# 텍스트 합성/예측
# ──────────────────────────────────────────────────────────────────────────────
def safe_join(v):
    if v is None: return ""
    if isinstance(v, str): return v
    if isinstance(v, (int, float, bool)): return str(v)
    if isinstance(v, list): return " ".join(safe_join(x) for x in v)
    if isinstance(v, dict): return " ".join(safe_join(x) for x in v.values())
    return str(v)

def build_text(rec: dict) -> str:
    keys = ["제목", "설명", "세부카테고리", "주최기관", "대상", "기간"]
    parts = [safe_join(rec.get(k, "")) for k in keys]
    return " ".join([p for p in parts if p]).strip()

def predict_category_posterrec(rec: dict) -> str:
    clf, vectorizer, label_encoder = load_posterrec()
    text = build_text(rec)
    if not text:
        return "기타"

    if clf is None or vectorizer is None or label_encoder is None:
        return predict_category_builtin(rec)

    try:
        X = vectorizer.transform([text])
        pred_idx = clf.predict(X)[0]
        classes = None
        if isinstance(label_encoder, dict):
            classes = label_encoder.get("idx2label") or label_encoder.get("classes")
        if classes is not None:
            try:
                pred_idx_int = int(pred_idx)
                if 0 <= pred_idx_int < len(classes):
                    return classes[pred_idx_int]
            except Exception:
                pass
        return str(pred_idx)
    except Exception as e:
        st.warning(f"poster_rec 예측 실패: {e}")
        print(f"[DEBUG 4_] predict error: {e}")
        return predict_category_builtin(rec)

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
:root{ --primary-color: #067161; }
.h1{ font-size: 2.2rem; font-weight: 800; color: #fff; }
.status-badge { padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: 700; color: white; }
.status-open { background-color: var(--primary-color); }
.status-soon { background-color: #f59e0b; }
.status-closed { background-color: #6b7280; }
.status-tbd { background-color: #4b5563; }
.stButton > button { background: var(--primary-color) !important; color: white !important; border: 1px solid var(--primary-color) !important; border-radius: 8px !important; }
.stButton > button:hover{ background:#04574d !important; border-color:#04574d !important; }
.poster-card .title{ font-weight:700; font-size:15px; color:#374151 }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="h1">✨ 프로필 기반 맞춤 추천</div>', unsafe_allow_html=True)
st.caption("프로필을 입력하면, poster_rec 모델과 텍스트 유사도를 함께 사용해 맞춤 추천을 제공합니다.")

# ──────────────────────────────────────────────────────────────────────────────
# 폼 (세션 플래그로 제출 상태 유지 → rerun에도 그리드/버튼 유지)
# ──────────────────────────────────────────────────────────────────────────────
with st.form("profile_form"):
    c1, c2, c3 = st.columns([1.4,1,1])
    name   = c1.text_input("닉네임 (선택)")
    age_group = c2.selectbox("연령", ["고등학생", "대학생", "일반", "기타"], index=1)
    region = c3.selectbox("지역", ["전국", "서울/수도권", "경기/인천", "강원", "충청", "전라", "경상", "제주", "해외"], index=0)

    kw_text = st.text_input("관심 키워드 (쉼표로 입력)", value="AI, 해커톤", help="예: AI, 데이터, 창업, 디자인, 공모전, 장학금 …")
    interests = [k.strip() for k in kw_text.split(",") if k.strip()]

    c4, c5 = st.columns(2)
    pref_cats = c4.multiselect("선호 카테고리", ["대회", "모집", "자금", "진로", "행사", "기타"], default=["대회", "모집"])
    status_filter = c5.multiselect("모집 상태", ["모집 중", "시작 전", "모집 완료", "기간 미정"], default=["모집 중", "시작 전"])

    c6, c7 = st.columns(2)
    start_pref = c6.date_input("희망 시작일", value=date.today())
    end_pref   = c7.date_input("희망 마감일", value=date.today())

    extra_desc = st.text_area("추가 설명 (선택)", placeholder="관심 분야/목표/학교/전공 등 자유롭게 적어주세요")

    submitted = st.form_submit_button("추천 보기")

# 폼 제출 상태를 세션으로 유지 (버튼 클릭 rerun에서도 결과 영역이 유지되게)
if submitted:
    st.session_state["profile_ready"] = True
    st.session_state["profile_inputs"] = {
        "name": name, "age_group": age_group, "region": region,
        "interests": interests, "pref_cats": pref_cats, "status_filter": status_filter,
        "start_pref": start_pref, "end_pref": end_pref, "extra_desc": extra_desc
    }
elif not st.session_state.get("profile_ready"):
    st.info("상단 폼을 작성하고 **추천 보기**를 눌러주세요.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# 추천 계산
# ──────────────────────────────────────────────────────────────────────────────
# 세션에서 입력 복원 (rerun 대응)
inputs = st.session_state.get("profile_inputs", {})
name         = inputs.get("name", name)
age_group    = inputs.get("age_group", age_group)
region       = inputs.get("region", region)
interests    = inputs.get("interests", interests)
pref_cats    = inputs.get("pref_cats", pref_cats)
status_filter= inputs.get("status_filter", status_filter)
start_pref   = inputs.get("start_pref", start_pref)
end_pref     = inputs.get("end_pref", end_pref)
extra_desc   = inputs.get("extra_desc", extra_desc)

profile_record = {
    "제목": f"{name or ''} {age_group} {region}",
    "설명": " ".join(interests + ([extra_desc] if extra_desc else [])),
    "세부카테고리": interests,
    "주최기관": [],
    "대상": {"연령": age_group, "지역": region, "특이조건": []},
    "기간": {"start": start_pref.isoformat() if start_pref else "", "end": end_pref.isoformat() if end_pref else ""},
}

predicted_cat = predict_category_posterrec(profile_record)
final_cats = set(pref_cats) if pref_cats else {predicted_cat}

st.success(f"모델 예측 카테고리: **{predicted_cat}**  •  적용 카테고리 필터: **{', '.join(sorted(final_cats))}**")

primary_tag = (interests[0].lower() if interests else None)
ref_date = date.today()

rows = search_and_rank_posters(
    keyword=(" ".join(interests) if interests else None),
    tag=primary_tag,
    categories=final_cats,
    sort_by="Newest",
    ref_date=ref_date,
    statuses=status_filter or None,
)

if not rows:
    st.warning("조건에 맞는 포스터가 없습니다. 필터를 완화하거나 관심 키워드를 늘려보세요.")
    st.stop()

st.markdown(f"#### 추천 결과: {len(rows)}건")

# ──────────────────────────────────────────────────────────────────────────────
# 그리드 렌더 + 상세보기 이동 (세션/쿼리 동시 세팅, 콘솔 디버그 로그)
# ──────────────────────────────────────────────────────────────────────────────
COLS = 5
cols = st.columns(COLS, gap="medium")

for idx, (pid, title, _, tags, image_path, created, folder, status) in enumerate(rows[:25]):
    with cols[idx % COLS]:
        with st.container(border=True):
            if status == "모집 중":
                status_class = "status-open"
            elif status == "시작 전":
                status_class = "status-soon"
            elif status == "모집 완료":
                status_class = "status-closed"
            else:
                status_class = "status-tbd"

            st.markdown(f'<div class="status-badge {status_class}">{status}</div>', unsafe_allow_html=True)
            st.image(image_path, use_container_width=True)
            st.markdown(f'<div class="poster-card"><div class="title">{title}</div></div>', unsafe_allow_html=True)

            btn_key = f"go_{pid}"
            if st.button("상세보기", key=btn_key, use_container_width=True):
                print(f"[DEBUG 4_] click: pid={pid}, key={btn_key}")
                st.session_state["pid"] = str(pid)
                print(f"[DEBUG 4_] session pid set → {st.session_state['pid']}")

                # 세션 유실 대비 URL 쿼리에도 설정
                st.query_params["pid"] = st.session_state["pid"]
                print(f"[DEBUG 4_] query pid set → {st.query_params.get('pid')}")

                st.switch_page("pages/3_detail.py")

st.divider()
st.caption("Tip: 카테고리/상태를 조정하고, 관심 키워드를 2~4개로 조합하면 더 정교한 결과를 볼 수 있어요. "
           "POSTER_REC_DIR 환경변수로 아티팩트 경로를 지정할 수 있습니다.")
