import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import os
import qrcode
from io import BytesIO

# PostgreSQL 接続情報
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "portfolio_db"

# SQLAlchemy 用接続文字列
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

# 画像保存用フォルダ
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

st.title("実績一覧")

# データ取得
query = text("SELECT id, date, title, detail, url, uploaded_file FROM records ORDER BY id DESC")
with engine.connect() as conn:
    rows = conn.execute(query).fetchall()

if not rows:
    st.info("まだ送信内容はありません。")
else:
    for row in rows:
        id, date, title, detail, url, uploaded_file_path = row
        
        with st.expander(f"{id}. {title}"):
            # 編集用フォーム
            new_date = st.date_input("日付", value=date, key=f"date_{id}")
            new_title = st.text_input("タイトル", value=title, key=f"title_{id}")
            # new_detail = st.text_area("詳細", value=detail, key=f"detail_{id}")
            # データベースから取得した値を初期値として保持
            initial_detail = detail  # 既存の内容

            # 行数に応じて高さを計算
            height = max(100, 25 * (initial_detail.count("\n") + 1))

            # text_area に初期値と高さを渡す
            new_detail = st.text_area("詳細", value=initial_detail, height=height, key=f"detail_{id}")  # ← idを使ってユニークにする)
            
            new_url = st.text_input("成果物URL", value=url if url else "", key=f"url_{id}")
            
            # ▼ 成果物URLがある場合はQRコードを表示
            if new_url:
                qr = qrcode.QRCode(box_size=6, border=2)
                qr.add_data(new_url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
            
                # Streamlitに表示するためバイナリに変換
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="成果物QRコード", width=200)
            
            # アップロード欄を追加
            uploaded_file = st.file_uploader("成果物の画像をアップロード", type=["png", "jpg", "jpeg"], key=f"upload_{id}")
            
            # アップロード画像をプレビュー
            if uploaded_file is not None:
                st.image(uploaded_file, caption="アップロードされたプレビュー", width=300)
            
            # DBに保存した画像パスを表示
            if uploaded_file_path:
                st.image(uploaded_file_path, caption="成果物画像", width=300)
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("更新", key=f"update_{id}"):
                    # もし新しい画像をアップロードした場合、保存して image_path を更新
                    new_image_path = uploaded_file_path
                    if uploaded_file is not None:
                        save_path = os.path.join(IMAGE_DIR, f"record_{id}.png")
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        new_image_path = save_path
                    
                    update_query = text("""
                        UPDATE records
                        SET date = :date, title = :title, detail = :detail, url = :url, uploaded_file = :image_path
                        WHERE id = :id
                    """)
                    # トランザクション開始
                    with engine.begin() as conn:
                        conn.execute(update_query, {
                            "date": new_date,
                            "title": new_title,
                            "detail": new_detail,
                            "url": new_url,
                            "image_path": new_image_path,
                            "id": id
                        })
                    st.success("更新しました！")
                    st.rerun()  # 更新後に画面をリロード

            with col2:
                if st.button("削除", key=f"delete_{id}"):
                    delete_query = text("DELETE FROM records WHERE id = :id")
                    with engine.begin() as conn:
                        conn.execute(delete_query, {"id": id})
                    st.warning("削除しました！")
                    st.rerun()