import boto3
import common_config as config

dynamo = boto3.resource('dynamodb').Table(config.getTableName())


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

def get_test_data(system_id, system_ip):
    item = dynamo.get_item(
        Key = {
            'system_id': system_id,
            'system_ip': system_ip
        }
    )
    return item