import pytz
import pandas as pd
import os
import json
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from datetime import datetime
import requests
import pytz

seoul_tz = pytz.timezone("Asia/Seoul")

# .env 파일 로드
load_dotenv()

user_table_name = os.getenv("USER_TABLE")
match_table_name = os.getenv("MATCH_TABLE")
bedrock_lambda_url = os.getenv("BEDROCK_LAMBDA_URL")
dynamo_lambda_url = os.getenv("DYNAMO_LAMBDA_URL")
max_user_id = os.getenv("GET_MAX_USER_ID")
name_check = os.getenv("IS_NAME_EXIST")
create_user = os.getenv("ADD_USER")
today_match = os.getenv("TODAY_MATCH")
top_users = os.getenv("TOP_USERS")
head_to_head = os.getenv("HEAD_TO_HEAD")
user_info = os.getenv("USER_INFO")
user_matches = os.getenv("USER_MATCHES")


# 현재 최대 user_id 가져오기
def get_max_user_id():
    response = requests.get(max_user_id)
    return response.json()["max_user_id"]  # Number


# 사용자 이름 중복 여부 확인 함수
def is_name_exist(name):
    response = requests.post(name_check, json={"name": name})
    return response.json()["is_name_exist"]  # True or False


# 사용자 추가 함수
def add_user(name, password):
    max_user_id = get_max_user_id()
    response = requests.post(
        create_user,
        json={"max_user_id": max_user_id, "name": name, "password": password},
    )
    return response.json()  # True or False


# 오늘의 경기 정보 가져오기
def get_today_matches(place):
    today = datetime.now(pytz.timezone("Asia/Seoul")).date().isoformat()
    response = requests.post(today_match, json={"today": today, "place": place})
    return response.json()  # 리스트에 들어가 있는 객체 형태의 매치 정보


# 포인트 상위 10위 사용자 가져오기
def get_top_users():
    response = requests.get(top_users)
    return response.json()  # 객체 안에 있는 유저 정보


# 대기열 사용자 가져오기
def get_queue_users(place):
    try:
        response = requests.get(f"{os.getenv('SERVER_URL')}/players?place={place}")
        response.raise_for_status()  # HTTPError가 발생할 경우 예외가 던져짐
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching queue users: {e}")
        return []


# 상대 전적 가져오기
def get_head_to_head(player1, player2):
    response = requests.post(
        head_to_head, json={"player1": player1, "player2": player2}
    )
    matches = response.json()
    player1_wins = sum(1 for match in matches if match["winner"] == player1)
    player2_wins = sum(1 for match in matches if match["winner"] == player2)
    return player1_wins, player2_wins


# 사용자 정보 가져오기 함수
def get_user_info_from_dynamo(name, password):
    response = requests.post(user_info, json={"name": name, "password": password})
    items = response.json()
    return items[0] if items else None


# 사용자 경기 기록 가져오기 함수
def get_user_matches_from_dynamo(name):
    response = requests.post(user_matches, json={"name": name})
    items = response.json()
    return items


def get_streaming_response(prompt, user_info, user_matches):
    s = requests.Session()

    # user_info와 user_matches 데이터를 텍스트로 변환
    user_info_text = f"User Info: 이름: {user_info['name']}, 포인트: {user_info['point']}, 승리: {user_info['win']}, 패배: {user_info['lose']}, 랭크: {user_info['rank']}"
    user_matches_text = "User Matches:\n"
    for match in user_matches:
        match_date = (
            pd.to_datetime(match["match_date"])
            .tz_convert(seoul_tz)
            .strftime("%m월 %d일 %H시 %M분")
        )
        user_matches_text += f"{match_date} - {match['player1_name']} {match['player1_score']} vs {match['player2_score']} {match['player2_name']} ({match['match_type']})\n"

    # 모든 데이터를 하나의 문자열로 합침
    prompt_with_data = f"{user_info_text}\n{user_matches_text}\nPrompt: {prompt}"

    response = s.post(
        bedrock_lambda_url, json={"prompt": prompt_with_data}, stream=True
    )

    output = ""
    for chunk in response.iter_lines():
        if chunk:
            text = chunk.decode()  # 바이트코드인 chunk를 decode
            print(text)
            try:
                # JSON 파싱 시도
                data = json.loads(text)
                output += data.get("output", "")  # output 키의 값을 추가
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원래 텍스트 추가
                output += text
            yield output
