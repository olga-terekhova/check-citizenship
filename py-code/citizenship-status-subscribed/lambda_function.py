import json
import boto3
import os

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

BUCKET_NAME = os.environ['BUCKET_NAME']
PROJECT_PATH = os.environ['PROJECT_PATH']





def subscribed_file_to_list():
    
    # open the file
    try:
        s3_bucket_name = BUCKET_NAME
        s3_directory = PROJECT_PATH + 'config/'
        s3_filename = 'subscribed.config'
        s3_key = s3_directory + s3_filename
        s3_client = boto3.client('s3')
        sub_file = s3_client.get_object(
                Bucket=s3_bucket_name,
                Key=s3_key,
            ) #NoSuchKey
    except s3_client.exceptions.NoSuchKey:
        json_str = '{ "listSubscribedChatIDs":   []}'
        s3_bucket_name = BUCKET_NAME
        s3_directory = PROJECT_PATH + 'config/'
        s3_filename = 'subscribed.config'
        s3_key = s3_directory + s3_filename
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=json_str,
        )    
        return []
        
    # read the file to json
    sub_contents = sub_file['Body'].read().decode('utf-8')
    print(sub_contents)
    
    # from json to dict
    sub_dict = json.loads(sub_contents)
    print(sub_dict)
    
    # list = dict.to list
    #sub_list = list(sub_dict['listSubscribedChatIDs'](values()))
    sub_list = [x["id"] for x in sub_dict['listSubscribedChatIDs']] 
    #list(sub_dict['listSubscribedChatIDs'](values()))
    print(sub_list)
    return sub_list

   
def json_to_cred(json_str):
    data = json.loads(json_str)
    credentials = data['credentials']
    return credentials


def read_credentials(chat_id):
    s3_bucket_name = BUCKET_NAME
    s3_directory = PROJECT_PATH + 'config/'
    s3_filename = 'cred' + str(chat_id) + '.config'
    s3_key = s3_directory + s3_filename
    s3_client = boto3.client('s3')
    cred_file = s3_client.get_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
        )
    cred_contents = cred_file['Body'].read().decode('utf-8') 
    credentials = json_to_cred(cred_contents)
    return credentials


def check_tracker_status(chat_id, cred):
    inputParams = {
            "output" : "bot",
            "chat"   : {
               
                "chat_id" : chat_id,
            },
            "cred": cred,
        }
        
    print(inputParams)
    client = boto3.client('lambda')
    runCheck = client.invoke (
        FunctionName = 'citizenship-status-get' ,# 'citizenship-status-get'), 
        InvocationType = 'Event',
        Payload = json.dumps(inputParams))


def subscribed_run():
    for chat_id in subscribed_file_to_list():
        print(chat_id)
        cred = read_credentials(chat_id)
        if cred['isCredValid'] == 'True':
            check_tracker_status(chat_id, cred)


def lambda_handler(event, context):
    # TODO implement
    subscribed_run()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
