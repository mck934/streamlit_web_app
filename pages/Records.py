import streamlit as st
import json
import os
import qrcode
from io import BytesIO
from datetime import datetime
from PIL import Image
import pandas as pd

# JSONファイルと画像フォルダ
JSON_FILE = "records.json"
IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

st.title("実績一覧")

# JSONデータ読み込み
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
else:
    records = []

if not records:
    st.info("まだ送信内容はありません。")
else:
    # 日付で降順ソート
    def parse_date(rec):
        try:
            return datetime.strptime(rec["date"], "%Y-%m-%d")
        except:
            return datetime.min

    records.sort(key=parse_date, reverse=True)

    for rec in records:
        id = rec.get("id")
        date = rec.get("date", "")
        title = rec.get("title", "")
        detail = rec.get("detail", "")
        url = rec.get("url", "")
        uploaded_file_path = rec.get("uploaded_file", "")

        with st.expander(f"{id}. {title}"):
            # 編集フォーム
            new_date = st.date_input("日付", value=datetime.strptime(date, "%Y-%m-%d"), key=f"date_{id}")
            new_title = st.text_input("タイトル", value=title, key=f"title_{id}")

            # 行数に応じて高さを計算
            height = max(100, 25 * (detail.count("\n") + 1))
            new_detail = st.text_area("詳細", value=detail, height=height, key=f"detail_{id}")

            new_url = st.text_input("成果物URL", value=url, key=f"url_{id}")

            # URLがあればQRコード表示
            if new_url:
                qr = qrcode.QRCode(box_size=6, border=2)
                qr.add_data(new_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf.getvalue(), caption="成果物QRコード", width=200)

            # アップロード欄
            uploaded_file = st.file_uploader("成果物の画像をアップロード", type=["png","jpg","jpeg"], key=f"upload_{id}")

            # JSONに保存された画像を表示
            if uploaded_file_path:
                if os.path.exists(uploaded_file_path):
                    try:
                        img = Image.open(uploaded_file_path)
                        st.image(img, caption="成果物画像", width=300)
                    except:
                        st.warning(f"画像の読み込みに失敗しました: {uploaded_file_path}")
                else:
                    st.warning(f"画像ファイルが見つかりません: {uploaded_file_path}")

            # アップロードされた新規画像プレビュー
            if uploaded_file:
                st.image(uploaded_file, caption="アップロードされたプレビュー", width=300)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("更新", key=f"update_{id}"):
                    # アップロード画像があれば保存
                    new_image_path = uploaded_file_path
                    if uploaded_file:
                        save_path = os.path.join(IMAGE_DIR, f"record_{id}.png")
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        new_image_path = save_path

                    # JSONデータを更新
                    for r in records:
                        if r["id"] == id:
                            r["date"] = new_date.strftime("%Y-%m-%d")
                            r["title"] = new_title
                            r["detail"] = new_detail
                            r["url"] = new_url
                            r["uploaded_file"] = new_image_path
                            break

                    # JSONに保存
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=4)
                    st.success("更新しました！")
                    st.experimental_rerun()

            with col2:
                if st.button("削除", key=f"delete_{id}"):
                    # JSONデータから削除
                    records = [r for r in records if r["id"] != id]
                    with open(JSON_FILE, "w", encoding="utf-8") as f:
                        json.dump(records, f, ensure_ascii=False, indent=4)
                    st.warning("削除しました！")
                    st.experimental_rerun()
