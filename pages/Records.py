import streamlit as st
import json
import os
import qrcode
from io import BytesIO
import pandas as pd

# JSONファイルのパス
JSON_FILE = "records.json"

# 画像保存用フォルダ（アップロード時）
IMAGE_DIR = "uploaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

st.title("実績一覧（JSON版）")

# JSONデータ読み込み
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
else:
    records = []

if not records:
    st.info("まだ送信内容はありません。")
else:
    # 日付の新しい順にソート
    records = sorted(records, key=lambda x: x.get("date", ""), reverse=True)

    for record in records:
        id = record.get("id")
        date = record.get("date", "")
        title = record.get("title", "")
        detail = record.get("detail", "")
        url = record.get("url", "")
        uploaded_file_name = record.get("uploaded_file", "")

        with st.expander(f"{id}. {title}"):
            # 編集用フォーム
            new_date = st.text_input("日付", value=date, key=f"date_{id}")
            new_title = st.text_input("タイトル", value=title, key=f"title_{id}")

            # text_areaの高さを自動調整
            height = max(100, 25 * (detail.count("\n") + 1))
            new_detail = st.text_area("詳細", value=detail, height=height, key=f"detail_{id}")

            new_url = st.text_input("成果物URL", value=url if url else "", key=f"url_{id}")

            # URLがあればQRコードを表示
            if new_url:
                qr = qrcode.QRCode(box_size=6, border=2)
                qr.add_data(new_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="成果物QRコード", width=200)

            # アップロード欄
            uploaded_file = st.file_uploader("成果物の画像をアップロード", type=["png", "jpg", "jpeg"], key=f"upload_{id}")

            # アップロード済みファイルを表示
            if uploaded_file is not None:
                # ファイルを保存
                save_path = os.path.join(IMAGE_DIR, f"record_{id}_{uploaded_file.name}")
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.image(uploaded_file, caption="アップロードされたプレビュー", width=300)
                uploaded_file_name = save_path  # JSON に保存するパス更新

            # 既存の画像があれば表示
            elif uploaded_file_name and os.path.exists(uploaded_file_name):
                st.image(uploaded_file_name, caption="成果物画像", width=300)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("更新", key=f"update_{id}"):
                    # JSONデータを更新
                    record.update({
                        "date": new_date,
                        "title": new_title,
                        "detail": new_detail,
                        "url": new_url,
                        "uploaded_file": uploaded_file_name
                    })
                    # JSONファイルに書き込み
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=4)
                    st.success("更新しました！")
                    st.experimental_rerun()

            with col2:
                if st.button("削除", key=f"delete_{id}"):
                    # レコード削除
                    records.remove(record)
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=4)
                    st.warning("削除しました！")
                    st.experimental_rerun()
