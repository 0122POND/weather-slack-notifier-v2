import urllib3
import os
import boto3
import requests
import json

http = urllib3.PoolManager()

dynamodb = boto3.resource("dynamodb", region_name='ap-northeast-1')

table = boto3.resource('dynamodb').Table('places')
response = table.scan(Limit=3, ReturnConsumedCapacity='TOTAL')


# エリアコード
area_dic = {'北海道/釧路':'014100',
            '北海道/旭川':'012000',
            '北海道/札幌':'016000',
            '青森県':'020000',
            '岩手県':'030000',
            '宮城県':'040000',
            '秋田県':'050000',
            '山形県':'060000',
            '福島県':'070000',
            '茨城県':'080000',
            '栃木県':'090000',
            '群馬県':'100000',
            '埼玉県':'110000',
            '千葉県':'120000',
            '東京都':'130000',
            '神奈川県':'140000',
            '新潟県':'150000',
            '富山県':'160000',
            '石川県':'170000',
            '福井県':'180000',
            '山梨県':'190000',
            '長野県':'200000',
            '岐阜県':'210000',
            '静岡県':'220000',
            '愛知県':'230000',
            '三重県':'240000',
            '滋賀県':'250000',
            '京都府':'260000',
            '大阪府':'270000',
            '兵庫県':'280000',
            '奈良県':'290000',
            '和歌山県':'300000',
            '鳥取県':'310000',
            '島根県':'320000',
            '岡山県':'330000',
            '広島県':'340000',
            '山口県':'350000',
            '徳島県':'360000',
            '香川県':'370000',
            '愛媛県':'380000',
            '高知県':'390000',
            '福岡県':'400000',
            '佐賀県':'410000',
            '長崎県':'420000',
            '熊本県':'430000',
            '大分県':'440000',
            '宮崎県':'450000',
            '鹿児島県':'460100',
            '沖縄県/那覇':'471000',
            '沖縄県/石垣':'474000'
            }



jma_url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{place_id}.json'
jma_json = requests.get(jma_url).json()
jma_date = jma_json[0]["timeSeries"][0]["timeDefines"][1]
jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][1]



def lambda_handler(event, context):
    url = "slack着信用webhookURL"
    items = response['Items']
    for item in items:
        place = item['prefecture']
        place_id = area_dic[place]

        if '雨' in jma_weather:
            msg = {
                "channel": "#general",
                "username": "user_name",
                "text": '明日、{}の天気は{}です。傘が必要です:umbrella:！。'.format(place, jma_weather),
                "icon_emoji": ""
        }
        else:
            msg = {
                "channel": "#general",
                "username": "user_name",
                "text": '明日、{}の天気は{}です。傘は必要ないです!:smile:'.format(place, jma_weather),
                "icon_emoji": ""
        }
            

        encoded_msg = json.dumps(msg).encode('utf-8')
        resp = http.request('POST', url, body=encoded_msg)
        print({
            "message": "Hello From Lambda", 
            "status_code": resp.status, 
            "response": resp.data
        })