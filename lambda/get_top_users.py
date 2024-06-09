import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")

    try:
        dynamodb = boto3.resource("dynamodb")
        user_table_name = "glen-spops-user"
        user_table = dynamodb.Table(user_table_name)
        response = user_table.scan()
        users = response["Items"]
        top_users = sorted(users, key=lambda x: x["point"], reverse=True)[:10]
        return top_users
    except Exception as e:
        print(f"Error adding user: {e}")
        return e
