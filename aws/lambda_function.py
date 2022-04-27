import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    if event['requestContext']['http']['method'] == 'GET':
        data_key = event['requestContext']['http']['path'].lstrip('/')
        return {
            'statusCode': 200,
            'body': data_key
        }
    return {
        'statusCode': 403,
        'body': '403 forbidden'
    }
