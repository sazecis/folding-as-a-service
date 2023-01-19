import boto3
import os

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

def get_item_data(item):
    return dynamo.get_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        }
    )['Item']

def update_item_data(item):
    dynamo.update_item(
        Key = {
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set remaining_credit= :r',
        ExpressionAttributeValues={
            ':r': item['remaining_credit'],
        },
        ReturnValues="UPDATED_NEW"
    )
    return item