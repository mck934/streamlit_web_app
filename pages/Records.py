import streamlit as st
import pandas as pd
import os
import json
import qrcode
from io import BytesIO
from datetime import datetime

# JSON ファイルパス
JSON_FILE = "records.json"

# 画像保存用フォルダ
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# JSON 読み込み
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
else:
    records = []

# 日付の新しい順にソート
records.sort(key=lambda x: x["date"], reverse=True)

st.title("実績一覧")

if not records:
    st.info("まだ送信内容はありません。")
else:
    for rec in records:
        id = rec.get("id")
        date = rec.get("date")
        title = rec.get("title")
        detail = rec.get("detail")
        url = rec.get("url")
        uploaded_file_path = rec.get("uploaded_file", "")

        with st.expander(f"{id}. {title}"):
            new_date = st.date_input("日付", value=datetime.strptime(date, "%Y-%m-%d").date(), key=f"date_{id}")
            new_title = st.text_input("タイトル", value=title, key=f"title_{id}")
            
            # 行数に応じて高さを調整
            height = max(100, 25 * (detail.count("\n") + 1))
            new_detail = st.text_area("詳細", value=detail, height=height, key=f"detail_{id}")
            
            new_url = st.text_input("成果物URL", value=url if url else "", key=f"url_{id}")

            # QRコード表示
            if new_url:
                qr = qrcode.QRCode(box_size=6, border=2)
                qr.add_data(new_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="成果物QRコード", width=200)

            # 画像アップロード
            uploaded_file = st.file_uploader("成果物の画像をアップロード", type=["png","jpg","jpeg"], key=f"upload_{id}")
            if uploaded_file is not None:
                st.image(uploaded_file, caption="アップロードされたプレビュー", width=300)
            
            # JSON に保存されている画像表示
            if uploaded_file_path:
                st.image(uploaded_file_path, caption="成果物画像", width=300)

            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("更新", key=f"update_{id}"):
                    new_image_path = uploaded_file_path
                    if uploaded_file is not None:
                        save_path = os.path.join(IMAGE_DIR, f"record_{id}.png")
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        new_image_path = save_path

                    # JSON 更新
                    for r in records:
                        if r["id"] == id:
                            r["date"] = new_date.strftime("%Y-%m-%d")
                            r["title"] = new_title
                            r["detail"] = new_detail
                            r["url"] = new_url
                            r["uploaded_file"] = new_image_path
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=2)
                    st.success("更新しました！")
                    st.experimental_rerun()

            with col2:
                if st.button("削除", key=f"delete_{id}"):
                    records = [r for r in records if r["id"] != id]
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=2)
                    st.warning("削除しました！")
                    st.experimental_rerun()
