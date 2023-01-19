import os
import boto3

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

def revive_system(item):
    item['system_status'] = 'running'
    item['folding_info']['overall_status'] = 'initializing'
    dynamo.update_item(
        Key = {
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set system_status= :s, folding_info.overall_status= :f',
        ExpressionAttributeValues={
            ':s': item['system_status'],
            ':f': item['folding_info']['overall_status']
        },
        ReturnValues="UPDATED_NEW"
    )
    print('Revive system status:')
    print(item)
    return item
