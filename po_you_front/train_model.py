# train_model.py
import os, re, json, glob, joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

# --- ipynb 파일의 핵심 함수들을 그대로 가져옵니다 ---
def safe_join(v):
    if v is None: return ""
    if isinstance(v, str): return v
    if isinstance(v, (int, float, bool)): return str(v)
    if isinstance(v, list): return " ".join(safe_join(x) for x in v)
    if isinstance(v, dict): return " ".join(safe_join(x) for x in v.values())
    return str(v)

def extract_text(rec):
    parts = []
    for key in ["제목", "설명", "세부카테고리", "주최기관", "대상", "기간"]:
        if key in rec: parts.append(safe_join(rec[key]))
    return re.sub(r"\\s+", " ", " ".join(parts)).strip()

def collect_dataset(data_dir):
    rows = []
    LABELS = ["기타", "대회", "모집", "자금", "진로", "행사"]
    files = glob.glob(os.path.join(data_dir, '**', '*.json'), recursive=True) + \
            glob.glob(os.path.join(data_dir, '**', '*.txt'), recursive=True)
            
    for path in files:
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                rec = json.load(f)
            text = extract_text(rec)
            label = rec.get("카테고리", None)
            if text and label in LABELS:
                rows.append({"text": text, "label": label})
        except Exception:
            pass
    return pd.DataFrame(rows)

def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_df=0.95)),
        ("clf", LinearSVC(class_weight="balanced", C=0.5, random_state=42))
    ])

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    DATA_DIR = "json"
    MODEL_OUT = "category_classifier.pkl"
    
    print(f"'{DATA_DIR}' 폴더에서 데이터 수집을 시작합니다...")
    df = collect_dataset(DATA_DIR)
    
    if df.empty:
        print("학습할 데이터가 없습니다. json 폴더에 데이터가 있는지 확인해주세요.")
    else:
        print(f"총 {len(df)}개의 포스터 데이터를 수집했습니다.")
        print("카테고리별 데이터 개수:")
        print(df['label'].value_counts())
        
        X, y = df["text"].values, df["label"].values
        
        print("\n카테고리 분류 모델 학습을 시작합니다...")
        pipeline = build_pipeline()
        pipeline.fit(X, y)
        
        joblib.dump(pipeline, MODEL_OUT)
        print(f"✅ 모델 학습 완료! '{MODEL_OUT}' 파일로 저장되었습니다.")