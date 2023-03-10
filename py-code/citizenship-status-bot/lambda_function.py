import json
import boto3
import os

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

BUCKET_NAME = os.environ['BUCKET_NAME']
PROJECT_PATH = os.environ['PROJECT_PATH']

PROMPT_EXIST_NOCRED = 'You can /register to provide credentials or /delete to stop using this bot and erase your data.'
PROMPT_EXIST_CRED_NOSUB = 'You can /check to get the status of your application, /subscribe to get automated notifications about the status, or /register to enter different credentials.'
PROMPT_EXIST_CRED_SUB = 'You can /check to get the status of your application, /unsubscribe to stop automated notifications about the status, or /register to enter different credentials.'
PROMPT_NEXIST = 'No user data. You need to /start to use the bot again.'

def check_user_exists(chat_id):
    # Specify the S3 bucket name, directory, and filename
    s3_bucket_name = BUCKET_NAME
    s3_directory = PROJECT_PATH + 'config/'
    s3_filename = 'cred' + str(chat_id) + '.config'
    s3_key = s3_directory + s3_filename

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        s3_client.get_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
        )
        print('Yes')
        return True
        
    except s3_client.exceptions.NoSuchKey:
        print('No')
        return False
   

def delete_user(chat_id):
    s3_bucket_name = BUCKET_NAME
    s3_directory = PROJECT_PATH + 'config/'
    s3_filename = 'cred' + str(chat_id) + '.config'
    s3_key = s3_directory + s3_filename
    s3_client = boto3.client('s3')
    try:
        s3_client.delete_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
        )    
        print('File deleted')
        return True
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return False
   
   
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


def cred_to_json(login, password, name, isCredValid, isSubscribed):
    credentials = {"login": login, "password": password, "name": name, "isCredValid" : isCredValid, "isSubscribed": isSubscribed}
    file = {"credentials": credentials}
    json_object = json.dumps(file, indent = 4) 
    print(json_object)
    return json_object
  
  
def credentials_to_file(chat_id, json_str):
    s3_bucket_name = BUCKET_NAME
    s3_directory = PROJECT_PATH + 'config/'
    s3_filename = 'cred' + str(chat_id) + '.config'
    s3_key = s3_directory + s3_filename
    s3_client = boto3.client('s3')
    s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=json_str,
        )    
  

  
def create_new_user(chat_id, name):
    json_str = cred_to_json('', '', name, 'False', 'False')
    credentials_to_file(chat_id, json_str)
    return


def bot_send_message(chat_id, message):
    data_res = {"text": message.encode("utf8"), "chat_id": chat_id}
    url = BASE_URL + "/sendMessage"
    requests.post(url, data_res)


'''

structure of the file with subscribed users:

{ "listSubscribedChatIDs": 
    [{"id": 13211}, {"id": 3413}]
}

'''

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
    sub_list = [x["id"] for x in sub_dict['listSubscribedChatIDs']] 
    print(sub_list)
    return sub_list
    
    
def subscribed_list_to_file(sub_list):
    
    # from list to dict
    sub_list_w_keys = [{"id": x} for x in sub_list]
    sub_dict = {"listSubscribedChatIDs" : sub_list_w_keys}
    
    # from dict to json
    json_str = json.dumps(sub_dict) 
    
    # from json to file
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
    return "success"


def insert_user_into_subcribed(chat_id):
    sub_list = subscribed_file_to_list()
    if chat_id not in sub_list:
        sub_list.append(chat_id)
        subscribed_list_to_file(sub_list)  
        return {"status":"success", "comment": "User subscribed"}  
    else:
        return {"status":"success", "comment": "User already subscribed"}
    return


def delete_user_from_subscribed(chat_id):
    sub_list = subscribed_file_to_list()
    if chat_id in sub_list:
        sub_list.remove(chat_id)
        subscribed_list_to_file(sub_list)   
        return {"status":"success", "comment": "User unsubscribed"} 
    else:
        return {"status":"success", "comment": "User already not subscribed"} 
    return


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
        FunctionName = 'citizenship-status-get' ,
        InvocationType = 'Event',
        Payload = json.dumps(inputParams))


def check_query(chat_id):
    welcome_message=''
    is_user_exists = check_user_exists(chat_id)
    if is_user_exists == True:
        print('Existing user')
        cred = read_credentials(chat_id)
        if cred['isCredValid'] == 'True':
            welcome_message+='I will check the status. Just give me a minute and I will get back to you.'
            bot_send_message(chat_id, welcome_message)
            check_tracker_status(chat_id, cred)
        else:
            welcome_message+='Please use /register first to enter your credentials'
            bot_send_message(chat_id, welcome_message)
    else:
        welcome_message = welcome_message + PROMPT_NEXIST
        bot_send_message(chat_id, welcome_message)
    

def start_query(chat_id, name):
    welcome_message = 'Hi, ' + name + '. '
    is_user_exists = check_user_exists(chat_id)
    print(str(is_user_exists))
    if is_user_exists == True:
        print('Existing user')
        cred = read_credentials(chat_id)
        print(str(cred))
        print(cred)
        if cred['isCredValid'] == 'False':
            welcome_message = welcome_message + PROMPT_EXIST_NOCRED
            print(welcome_message)
        elif (cred['isCredValid'] == 'True') and (cred['isSubscribed'] == 'False'):
            welcome_message = welcome_message + PROMPT_EXIST_CRED_NOSUB
            print(welcome_message)
        elif (cred['isCredValid'] == 'True') and (cred['isSubscribed'] == 'True'):
            welcome_message = welcome_message + PROMPT_EXIST_CRED_SUB
            print(welcome_message)
        else:
            welcome_message = welcome_message
            print(welcome_message)
        bot_send_message(chat_id, welcome_message)
    else:
        print('New user')
        create_new_user(chat_id, name)
        welcome_message = welcome_message + PROMPT_EXIST_NOCRED
        bot_send_message(chat_id, welcome_message)
        

