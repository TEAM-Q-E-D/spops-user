import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")

    body = json.loads(event["body"])
    print(body)
    place = body.get("place")
    today = body.get("today")

    try:
        dynamodb = boto3.resource("dynamodb")
        match_table_name = "glen-spops-match"
        match_table = dynamodb.Table(match_table_name)
        response = match_table.scan(
            FilterExpression=Key("place").eq(place)
            & Key("match_date").begins_with(today)
        )
        return response["Items"]
    except Exception as e:
        print(f"Error adding user: {e}")
        return e
