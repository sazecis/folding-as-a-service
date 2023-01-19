import os
import boto3

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

def pause_system(item):
    print(item)
    item['system_status'] = 'paused'
    dynamo.update_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set system_status= :s',
        ExpressionAttributeValues={
            ':s': item['system_status'],
        },
        ReturnValues="UPDATED_NEW"
    )
    return item
