import streamlit as st
from PIL import Image
import datetime
import qrcode
from io import BytesIO
from sqlalchemy import create_engine, text
import pandas as pd

# DB接続情報
DB_USER = "postgres"             # PostgreSQL ユーザー名
DB_PASSWORD = "postgres"     # パスワード
DB_HOST = "localhost"            # ローカルなら localhost
DB_PORT = "5432"
DB_NAME = "portfolio_db"

# SQLAlchemy用の接続文字列
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エンジン作成
engine = create_engine(DATABASE_URL, echo=True)

st.title('ポートフォリオ')
st.caption('Webアプリ開発などを学習中')
st.subheader('自己紹介')
# 画像
image = Image.open('./faceImage.jpg')
st.image(image, width=150)
st.text('はじめまして。眞田開人と申します。私は職業訓練において、Javaを中心としたシステム開発を学びました。Java言語の基本から、JavaScriptを用いたフロントエンド開発、Servlet・JSPによるWebアプリケーション構築、データベースとの連携、さらにSpringフレームワークを活用した業務アプリケーション開発演習を通して、システム開発のプロセスと実践的な技術を習得しました。'
        'これまでの学習を活かし、JavaシステムエンジニアやJavaプログラマーとして、チームに貢献しながら実務経験を積み、着実に成長していきたいと考えております。'
        # '私は職業訓練において、Javaを中心としたシステム開発を学びました。\n'
        # '関心があることの情報発信もしていく予定です、よろしくお願いします!\n'
        # 'Java言語の基本から、JavaScriptを用いたフロントエンド開発、\n'
        # 'Servlet・JSPによるWebアプリケーション構築、\n'
        # 'データベースとの連携、さらにSpringフレームワークを活用した業務アプリケーション開発演習を通して、\n'
        # 'システム開発のプロセスと実践的な技術を習得しました。\n'       
        # 'これまでの学習を活かし、JavaシステムエンジニアやJavaプログラマーとして、\n'
        # 'チームに貢献しながら実務経験を積み、着実に成長していきたいと考えております。\n'
        )
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
    st.text('以下に実績を入力します。')
    
    # 日付
    record_date = st.date_input(
        '日付',
        datetime.date.today()
    )
    
    
    # テキストボックス
    title = st.text_input('タイトル')
    
    detail = st.text_area('詳細')
    
    # 成果物URL入力欄
    url = st.text_input("成果物URL（WebページやGitHubのリンクなど）")
    
    # アップロードファイルの一時保存パス（DBに保存するのはこの文字列）
    uploaded_path = None
    
    # 画像アップロード
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=["png", "jpg", "jpeg", "gif", "webp"])
    
    if uploaded_file is not None:
        # バイトデータに変換して表示
        bytes_data = uploaded_file.getvalue()
        # アップロードしたファイルをそのまま表示
        st.image(bytes_data, caption="アップロードした画像", width=300)

        # query = text("""
        #     INSERT INTO records (uploaded_file)
        #     VALUES (:uploaded_file)
        # """)

        # with engine.connect() as conn:
        #     conn.execute(query, {
        #         "uploaded_file": uploaded_file
        #     })
        #     conn.commit()  # COMMITを忘れずに

        # ローカル保存してパスを記録
        uploaded_path = f"uploaded_{uploaded_file.name}"
        with open(uploaded_path, "wb") as f:
            f.write(bytes_data)
    
    if url:
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="QRコードをスキャンしてダウンロード")
        
    # セレクトボックス
    # age_category = st.radio(
    #     '年齢層',
    #     ('子ども(18才未満)', '大人(18才以上)'))

    # 複数選択
    # hobby = st.multiselect(
    #     '趣味',
    #     ('スポーツ', '読書', 'プログラミング', 'アニメ・映画', '釣り', '料理'))

    # チェックボックス
    # mail_subscribe = st.checkbox('メールマガジンを購読する')
    
    # スライダー
    # height = st.slider('身長', min_value=110, max_value=210)

    
    # カラーピッカー
    color = st.color_picker('テーマカラー', '#00f900')

    # ボタン
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル') 
    if submit_btn:
        # INSERT 文で records テーブルに保存
        query = text("""
            INSERT INTO records (date, title, detail, url, uploaded_file)
            VALUES (:date, :title, :detail, :url, :uploaded_file)
        """)
        
        # uploaded_path が None の場合は空文字に
        file_path = uploaded_path if uploaded_path else ""
        
        with engine.begin() as conn:
            conn.execute(query, {
                "date": str(record_date), 
                "title": title, 
                "detail": detail, 
                "url": url, 
                "uploaded_file": uploaded_path
            })
        st.success("送信しました！")
        
        # ✅ Records ページに移動
        st.switch_page("pages/Records.py")
    #     st.text(f'年齢層：{age_category}')
    #     st.text(f'趣味：{", ".join(hobby)}')