import streamlit as st
import pandas as pd
from datetime import datetime
from dynamo_utils import get_queue_users, get_today_matches, get_head_to_head
import altair as alt
import pytz

# 서울 시간대 설정
seoul_tz = pytz.timezone("Asia/Seoul")

# Streamlit 앱 시작
st.title("중화스쿼시 :blue[A 코트]")

# 대기열 사용자 가져오기
queue_users = get_queue_users("중화A")
st.header("현재 대기열", divider="rainbow")
if queue_users:
    total_queue = len(queue_users)
    st.metric(label="총 대기자 수", value=f"{total_queue} 명")

    # 대기열 수에 따른 알림 메시지
    if total_queue <= 4:
        st.success("운동 많이할 찬스! 얼른 오세요! 🕺")
    elif total_queue >= 8:
        st.warning("좀 많긴하네요.. 🤷")

    if total_queue % 2 != 0:
        queue_users.append("대기 중")

    matches = [queue_users[i : i + 2] for i in range(0, len(queue_users), 2)]
    for i, match in enumerate(matches):
        with st.expander(f"매치 {i + 1}", expanded=True):
            player1, player2 = match[0], match[1]
            st.write(f"{player1} vs {player2}")
            if player1 != "대기 중" and player2 != "대기 중":
                player1_wins, player2_wins = get_head_to_head(player1, player2)
                st.write(
                    f"상대 전적: {player1} {player1_wins} - {player2_wins} {player2}"
                )
else:
    st.write("비어있거나 대기열 정보를 가져올 수 없습니다.")

st.divider()
# 오늘의 경기 정보 가져오기
today_matches = get_today_matches("중화A")

# 오늘의 경기 수와 사용한 사람 수 계산
total_matches = len(today_matches)
total_players = len(
    set(match["player1_name"] for match in today_matches).union(
        set(match["player2_name"] for match in today_matches)
    )
)

# 오늘의 최다 승자 계산
winners = [match["winner"] for match in today_matches]
most_wins = pd.Series(winners).value_counts().idxmax()
most_wins_count = pd.Series(winners).value_counts().max()


# 최대 점수차 계산
def calculate_point_diff(row):
    return abs(row["player1_score"] - row["player2_score"])


today_match_df = pd.DataFrame(today_matches)
today_match_df["point_diff"] = today_match_df.apply(calculate_point_diff, axis=1)
max_point_diff_match = today_match_df.loc[today_match_df["point_diff"].idxmax()]

# 0점 맞은 사람 계산
zero_score_players = []
for index, row in today_match_df.iterrows():
    if row["player1_score"] == 0:
        zero_score_players.append(row["player1_name"])
    if row["player2_score"] == 0:
        zero_score_players.append(row["player2_name"])

# 오늘 무패 계산
player_wins = pd.Series(winners).value_counts()
player_matches = pd.Series(
    [match["player1_name"] for match in today_matches]
    + [match["player2_name"] for match in today_matches]
).value_counts()
undefeated_players = [
    player for player, wins in player_wins.items() if wins == player_matches[player]
]

# 탭 생성
tab1, tab2, tab3 = st.tabs(["🏅 오늘의 경기 정보", "📊 경기 목록", "📈 경기 수 그래프"])

with tab1:
    st.header("오늘의 :blue[경기 정보]", divider="rainbow")

    st.code("오늘도 멋진 경기가 펼쳐졌습니다!")

    col1, col2, col3 = st.columns(3)
    col1.metric("총 경기 수", f"👊 {total_matches} 경기")
    col2.metric("총 사용자 수", f"🏃‍♀️ 🏃‍♂️ {total_players} 명")
    col3.metric("최다 승자", f"🔥 {most_wins} : {most_wins_count}승")

    col4, col5, col6 = st.columns(3)
    col4.metric(
        "최대 점수차 경기",
        f"🤔 {max_point_diff_match['player1_score']} - {max_point_diff_match['player2_score']} 점",
    )
    col5.metric(
        "0점 맞은 사람",
        f"🥖 {', '.join(zero_score_players) if zero_score_players else '없음'}",
    )
    col6.metric(
        "오늘 무패",
        f"💯 {', '.join(undefeated_players) if undefeated_players else '없음'}",
    )


with tab2:
    st.header("오늘의 :blue[경기 목록]", divider="rainbow")
    st.code("다들 수고 많으셨습니다! 오늘의 경기 결과입니다. 🎉")
    # 최신 경기 정보가 가장 위에 오도록 정렬
    today_match_df = today_match_df.sort_values(by="match_date", ascending=False)
    # 매치 타입 변환
    today_match_df["match_type"] = today_match_df["match_type"].replace(
        {"normal": "일반", "deathmatch": "데스매치"}
    )

    # 승자와 패자를 구분하여 데이터 변환
    def transform_match_data(row):
        if row["player1_score"] > row["player2_score"]:
            winner = row["player1_name"]
            winner_score = row["player1_score"]
            loser = row["player2_name"]
            loser_score = row["player2_score"]
        else:
            winner = row["player2_name"]
            winner_score = row["player2_score"]
            loser = row["player1_name"]
            loser_score = row["player1_score"]
        return pd.Series(
            [
                winner,
                winner_score,
                loser_score,
                loser,
                row["match_type"],
                row["match_date"],
            ]
        )

    transformed_df = today_match_df.apply(transform_match_data, axis=1)
    transformed_df.columns = [
        "승자",
        "승자 점수",
        "패자 점수",
        "패자",
        "모드",
        "match_date",
    ]
    transformed_df = transformed_df.sort_values(by="match_date", ascending=False).drop(
        columns=["match_date"]
    )
    # 테이블 표시 (가운데 정렬)
    styled_table = transformed_df.style.hide(axis="index").set_table_styles(
        [{"selector": "td", "props": [("text-align", "center")]}]
    )
    st.table(styled_table)

with tab3:
    st.header("오늘의 :blue[경기 수 그래프]", divider="rainbow")
    st.code("어느 시간대에 경기가 가장 많았을까요? 통계를 확인해보세요! 📊")
    if not today_match_df.empty:
        # match_time을 정수형으로 변환
        today_match_df["match_time"] = today_match_df["match_time"].astype(int)
        # match_date를 datetime 형식으로 변환 후 서울 시간대로 변환
        today_match_df["match_date"] = pd.to_datetime(
            today_match_df["match_date"]
        ).dt.tz_convert(seoul_tz)
        # 시간대별 경기 수 계산
        today_match_df["hour"] = today_match_df["match_date"].dt.hour
        today_match_df["hour_label"] = today_match_df["hour"].astype(str) + "시"
        match_counts = (
            today_match_df.groupby("hour_label").size().reset_index(name="counts")
        )
        match_counts["hour"] = (
            match_counts["hour_label"].str.replace("시", "").astype(int)
        )
        # Altair를 사용한 시간대별 경기 수 시각화
        chart = (
            alt.Chart(match_counts)
            .mark_bar()
            .encode(
                x=alt.X(
                    "hour_label:O",
                    title="시간대",
                    sort=alt.SortField(field="hour", order="ascending"),
                ),
                y=alt.Y("counts:Q", title="경기 수"),
                tooltip=["hour_label", "counts"],
            )
            .properties(width=700, height=400, title="시간대 별 경기 수")
        )
        st.altair_chart(chart)
