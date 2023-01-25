from datetime import datetime
import pytz
import boto3
import os

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def send_hearthbeat(item):
    dynamo.update_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set heartbeat= :h',
        ExpressionAttributeValues={
            ':h': datetime.now(tz=pytz.UTC).strftime(FORMAT),
        },
        ReturnValues="UPDATED_NEW"
    )
    return item

def get_heartbeat(item):
    item = dynamo.get_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        }
    )
    return item['Item']['heartbeat']


def alive(item):
    print(item)
    now = datetime.strptime(datetime.now(tz=pytz.UTC).strftime(FORMAT), FORMAT)
    last = datetime.strptime(get_heartbeat(item), FORMAT)
    difference = now - last
    if difference.seconds > 3600:
        return False
    return True
