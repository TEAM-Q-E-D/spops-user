import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("glen-spops-user")


def update_daily_limit():
    try:
        response = table.scan()
        items = response.get("Items", [])

        for item in items:
            user_id = item["user_id"]
            user_type = item.get("type", None)

            if user_type == 1:
                new_daily_limit = 3
            elif user_type == 2:
                new_daily_limit = 3
            elif user_type == 0:
                new_daily_limit = 3
            else:
                continue

            table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET daily_limit = :val",
                ExpressionAttributeValues={":val": new_daily_limit},
            )
    except ClientError as e:
        print(f"Error updating items: {e.response['Error']['Message']}")


def lambda_handler(event, context):
    update_daily_limit()
    return {"statusCode": 200, "body": "Daily limits updated successfully"}
