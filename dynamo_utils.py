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

# AWS 자격 증명 환경 변수 설정
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region = os.getenv("AWS_REGION")
user_table_name = os.getenv("USER_TABLE")
match_table_name = os.getenv("MATCH_TABLE")
lambda_url = os.getenv("LAMBDA_URL")

# DynamoDB 연결 설정
dynamodb = boto3.resource(
    "dynamodb",
    region_name=region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)
user_table = dynamodb.Table(user_table_name)
match_table = dynamodb.Table(match_table_name)


# 현재 최대 user_id 가져오기
def get_max_user_id():
    response = user_table.scan()
    items = response["Items"]
    if not items:
        return 0
    max_user_id = max(int(item["user_id"]) for item in items)
    return max_user_id


# 사용자 이름 중복 여부 확인 함수
def is_name_exist(name):
    response = user_table.scan(FilterExpression=Key("name").eq(name))
    items = response["Items"]
    return len(items) > 0


# 사용자 추가 함수
def add_user(name, password):
    try:
        max_user_id = get_max_user_id()
        new_user_id = max_user_id + 1
        user_table.put_item(
            Item={
                "user_id": new_user_id,  # 숫자 타입으로 설정
                "name": name,
                "password": int(password),  # 숫자 타입으로 설정
                "win": 0,  # 숫자 타입으로 설정
                "lose": 0,  # 숫자 타입으로 설정
                "point": 0,  # 숫자 타입으로 설정
                "daily_limit": 3,  # 숫자 타입으로 설정
                "rank": "비기너",
                "type": 1,
            }
        )
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False


# 오늘의 경기 정보 가져오기
def get_today_matches(place):
    today = datetime.now(pytz.timezone("Asia/Seoul")).date().isoformat()
    response = match_table.scan(
        FilterExpression=Key("place").eq(place) & Key("match_date").begins_with(today)
    )
    return response["Items"]


# 포인트 상위 10위 사용자 가져오기
def get_top_users():
    response = user_table.scan()
    users = response["Items"]
    top_users = sorted(users, key=lambda x: x["point"], reverse=True)[:10]
    return top_users


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
    response = match_table.scan(
        FilterExpression=(
            Key("player1_name").eq(player1) & Key("player2_name").eq(player2)
        )
        | (Key("player1_name").eq(player2) & Key("player2_name").eq(player1))
    )
    matches = response["Items"]
    player1_wins = sum(1 for match in matches if match["winner"] == player1)
    player2_wins = sum(1 for match in matches if match["winner"] == player2)
    return player1_wins, player2_wins


# 사용자 정보 가져오기 함수
def get_user_info_from_dynamo(name, password):
    response = user_table.scan(
        FilterExpression=Key("name").eq(name) & Key("password").eq(int(password))
    )
    items = response["Items"]
    return items[0] if items else None


# 사용자 경기 기록 가져오기 함수
def get_user_matches_from_dynamo(name):
    response = match_table.scan(
        FilterExpression=Key("player1_name").eq(name) | Key("player2_name").eq(name)
    )
    items = response["Items"]
    return items


def get_streaming_response(prompt, user_info, user_matches):
    s = requests.Session()
    print("넘어오는 내용확인")
    print(prompt)

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

    response = s.post(lambda_url, json={"prompt": prompt_with_data}, stream=True)

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
