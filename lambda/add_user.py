import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")
    body = json.loads(event["body"])
    name = body.get("name")
    password = body.get("password")
    max_user_id = body.get("max_user_id")
    print(body)
    try:
        dynamodb = boto3.resource("dynamodb")
        user_table_name = "glen-spops-user"
        user_table = dynamodb.Table(user_table_name)

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
                "death_match_limit": 2,
                "rank": "비기너",
                "type": 1,
            }
        )
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
