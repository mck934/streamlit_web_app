import streamlit as st
import datetime
import qrcode
from io import BytesIO
from PIL import Image
import json
import os

# JSON ファイル名
JSON_FILE = "records.json"

# JSON ファイル読み込み（なければ空リスト作成）
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
else:
    records = []

st.title("ポートフォリオ")

st.caption('Webアプリ開発などを学習中')
st.subheader('自己紹介')
# 画像
image = Image.open('./faceImage.jpg')
st.image(image, width=150)
st.text('はじめまして。眞田開人と申します。私は職業訓練において、Javaを中心としたシステム開発を学びました。Java言語の基本から、JavaScriptを用いたフロントエンド開発、Servlet・JSPによるWebアプリケーション構築、データベースとの連携、さらにSpringフレームワークを活用した業務アプリケーション開発演習を通して、システム開発のプロセスと実践的な技術を習得しました。'
        'これまでの学習を活かし、JavaシステムエンジニアやJavaプログラマーとして、チームに貢献しながら実務経験を積み、着実に成長していきたいと考えております。')

st.markdown("""
        ### 自己紹介  
        はじめまして。**眞田開人**と申します。  
        
        職業訓練で以下のことを勉強しました。
        - **Javaを中心としたシステム開発** を学習  
        - JavaScript を用いたフロントエンド開発  
        - Servlet・JSP を用いた Web アプリ構築  
        - データベース連携や **Spring フレームワーク** を利用した業務アプリ開発演習  

        これまでの学習を活かし、**Javaシステムエンジニア／プログラマー** として成長していきたいと考えております。
""")

with st.form(key='profile_form'):
    st.markdown("#### 実績入力")
    
    record_date = st.date_input('日付', datetime.date.today())
    title = st.text_input('タイトル')
    detail = st.text_area('詳細')
    url = st.text_input('成果物URL')
    
    uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "gif", "webp"])
    
    uploaded_path = ""
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        uploaded_path = f"uploaded_{uploaded_file.name}"
        with open(uploaded_path, "wb") as f:
            f.write(bytes_data)
        st.image(bytes_data, caption="アップロード画像", width=300)
    
    if url:
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="QRコード")
    
    submit_btn = st.form_submit_button("送信")
    if submit_btn:
        # 辞書として保存
        new_record = {
            "date": str(record_date),
            "title": title,
            "detail": detail,
            "url": url,
            "uploaded_file": uploaded_path
        }
        records.append(new_record)
        
        # JSON に保存
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        st.success("送信しました！")
