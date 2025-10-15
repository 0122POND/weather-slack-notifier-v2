import json
import os
import boto3

TableName = os.environ['TableName']
dynamodb = boto3.resource("dynamodb", region_name='ap-northeast-1')


def next_id(table_name, num):

    table = dynamodb.Table("sequences")
    data = table.update_item(
        Key={
            'name': table_name
        },
        UpdateExpression='ADD current_number :incr',
        ExpressionAttributeValues={
            ':incr': num
        },
        ReturnValues="UPDATED_NEW"
    )
    return data['Attributes']['current_number']


def getItem(post_id):

    table = dynamodb.Table(TableName)

    response = table.get_item(
        Key={
            'post_id': post_id
        }
    )

    if "Item" in response:
        item = response['Item']
    else:
        # 存在しないプライマリーキーで取得する場合、メタデータが返される
        item = {}
        item['prefecture'] = None

    return item


def getLatestID():

    table = dynamodb.Table("sequences")
    response = table.get_item(
        Key={
            'name': TableName
        }
    )
    if "Item" in response:
        id = response['Item']['current_number']
    else:
        id = ''
    return id


def getPlaces(event):

    # 1) 記事IDの取得
    post_id = event['queryStringParameters']['post_id']
    print(post_id)

    # 最新の記事IDを取得
    latest_id = getLatestID()

    # 2) 記事IDの判定 + 記事の詳細を取得
    if post_id == 'first':
        new_post_id = str(latest_id)
        item = getItem(new_post_id)
    elif post_id == 'second':
        new_post_id = str(latest_id - 1)
        item = getItem(new_post_id)
    elif post_id == 'third':
        new_post_id = str(latest_id - 2)
        item = getItem(new_post_id)
    else:
        item = getItem(post_id)

    return item


def putPlaces(event):

    body = json.loads(event['body']) #json形式で
    prefecture = body['prefecture'] 

    try:
        # 1) オートインクリメントで新しい記事IDを取得
        post_id = str(next_id(TableName, 1))

        dynamo = boto3.client('dynamodb', region_name='ap-northeast-1')

        # 2) 取得した記事IDでアイテムを追加
        response = dynamo.put_item(
            TableName=TableName,
            Item={
                "post_id": {"S": post_id},
                "prefecture": {"S": prefecture}, 
            }
        )
        return response
    except Exception as e:
        print(e)
        return 0


def lambda_handler(event, context):

    # 1) HTTPメソッドの判定
    httpMethod = event['httpMethod']
    print(httpMethod)

    if(httpMethod == 'GET'):
        result = getPlaces(event)
    elif(httpMethod == 'POST'):
        result = putPlaces(event)

    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False),
        'isBase64Encoded': False,
        'headers': {
            "Access-Control-Allow-Origin": '*'
        }
    }