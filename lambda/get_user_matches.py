import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal


# 헬퍼 함수: Decimal 객체를 직렬화 가능한 타입으로 변환
# decimal_default 헬퍼 함수 추가:
# 이 함수는 decimal.Decimal 객체를 float로 변환합니다.
# json.dumps 함수 호출 시 default 인자를 추가하여 decimal_default 함수를 사용하도록 설정:
# 이로 인해 decimal.Decimal 객체가 JSON으로 직렬화될 때 float로 변환됩니다.
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    print("넘어오는거 확인")

    body = json.loads(event["body"])
    print(body)
    name = body.get("name")

    try:
        dynamodb = boto3.resource("dynamodb")
        match_table_name = "glen-spops-match"
        match_table = dynamodb.Table(match_table_name)

        # player1_name으로 쿼리
        response_player1 = match_table.query(
            IndexName="player1_name-index",  # 인덱스 이름 사용
            KeyConditionExpression=Key("player1_name").eq(name),
        )

        # player2_name으로 쿼리
        response_player2 = match_table.query(
            IndexName="player2_name-index",  # 인덱스 이름 사용
            KeyConditionExpression=Key("player2_name").eq(name),
        )

        # 두 쿼리 결과 합치기
        items = response_player1["Items"] + response_player2["Items"]
        print(items)

        return {"statusCode": 200, "body": json.dumps(items, default=decimal_default)}

    except Exception as e:
        print(f"Error fetching matches: {e}")
        return {"statusCode": 500, "body": json.dumps(str(e))}
