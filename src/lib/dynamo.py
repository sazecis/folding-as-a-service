import os
import boto3

dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

def add_new_system(email, user, node_instance, basic_credit, remaining_credit, spot_available):
    item = {'system_id': node_instance['InstanceId'],
            'system_ip': node_instance['PrivateIpAddress'],
            'email': email,
            'user': user,
            'instance_data': node_instance,
            'system_status': 'running',
            'basic_credit': basic_credit,
            'remaining_credit': remaining_credit,
            'spot_available': spot_available,
            'folding_info': {
        'overall_status': 'initializing'
    }
    }
    dynamo.put_item(Item=item)
    return item

def get_system_data(item):
    return dynamo.get_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        }
    )['Item']

def update_credit_and_public_ip(item):
    dynamo.update_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set remaining_credit= :r, instance_data.PublicIpAddress= :ip',
        ExpressionAttributeValues={
            ':r': item['remaining_credit'],
            ':ip': item['instance_data']['PublicIpAddress']
        },
        ReturnValues="UPDATED_NEW"
    )
    return item

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

def get_test_data(system_id, system_ip):
    item = dynamo.get_item(
        Key={
            'system_id': system_id,
            'system_ip': system_ip
        }
    )
    return item

def revive_system(item):
    item['system_status'] = 'running'
    item['folding_info']['overall_status'] = 'initializing'
    dynamo.update_item(
        Key={
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

def terminate_system(item):
    print(item)
    dynamo.update_item(
        Key={
            'system_id': item['system_id'],
            'system_ip': item['system_ip']
        },
        UpdateExpression='set system_status= :s',
        ExpressionAttributeValues={
            ':s': 'terminated',
        },
        ReturnValues="UPDATED_NEW"
    )
    return item
