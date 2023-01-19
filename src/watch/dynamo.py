import os
import boto3

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])


def update_system_status(item):
    dynamo.update_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set folding_info= :s',
        ExpressionAttributeValues={
            ':s': item['folding_info'],
        },
        ReturnValues="UPDATED_NEW"
    )

    return item
