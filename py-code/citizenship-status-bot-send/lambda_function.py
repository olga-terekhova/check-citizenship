import json
import boto3
import requests
import os

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
BUCKET_NAME = os.environ['BUCKET_NAME']  # name of the AWS S3 bucket to store configs and results
PROJECT_PATH = 'projects/citizenship/' # path in the S3 bucket to the project directory 


def bot_send_message(chat_id, message):
    data_res = {"text": message.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    requests.post(url, data_res)
    
    
def bot_send_picture(chat_id, message, picture):
    data_res = {"chat_id": chat_id, "caption": message}
    url = BASE_URL + "/sendPhoto"
    requests.post(url, data = data_res, files = picture)
    

def lambda_handler(event, context):
    chat_id = event['chat']['chat_id']
    if "image" in event['result']:
        message = "Updated: " + event['result']['text']
        bucket_name = event['result']['image']['bucket']
        image_key = event['result']['image']['key']
    
        s3_client = boto3.client("s3")
        pngFile = s3_client.get_object(Bucket = bucket_name, Key = image_key)
        pngContent = {"photo":  pngFile['Body'].read() }
        bot_send_picture(chat_id, message, pngContent)
    else:
        bot_send_message(chat_id, event['result']['text'])
    
   
