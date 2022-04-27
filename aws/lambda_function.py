import os
import json
import boto3

TABLE = 'narf'

def get_value(key):
    dynamo = boto3.client('dynamodb')
    try:
        response = dynamo.get_item(
            TableName=TABLE,
            Key={
                'key': {
                    'S': key
                    }
                }
            )
    except:
        return '1,13' # XP_STORAGE_EXCEPTION
    if 'Item' in response:
        return '0,' + response['Item']['value']['S'] # XP_ERROR_NONE
    return '1,14' # XP_ERROR_KEY_NOT_FOUND

def lambda_handler(event, context):
    global TABLE
    TABLE = os.environ['table']
    if event['requestContext']['http']['method'] == 'GET':
        data_key = event['requestContext']['http']['path'].lstrip('/')
        key_value = get_value( data_key )
        return {
            'statusCode': 200,
            'body': key_value
        }
    return {
        'statusCode': 403,
        'body': '403 forbidden'
    }
