import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")
    body = json.loads(event["body"])
    print(body)
    name = body.get("name")
    password = body.get("password")

    try:
        dynamodb = boto3.resource("dynamodb")
        user_table_name = "glen-spops-user"
        user_table = dynamodb.Table(user_table_name)
        response = user_table.scan(
            FilterExpression=Key("name").eq(name) & Key("password").eq(int(password))
        )
        user = response["Items"]
        return user
    except Exception as e:
        print(f"Error adding user: {e}")
        return e
