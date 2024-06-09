import requests
import os
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

lambda_url = os.getenv("BEDROCK_LAMBDA_URL")


def lambda_request(action, payload={}):
    payload["action"] = action
    response = requests.post(lambda_url, json=payload)
    response.raise_for_status()
    return response.json()


def get_max_user_id():
    return lambda_request("get_max_user_id")


def is_name_exist(name):
    return lambda_request("is_name_exist", {"name": name})


def add_user(name, password):
    return lambda_request("add_user", {"name": name, "password": password})


def get_today_matches(place):
    return lambda_request("get_today_matches", {"place": place})


def get_top_users():
    return lambda_request("get_top_users")


def get_head_to_head(player1, player2):
    return lambda_request("get_head_to_head", {"player1": player1, "player2": player2})


def get_user_info_from_dynamo(name, password):
    return lambda_request(
        "get_user_info_from_dynamo", {"name": name, "password": password}
    )


def get_user_matches_from_dynamo(name):
    return lambda_request("get_user_matches_from_dynamo", {"name": name})
