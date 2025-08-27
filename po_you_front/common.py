import streamlit as st 
import pandas as pd  
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity  
import json  
import os  
import glob 
from datetime import datetime, date
import time  
import uuid 
import joblib
import re

DATA_DIR = "json"
MODEL_PATH = "category_classifier.pkl"
os.makedirs(DATA_DIR, exist_ok=True)

def flatten_json_field(field_data):
    tags = []
    if isinstance(field_data, list):
        tags.extend(field_data)
    elif isinstance(field_data, dict):
        for value in field_data.values():
            if isinstance(value, list):
                tags.extend(value)
            else:
                tags.append(str(value))
    elif field_data:
        tags.append(str(field_data))
    return [str(t).strip() for t in tags if t]

@st.cache_resource
def load_classifier_model():
    if not os.path.exists(MODEL_PATH): return None
    try: return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"모델 로딩 실패: {e}")
        return None

def safe_join(v):
    if v is None: return ""
    if isinstance(v, str): return v
    if isinstance(v, (int, float, bool)): return str(v)
    if isinstance(v, list): return " ".join(safe_join(x) for x in v)
    if isinstance(v, dict): return " ".join(safe_join(x) for x in v.values())
    return str(v)

def extract_text_for_prediction(rec):
    parts = []
    for key in ["제목", "설명", "세부카테고리", "주최기관", "대상", "기간"]:
        if key in rec: parts.append(safe_join(rec[key]))
    return re.sub(r"\\s+", " ", " ".join(parts)).strip()

def predict_category(form_data):
    model = load_classifier_model()
    if model is None:
        st.warning("카테고리 분류 모델(`category_classifier.pkl`)을 찾을 수 없습니다. `train_model.py`를 실행해주세요.")
        return "기타"
    text_to_predict = extract_text_for_prediction(form_data)
    if not text_to_predict.strip(): return "기타"
    try:
        prediction = model.predict([text_to_predict])
        return prediction[0] if prediction else "기타"
    except Exception as e:
        print(f"카테고리 예측 실패: {e}")
        return "기타"

def get_poster_status(start_str, end_str, ref_date):
    if not start_str or not end_str: return "기간 미정"
    try:
        start_date_obj = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_str, "%Y-%m-%d").date()
        if ref_date < start_date_obj: return "시작 전"
        elif start_date_obj <= ref_date <= end_date_obj: return "모집 중"
        else: return "모집 완료"
    except (ValueError, TypeError):
        return "기간 미정"

@st.cache_data
def get_recommendation_model():
    all_posters_data = []
    error_logs = []
    metadata_files = glob.glob(os.path.join(DATA_DIR, '**', '*.json'), recursive=True) + \
                     glob.glob(os.path.join(DATA_DIR, '**', '*.txt'), recursive=True)

    for file_path in metadata_files:
        try:
            dir_name = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            folder_name = os.path.basename(dir_name)

            with open(file_path, 'r', encoding='utf-8-sig') as f: data = json.load(f)

            image_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                potential_path = os.path.join(dir_name, f"{base_name}{ext}")
                if os.path.exists(potential_path):
                    image_path = potential_path; break
            if not image_path:
                clean_base_name = '_'.join(base_name.split('_')[:-1]) if '_' in base_name else base_name
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    potential_path = os.path.join(dir_name, f"{clean_base_name}{ext}")
                    if os.path.exists(potential_path):
                        image_path = potential_path; break
            if not image_path:
                error_logs.append(f"이미지 파일 없음: '{file_path}'")
                continue

            poster_info = {
                'pid': base_name, 'image_path': image_path, 'folder_name': folder_name,
                '제목': data.get('제목', ''), '설명': data.get('설명', ''),
                '카테고리': data.get('카테고리', ''), '세부카테고리': data.get('세부카테고리', []),
                '대상': data.get('대상', {}), '주최기관': data.get('주최기관', []),
                '기간': data.get('기간', {})
            }
            start_date_str = poster_info['기간'].get('start')
            poster_info['start_date_str'] = start_date_str
            poster_info['end_date_str'] = poster_info['기간'].get('end')
            poster_info['등록일'] = pd.to_datetime(start_date_str, errors='coerce') if start_date_str else datetime.fromtimestamp(os.path.getmtime(file_path))
            all_posters_data.append(poster_info)
        except Exception as e:
            error_logs.append(f"파일 처리 오류 '{file_path}': {e}")

    if not all_posters_data:
        return pd.DataFrame(), None, None, error_logs

    df = pd.DataFrame(all_posters_data).drop_duplicates(subset=['pid']).dropna(subset=['등록일']).fillna('')
    def create_tags(row):
        tags = set([row['카테고리']])
        tags.update(flatten_json_field(row['세부카테고리']))
        tags.update(flatten_json_field(row['대상']))
        tags.update(flatten_json_field(row['주최기관']))
        return ", ".join(sorted([t.lower() for t in tags if t]))
    df['tags'] = df.apply(create_tags, axis=1)
    df['search_content'] = df['제목'] + " " + df['설명'] + " " + df['tags']
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(df['search_content'])
    return df, vectorizer, matrix, error_logs