def update_user_credentials(chat_id, login, password):
    cred = read_credentials(chat_id)
    cred['login'] = login
    cred['password'] = password
    cred['isCredValid'] = 'True'
    json_str = cred_to_json(cred['login'],  cred['password'], cred['name'], cred['isCredValid'], cred['isSubscribed'])
    credentials_to_file(chat_id, json_str)
    

def validate_register_string(chat_id, message):
    literals = message.split()
    if len(literals) !=3:
        comment = 'Input /register, your UCI and your password.\nThere should be three words separated by spaces, for example:\n /register 1234567890 qwerty'
        return {'valid': False, 'comment': comment, 'literals' : []}
    elif not (literals[1].isdigit() and 8 <= len(literals[1]) <= 10):
        comment = 'The second word should be UCI which is 8 to 10 digits'
        return {'valid': False, 'comment': comment, 'literals' : []}
    elif len(literals[2]) < 1:
        comment = 'The third word should be password which is at least 1 character long'
        return {'valid': False, 'comment': comment, 'literals' : []}
    else:
        return {'valid': True, 'literals': literals}
    return {'valid': False, 'comment': '', 'literals' : []}


def register_query(chat_id, name, message):
    welcome_message = 'Hi, ' + name + '. '
    is_user_exists = check_user_exists(chat_id)
    print(str(is_user_exists))
    if is_user_exists == True:
        validation_result = validate_register_string(chat_id, message)
        if validation_result['valid'] == True:
            print(str(validation_result['literals'][1]) + str(validation_result['literals'][2]))
            update_user_credentials(chat_id, validation_result['literals'][1],validation_result['literals'][2])
            bot_send_message(chat_id, 'Credential updated. You can press /check to check the status of the application.')
        elif validation_result['valid'] == False:
            bot_send_message(chat_id, validation_result['comment'])
        
    else:
        welcome_message = welcome_message + PROMPT_NEXIST
        bot_send_message(chat_id, welcome_message)
   

def subscribe_query(chat_id):
    welcome_message = ''
    is_user_exists = check_user_exists(chat_id)
    print(str(is_user_exists))
    if is_user_exists == True:
        insert_user_into_subcribed(chat_id)
        cred = read_credentials(chat_id)
        if cred['isSubscribed'] == 'True':
            bot_send_message(chat_id, 'Already subscribed')
        else:
            cred['isSubscribed'] = 'True'
            json_str = cred_to_json(cred['login'],  cred['password'], cred['name'], cred['isCredValid'], cred['isSubscribed'])
            credentials_to_file(chat_id, json_str)
            bot_send_message(chat_id, 'Subscribed for automated notifications.')
        welcome_message += PROMPT_EXIST_CRED_SUB
        bot_send_message(chat_id, welcome_message)
    else:
        welcome_message = welcome_message + PROMPT_NEXIST
        bot_send_message(chat_id, welcome_message)
    
    
def unsubscribe_query(chat_id):
    welcome_message = ''
    is_user_exists = check_user_exists(chat_id)
    print(str(is_user_exists))
    if is_user_exists == True:
        delete_user_from_subscribed(chat_id)
        cred = read_credentials(chat_id)
        if cred['isSubscribed'] == 'False':
            bot_send_message(chat_id, 'Already not subscribed')
        else:
            cred['isSubscribed'] = 'False'
            json_str = cred_to_json(cred['login'],  cred['password'], cred['name'], cred['isCredValid'], cred['isSubscribed'])
            credentials_to_file(chat_id, json_str)
            bot_send_message(chat_id, 'Unsubscribed from automated notifications.')
        welcome_message += PROMPT_EXIST_CRED_NOSUB
        bot_send_message(chat_id, welcome_message)
    else:
        welcome_message = welcome_message + PROMPT_NEXIST
        bot_send_message(chat_id, welcome_message)
    
    
def delete_query(chat_id):
    welcome_message = ''
    is_user_exists = check_user_exists(chat_id)
    if is_user_exists == True:
        bot_send_message(chat_id, 'Deleting user data. You can get back to interacting with the bot by pressing /start')
        if delete_user(chat_id) == True:
            delete_user_from_subscribed(chat_id)
            welcome_message = welcome_message + 'User deleted.\n' + PROMPT_NEXIST
            bot_send_message(chat_id, welcome_message)
        else:
            bot_send_message(chat_id, 'Error deleting')
    else:
        print('No user')
        welcome_message += PROMPT_NEXIST
        bot_send_message(chat_id, welcome_message)


def lambda_handler(event, context):
    data = json.loads(event["body"])
    message = str(data['message']["text"])
    chat_id = data["message"]["chat"]["id"]
    first_name = str(data["message"]["chat"]["first_name"])
    
    if "/check" in message:
        check_query(chat_id)
        
    elif "/start" in message:
        start_query(chat_id, first_name)
    
    elif "/register" in message:
        register_query(chat_id, first_name, message)
    
    elif "/subscribe" in message:
        subscribe_query(chat_id)
    
    elif "/unsubscribe" in message:
        unsubscribe_query(chat_id)
     
    elif "/delete" in message:
        delete_query(chat_id)
        
    else:
        bot_send_message(chat_id, "Unknown command. Send /start to begin")
        
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
