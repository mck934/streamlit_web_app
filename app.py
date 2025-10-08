import streamlit as st
import json
import pandas as pd

# JSON を読み込む
with open("records.json", "r", encoding="utf-8") as f:
    records = json.load(f)

# DataFrame に変換
df = pd.DataFrame(records)

# 表示
st.dataframe(df)