def search_and_rank_posters(keyword=None, tag=None, categories=None, sort_by='Newest', ref_date=None, statuses=None):
    model_data = get_recommendation_model()
    if model_data is None or model_data[0] is None:
        return []
    
    df, vectorizer, matrix, _ = model_data
    if df.empty: return []

    results_df = df.copy()

    if ref_date and statuses:
        results_df['status'] = results_df.apply(lambda row: get_poster_status(row.get('start_date_str'), row.get('end_date_str'), ref_date), axis=1)
        results_df = results_df[results_df['status'].isin(statuses)]
    if categories:
        pattern = '|'.join([cat.lower() for cat in categories])
        results_df = results_df[results_df['tags'].str.contains(pattern, na=False)]
    if tag:
        results_df = results_df[results_df['tags'].str.contains(tag.lower(), na=False)]
    if keyword and not results_df.empty and vectorizer is not None:
        query_vec = vectorizer.transform([keyword])
        sim_scores = cosine_similarity(query_vec, matrix[results_df.index]).flatten()
        results_df['relevance'] = sim_scores
        results_df = results_df[results_df['relevance'] > 0.01].sort_values(by='relevance', ascending=False)
    if sort_by.startswith('Title'):
        results_df = results_df.sort_values(by='제목', ascending=True)
    elif 'relevance' not in results_df.columns:
        results_df = results_df.sort_values(by='등록일', ascending=False)
    if 'status' not in results_df.columns:
        ref_date_today = date.today()
        results_df['status'] = results_df.apply(lambda row: get_poster_status(row.get('start_date_str'), row.get('end_date_str'), ref_date_today), axis=1)
    return [tuple(row) for row in results_df[['pid', '제목', '설명', 'tags', 'image_path', '등록일', 'folder_name', 'status']].to_records(index=False)]

def get_one_poster(pid: str):
    model_data = get_recommendation_model()
    if model_data is None or model_data[0] is None:
        return None
        
    df, _, _, _ = model_data
    if df.empty or pid is None: return None
    poster_series = df[df['pid'] == str(pid)]
    return poster_series.iloc[0] if not poster_series.empty else None

def add_poster_files(form_data: dict, image_bytes: bytes, image_suffix: str):
    category = form_data.get('카테고리', '기타')
    folder_without_suffix = os.path.join(DATA_DIR, category)
    folder_with_suffix = os.path.join(DATA_DIR, f"{category}_json")
    target_folder = ""
    if os.path.isdir(folder_without_suffix): target_folder = folder_without_suffix
    elif os.path.isdir(folder_with_suffix): target_folder = folder_with_suffix
    else: target_folder = folder_without_suffix
    os.makedirs(target_folder, exist_ok=True)
    base_name = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"
    image_filename = f"{base_name}{image_suffix}"
    with open(os.path.join(target_folder, image_filename), "wb") as f: f.write(image_bytes)
    json_filename = f"{base_name}_{category}.json"
    with open(os.path.join(target_folder, json_filename), "w", encoding="utf-8") as f: json.dump(form_data, f, ensure_ascii=False, indent=2)
    st.cache_data.clear()
    return os.path.splitext(json_filename)[0]

def delete_poster_files(pid: str):
    files_to_delete = glob.glob(os.path.join(DATA_DIR, '**', f'{pid}*'), recursive=True)
    if not files_to_delete: raise FileNotFoundError(f"PID '{pid}'를 가진 포스터 파일을 찾을 수 없습니다.")
    for file in files_to_delete:
        try: os.remove(file)
        except Exception as e: print(f"파일 삭제 실패 {file}: {e}")
    st.cache_data.clear()