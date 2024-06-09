import json
import boto3


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    user_table_name = "glen-spops-user"
    user_table = dynamodb.Table(user_table_name)

    response = user_table.scan()
    items = response["Items"]

    max_user_id = max(int(item["user_id"]) for item in items) if items else 0

    return {"statusCode": 200, "body": json.dumps({"max_user_id": max_user_id})}
