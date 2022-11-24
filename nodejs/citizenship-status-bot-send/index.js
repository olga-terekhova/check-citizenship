import json
import boto3
import requests
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
BUCKET_NAME = os.environ['BUCKET_NAME']  # name of the AWS S3 bucket to store configs and results
PROJECT_PATH = 'projects/citizenship/' # path in the S3 bucket to the project directory 

def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    first_name = event['name']
    chat_id = event['chat_id']
    credlist = event['credlist']
    
    prefixText = PROJECT_PATH + 'output/timeline-text/'
    prefixPic = PROJECT_PATH + 'output/timeline-pic/'
    
    for cred in credlist:
        jsonKey = prefixText + cred +".json"
        jsonFile = s3_client.get_object(Bucket = BUCKET_NAME, Key = jsonKey)
        jsonCredDate = json.loads(jsonFile['Body'].read())['lastUpdateDate']
        pngKey = prefixPic + cred+".png"
        pngFile = s3_client.get_object(Bucket = BUCKET_NAME, Key = pngKey)
        pngContent = {"photo":  pngFile['Body'].read() }
        
        data_res = {"chat_id": chat_id, "caption": cred + " - Last update date: " + jsonCredDate}
        url = BASE_URL + "/sendPhoto"
        requests.post(url, data = data_res, files = pngContent)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
