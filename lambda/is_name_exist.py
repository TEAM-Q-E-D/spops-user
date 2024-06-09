import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("넘어오는거 확인")
    body = json.loads(event["body"])
    name = body.get("name")
    print(name)

    dynamodb = boto3.resource("dynamodb")
    user_table_name = "glen-spops-user"
    user_table = dynamodb.Table(user_table_name)
    response = user_table.scan(FilterExpression=Key("name").eq(name))
    items = response["Items"]
    result = len(items) > 0
    print(f"결과 {result}")

    return {"statusCode": 200, "body": json.dumps({"is_name_exist": result})}
