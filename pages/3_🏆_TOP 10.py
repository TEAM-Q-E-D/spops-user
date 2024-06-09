import streamlit as st
import pandas as pd
from dynamo_utils import get_top_users

# Streamlit 앱 시작
st.title("포인트 상위 :blue[20위] 🏆")

# 포인트 상위 20위 사용자 가져오기
top_users = get_top_users()

# 필요한 컬럼만 선택하고 점수 컬럼을 정수형으로 변환
top_users_df = pd.DataFrame(top_users)[["name", "point", "win", "lose"]]
top_users_df["point"] = top_users_df["point"].astype(int)
top_users_df["win"] = top_users_df["win"].astype(int)
top_users_df["lose"] = top_users_df["lose"].astype(int)

# 승률 계산
top_users_df["승률"] = top_users_df.apply(
    lambda row: (
        int((row["win"] / (row["win"] + row["lose"])) * 100)
        if (row["win"] + row["lose"]) > 0
        else 0
    ),
    axis=1,
)
top_users_df["승률"] = top_users_df["승률"].astype(str) + "%"

# 1, 2, 3위 사용자 분리
top_3_users = top_users_df.iloc[:3]
other_users = top_users_df.iloc[3:]

# 1, 2, 3위 사용자 정보 표시
st.header("1위 / 2위 / 3위", divider="rainbow")
col1, col2, col3 = st.columns(3)
col1.metric(
    label="1위",
    value=top_3_users.iloc[0]["name"],
    delta=f'{top_3_users.iloc[0]["point"]} 점, {top_3_users.iloc[0]["승률"]} 승률',
)
col2.metric(
    label="2위",
    value=top_3_users.iloc[1]["name"],
    delta=f'{top_3_users.iloc[1]["point"]} 점, {top_3_users.iloc[1]["승률"]} 승률',
)
col3.metric(
    label="3위",
    value=top_3_users.iloc[2]["name"],
    delta=f'{top_3_users.iloc[2]["point"]} 점, {top_3_users.iloc[2]["승률"]} 승률',
)

st.divider()

# 순위 컬럼 추가
other_users.insert(0, "순위", range(4, 4 + len(other_users)))

# 테이블 표시 (가운데 정렬 및 인덱스 숨기기)
st.subheader("포인트 상위 4-20위", divider="rainbow")
styled_table = other_users.style.set_table_styles(
    [{"selector": "th, td", "props": [("text-align", "center")]}]
).hide(axis="index")

st.table(styled_table)
