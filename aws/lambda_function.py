"""
Simple queries and updates to SLDB-type key-value database
"""
import os
import hashlib
import boto3

def get_value(key):
    """
    Actually fetch data from the database
    """
    dynamo = boto3.client('dynamodb')
    try:
        response = dynamo.get_item(
            TableName=os.environ['table'],
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

def get_secret(secret):
    """
    Get secret for authentication
    """
    secret_manager = boto3.client('secretsmanager')
    try:
        response = secret_manager.get_secret_value( SecretId=secret )
        return response['SecretString']
    except:
        return ''

def authenticate(data_key, headers, secret_value):
    """
    Authenticate the request
    """
    try:
        auth_hash = hashlib.sha1(
            headers['x-secondlife-object-key']
            + data_key
            + secret_value
        )
        authentication = auth_hash.hexdigest()
        return authentication == headers['secure']
    except:
        return False

def lambda_handler(event, context):
    """
    Request handler
    """
    if event['requestContext']['http']['method'] == 'GET':
        data_key = event['requestContext']['http']['path'].lstrip('/')
        secret = get_secret(os.environ['secret'])
        if not secret:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/plain' },
                'body': '1,13' # XP_STORAGE_EXCEPTION
            }
        if not authenticate( key_value, event['headers'], secret ):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/plain' },
                'body': '1,4' # XP_ERROR_NOT_PERMITTED
            }
        key_value = get_value( data_key )
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain' },
            'body': key_value
        }
    return {
        'statusCode': 403,
        'headers': {'Content-Type': 'text/plain' },
        'body': '403 forbidden'
    }
