import boto3
import json


def lambda_handler(event, context):
    try:
        # 세션 토큰 생성
        sts_client = boto3.client("sts")
        session_token = sts_client.get_session_token()["Credentials"]

        region = "us-east-1"  # 혹은 다른 지역으로 설정

        dynamodb = boto3.resource(
            "dynamodb",
            region_name=region,
            aws_access_key_id=session_token["AccessKeyId"],
            aws_secret_access_key=session_token["SecretAccessKey"],
            aws_session_token=session_token["SessionToken"],
        )

        # 테이블 이름을 전달받아 DynamoDB 테이블 리소스를 생성
        table_name = event["table_name"]
        table = dynamodb.Table(table_name)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "access_key": session_token["AccessKeyId"],
                    "secret_key": session_token["SecretAccessKey"],
                    "session_token": session_token["SessionToken"],
                    "table_arn": table.table_arn,
                }
            ),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
