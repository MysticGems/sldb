"""
Simple queries and updates to SLDB-type key-value database
"""
import os
import logging
import hashlib
import boto3

# Configure logging
logging.getLogger().setLevel(logging.INFO)

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
    except ClientError as e:
        logging.warning( 'Error talking to DynamoDB: %s', e )
        return '0,13' # XP_STORAGE_EXCEPTION
    if 'Item' in response:
        return '1,' + response['Item']['value']['S'] # XP_ERROR_NONE
    logging.info( 'Key not found' )
    return '0,14' # XP_ERROR_KEY_NOT_FOUND

def put_value(key, value):
    """
    Database write
    """
    dynamo = boto3.client('dynamodb')
    # Limit bodies to 4095 characters
    value = value[:4095]
    try:
        response = dynamo.put_item(
            TableName=os.environ['table'],
            Item={
                'key': {
                    'S': key
                    },
                'value': {
                    'S': value
                    }
                }
            )
    except ClientError as e:
        logging.warning( 'Error talking to DynamoDB: %s', e )
        return '0,13' # XP_STORAGE_EXCEPTION
    return '1,' + value # XP_ERROR_NONE

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
        logging.info( 'Auth hash %s, header %s' )
        return authentication == headers['secure']
    except:
        logging.info('Error attempting authorization')
        return False
        
BAD_REQUEST = {
    'statusCode': 400,
    'headers': {'Content-Type': 'text/plain' },
    'body': '400 Bad Request'
}

def lambda_handler(event, context):
    """
    Request handler
    """
    if 'requestContext' not in event:
        logging.error('Not an http(s) request')
        return BAD_REQUEST
    if 'x-secondlife-object-key' not in event['headers']:
        logging.error(
            'No object key in headers; not a Second Life request. From %s for %s via %s',
            event['requestContext']['http']['sourceIp'],
            event['requestContext']['http']['path'],
            event['requestContext']['http']['userAgent']
        )
        return BAD_REQUEST
    data_key = event['requestContext']['http']['path'].lstrip('/')
    if not authenticate( data_key, event['headers'], os.environ['secret'] ):
        logging.warning('Not authorized')
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain' },
            'body': '0,4' # XP_ERROR_NOT_PERMITTED
        }
    if event['requestContext']['http']['method'] == 'GET':
        key_value = get_value( data_key )
        logging.info('Retrieved %s', data_key)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain' },
            'body': key_value
        }
    if event['requestContext']['http']['method'] == 'PUT':
        if 'body' not in event:
            logging.warn('Update without payload')
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'text/plain' },
                'body': '400 Bad Request: No payload'
                }
        key_value = put_value( data_key, event['body'] )
        logging.info('Updated %s', data_key)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain' },
            'body': key_value
        }
    logging.warning('Unrecognized request method')
    return {
        'statusCode': 501,
        'headers': {'Content-Type': 'text/plain' },
        'body': '501 Not Implemented'
    }
