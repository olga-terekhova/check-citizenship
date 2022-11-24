import json
import boto3
import os
# import sys

# here = os.path.dirname(os.path.realpath(__file__))
# sys.path.append(os.path.join(here, "./vendored"))

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

def lambda_handler(event, context):
    data = json.loads(event["body"])
    message = str(data['message']["text"])
    chat_id = data["message"]["chat"]["id"]
    first_name = str(data["message"]["chat"]["first_name"])
    if "check" in message:
        response = "Hello {}, I will check the status. Just give me a minute and I will get back to you. ".format(first_name) 
        print(response)
        
        data_res = {"text": response.encode("utf8"), "chat_id": chat_id}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data_res)
        
        inputParams = {
            "output" : "bot",
            "chat"   : {
                "name"    : first_name,
                "chat_id" : chat_id,
            }
        }
        
        client = boto3.client('lambda')
        runCheck = client.invoke (
            FunctionName = 'citizenship-status-get' ,# 'citizenship-status-get'), 
            InvocationType = 'Event',
            Payload = json.dumps(inputParams))
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
