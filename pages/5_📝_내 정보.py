import streamlit as st
import pandas as pd
from dynamo_utils import (
    get_user_info_from_dynamo,
    get_user_matches_from_dynamo,
    get_streaming_response,
)
from datetime import datetime
import pytz

# 서울 시간대 설정
seoul_tz = pytz.timezone("Asia/Seoul")

# Streamlit 앱 시작
st.title("내 정보 확인👤")
st.divider()

# 사용자 입력 필드
st.header("사용자 정보 입력", divider="rainbow")
name = st.text_input("이름을 입력하세요")
password = st.text_input("비밀번호 (숫자 4자리)", type="password")

# 세션 상태에 사용자 정보 확인 여부 추가
if "user_checked" not in st.session_state:
    st.session_state.user_checked = False

# 사용자 정보 가져오기
if st.button("내 정보 확인"):
    if not name or not password:
        st.error("이름과 비밀번호를 입력하세요.")
    else:
        user_info = get_user_info_from_dynamo(name, password)
        if not user_info:
            st.error("사용자 정보를 찾을 수 없습니다.")
            st.session_state.user_checked = False
        else:
            st.success("사용자 정보를 성공적으로 가져왔습니다.")
            user_matches = get_user_matches_from_dynamo(name)
            st.session_state.user_info = user_info
            st.session_state.user_matches = user_matches
            st.session_state.user_checked = True

if st.session_state.user_checked:
    tab1, tab2 = st.tabs(["📊 내 정보", "📅 경기 기록"])

    with tab1:
        st.header("내 정보", divider="rainbow")
        user_info = st.session_state.user_info

        col1, col2, col3 = st.columns(3)
        col1.metric("포인트", f"{int(user_info['point'])} 포인트")
        col2.metric("승리", f"{int(user_info['win'])} 회")
        col3.metric("패배", f"{int(user_info['lose'])} 회")

        total_matches = int(user_info["win"]) + int(user_info["lose"])
        win_rate = (
            (int(user_info["win"]) / total_matches * 100) if total_matches > 0 else 0
        )

        col4, col5, col6 = st.columns(3)
        col4.metric("승률", f"{win_rate:.2f}%")

        user_matches = st.session_state.user_matches
        if user_matches:
            match_df = pd.DataFrame(user_matches)

            # 승패여부 계산
            if not match_df.empty:
                match_df["result"] = match_df.apply(
                    lambda row: (
                        "승리"
                        if (
                            (
                                row["player1_name"] == user_info["name"]
                                and row["player1_score"] > row["player2_score"]
                            )
                            or (
                                row["player2_name"] == user_info["name"]
                                and row["player2_score"] > row["player1_score"]
                            )
                        )
                        else "패배"
                    ),
                    axis=1,
                )

                match_df["opponent"] = match_df.apply(
                    lambda row: (
                        row["player2_name"]
                        if row["player1_name"] == user_info["name"]
                        else row["player1_name"]
                    ),
                    axis=1,
                )
                win_df = match_df[match_df["result"] == "승리"]
                lose_df = match_df[match_df["result"] == "패배"]

                if not win_df.empty:
                    most_wins_against = win_df["opponent"].value_counts().idxmax()
                else:
                    most_wins_against = "없음"

                if not lose_df.empty:
                    most_losses_against = lose_df["opponent"].value_counts().idxmax()
                else:
                    most_losses_against = "없음"
            else:
                most_wins_against = "없음"
                most_losses_against = "없음"

            col5.metric("가장 많이 이긴 사람", f"🍚 {most_wins_against}")
            col6.metric("가장 많이 진 사람", f"👿 {most_losses_against}")

    with tab2:
        st.header("경기 기록", divider="rainbow")
        user_matches = st.session_state.user_matches
        if user_matches:
            match_df = pd.DataFrame(user_matches)

            if not match_df.empty:
                # 날짜 형식 변환
                match_df["match_date"] = pd.to_datetime(
                    match_df["match_date"]
                ).dt.tz_convert(seoul_tz)
                match_df["match_date"] = match_df["match_date"].dt.strftime(
                    "%m월 %d일 %H시 %M분"
                )

                # 사용자 이름 제거 및 필요한 컬럼만 선택
                match_df["상대 이름"] = match_df.apply(
                    lambda row: (
                        row["player2_name"]
                        if row["player1_name"] == user_info["name"]
                        else row["player1_name"]
                    ),
                    axis=1,
                )
                match_df["내 점수"] = match_df.apply(
                    lambda row: (
                        row["player1_score"]
                        if row["player1_name"] == user_info["name"]
                        else row["player2_score"]
                    ),
                    axis=1,
                )
                match_df["상대 점수"] = match_df.apply(
                    lambda row: (
                        row["player2_score"]
                        if row["player1_name"] == user_info["name"]
                        else row["player1_score"]
                    ),
                    axis=1,
                )
                match_df["내 점수"] = match_df["내 점수"].astype(int)
                match_df["상대 점수"] = match_df["상대 점수"].astype(int)

                # 승패여부 계산
                match_df["결과"] = match_df.apply(
                    lambda row: (
                        "승리"
                        if (
                            (
                                row["player1_name"] == user_info["name"]
                                and row["player1_score"] > row["player2_score"]
                            )
                            or (
                                row["player2_name"] == user_info["name"]
                                and row["player2_score"] > row["player1_score"]
                            )
                        )
                        else "패배"
                    ),
                    axis=1,
                )

                match_df = match_df[
                    [
                        "match_date",
                        "상대 이름",
                        "내 점수",
                        "상대 점수",
                        "결과",
                        "match_type",
                    ]
                ]

                match_df.columns = [
                    "경기 날짜",
                    "상대 이름",
                    "내 점수",
                    "상대 점수",
                    "결과",
                    "모드",
                ]

                st.table(match_df)
            else:
                st.write("경기 기록이 없습니다.")
        else:
            st.write("경기 기록이 없습니다.")

    st.header("💬 AI 경기 분석 코치", divider="rainbow")

    # 세션 상태에 메시지 없으면 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 첫 번째 메시지 추가
    if not st.session_state.messages:
        initial_message = f"안녕하세요 {user_info['name']}님! 당신의 경기 기록에서 무엇이 알고싶으신가요? 최근 10경기 전적? 주요 활동시간? 무엇이든 물어보세요!"
        st.session_state.messages.append(
            {"role": "assistant", "content": initial_message}
        )

    # 세션 상태에 저장된 메시지 순회하며 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):  # 채팅 메시지 버블 생성
            st.markdown(message["content"])  # 메시지 내용 마크다운으로 렌더링

    # 사용자로부터 입력 받음
    if prompt := st.chat_input("Message Bedrock..."):
        # 사용자 메시지 세션 상태에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):  # 사용자 메시지 채팅 메시지 버블 생성
            st.markdown(prompt)  # 사용자 메시지 표시

        with st.chat_message("assistant"):  # 보조 메시지 채팅 메시지 버블 생성
            response = ""
            with st.spinner("생각중..."):
                for model_output in get_streaming_response(
                    prompt, user_info, user_matches
                ):
                    st.markdown(model_output)  # 모델 출력 표시
                    response = model_output

            # 보조 응답 세션 상태에 추가
            st.session_state.messages.append({"role": "assistant", "content": response})
