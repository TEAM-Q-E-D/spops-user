import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import pytz

seoul_tz = pytz.timezone("Asia/Seoul")


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    user_table = dynamodb.Table("glen-spops-user")
    match_table = dynamodb.Table("glen-spops-match")

    action = event.get("action")

    if action == "get_max_user_id":
        response = user_table.scan()
        items = response["Items"]
        max_user_id = max(int(item["user_id"]) for item in items) if items else 0
        return {"statusCode": 200, "body": json.dumps(max_user_id)}

    elif action == "is_name_exist":
        name = event.get("name")
        response = user_table.scan(FilterExpression=Key("name").eq(name))
        items = response["Items"]
        return {"statusCode": 200, "body": json.dumps(len(items) > 0)}

    elif action == "add_user":
        name = event.get("name")
        password = event.get("password")
        response = user_table.scan()
        items = response["Items"]
        max_user_id = max(int(item["user_id"]) for item in items) if items else 0
        new_user_id = max_user_id + 1
        user_table.put_item(
            Item={
                "user_id": new_user_id,
                "name": name,
                "password": int(password),
                "win": 0,
                "lose": 0,
                "point": 0,
                "daily_limit": 3,
                "rank": "비기너",
                "type": 1,
            }
        )
        return {"statusCode": 200, "body": json.dumps(True)}

    elif action == "get_today_matches":
        place = event.get("place")
        today = datetime.now(seoul_tz).date().isoformat()
        response = match_table.scan(
            FilterExpression=Key("place").eq(place)
            & Key("match_date").begins_with(today)
        )
        return {"statusCode": 200, "body": json.dumps(response["Items"])}

    elif action == "get_top_users":
        response = user_table.scan()
        users = response["Items"]
        top_users = sorted(users, key=lambda x: x["point"], reverse=True)[:10]
        return {"statusCode": 200, "body": json.dumps(top_users)}

    elif action == "get_head_to_head":
        player1 = event.get("player1")
        player2 = event.get("player2")
        response = match_table.scan(
            FilterExpression=(
                Key("player1_name").eq(player1) & Key("player2_name").eq(player2)
            )
            | (Key("player1_name").eq(player2) & Key("player2_name").eq(player1))
        )
        matches = response["Items"]
        player1_wins = sum(1 for match in matches if match["winner"] == player1)
        player2_wins = sum(1 for match in matches if match["winner"] == player2)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"player1_wins": player1_wins, "player2_wins": player2_wins}
            ),
        }

    elif action == "get_user_info_from_dynamo":
        name = event.get("name")
        password = event.get("password")
        response = user_table.scan(
            FilterExpression=Key("name").eq(name) & Key("password").eq(int(password))
        )
        items = response["Items"]
        return {"statusCode": 200, "body": json.dumps(items[0] if items else None)}

    elif action == "get_user_matches_from_dynamo":
        name = event.get("name")
        response = match_table.scan(
            FilterExpression=Key("player1_name").eq(name) | Key("player2_name").eq(name)
        )
        items = response["Items"]
        return {"statusCode": 200, "body": json.dumps(items)}

    else:
        return {"statusCode": 400, "body": json.dumps("Invalid action")}
