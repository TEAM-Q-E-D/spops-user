import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")

    body = json.loads(event["body"])
    print(body)
    player1 = body.get("player1")
    player2 = body.get("player2")

    try:
        dynamodb = boto3.resource("dynamodb")
        match_table_name = "glen-spops-match"
        match_table = dynamodb.Table(match_table_name)
        response = match_table.scan(
            FilterExpression=(
                Key("player1_name").eq(player1) & Key("player2_name").eq(player2)
            )
            | (Key("player1_name").eq(player2) & Key("player2_name").eq(player1))
        )
        return response["Items"]
    except Exception as e:
        print(f"Error adding user: {e}")
        return e
