# common.py  (Python 3.9 호환 버전)
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import streamlit as st

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"
POSTER_DIR = BASE_DIR / "posters"
POSTER_DIR.mkdir(exist_ok=True)

# --- Database bootstrap ---
def _init_db(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT "",
            tags TEXT DEFAULT "",
            image_path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    _init_db(conn)
    return conn

# --- CRUD helpers ---
def add_poster(title: str, description: str, tags: str, image_bytes: bytes, image_suffix: str = ".png") -> int:
    """
    Save an uploaded poster image and metadata.
    Returns: inserted row id (int)
    """
    POSTER_DIR.mkdir(exist_ok=True)
    if not image_suffix.startswith("."):
        image_suffix = "." + image_suffix
    fname = f"{uuid.uuid4().hex}{image_suffix}"
    fpath = POSTER_DIR / fname
    with open(fpath, "wb") as f:
        f.write(image_bytes)

    created = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO posters (title, description, tags, image_path, created_at) VALUES (?,?,?,?,?)",
        (title, description, tags, str(fpath), created),
    )
    conn.commit()
    inserted_id = cur.lastrowid
    conn.close()
    return inserted_id

def get_posters(keyword: Optional[str] = None, tag: Optional[str] = None, order: str = "new"):
    """
    Fetch poster rows.
    order: "new" (created_at desc) or "title" (A-Z)
    Returns list of tuples: (id, title, description, tags, image_path, created_at)
    """
    conn = get_conn()
    base = "SELECT id, title, description, tags, image_path, created_at FROM posters"
    wh, params = [], []
    if keyword:
        wh.append("(title LIKE ? OR description LIKE ? OR tags LIKE ?)")
        like = f"%{keyword}%"
        params += [like, like, like]
    if tag:
        wh.append("tags LIKE ?")
        params.append(f"%{tag}%")
    if wh:
        base += " WHERE " + " AND ".join(wh)
    if order == "new":
        base += " ORDER BY datetime(created_at) DESC"
    else:
        base += " ORDER BY title COLLATE NOCASE ASC"
    rows = conn.execute(base, params).fetchall()
    conn.close()
    return rows

def get_one(poster_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT id, title, description, tags, image_path, created_at FROM posters WHERE id=?",
        (poster_id,),
    ).fetchone()
    conn.close()
    return row

def delete_poster(poster_id: int):
    row = get_one(poster_id)
    if not row:
        return
    _, _, _, _, image_path, _ = row
    try:
        os.remove(image_path)
    except Exception:
        pass
    conn = get_conn()
    conn.execute("DELETE FROM posters WHERE id=?", (poster_id,))
    conn.commit()
    conn.close()

# --- UI helpers ---
def app_header(title: str = "Poster Exhibition"):
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:24px; font-weight:700;">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
