import json
import dynamo
import boto3
import os
import heartbeat

REGION = os.environ['AWS_REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    record = jsonify(event['Records'][0]['body'])
    print(record)
    dynamo.update_system_status(record)
    item = dynamo.get_system_data(record)
    if heartbeat.alive(item):
        print('System still functioning with normal parameters')
    else:
        print(f"No hearbeat received from the {item['system_id']} system. Terminating it.")
        spot_request_id = [item['instance_data']['SpotInstanceRequestId']]
        instance_id = [item['instance_data']['InstanceId']]
        ec2.cancel_spot_instance_requests(
            SpotInstanceRequestIds=spot_request_id)
        ec2.terminate_instances(InstanceIds=instance_id)
        dynamo.terminate_system(item)
    return {
        'statusCode': 200,
        'body': json.dumps('folding-S-symbiote-watcher coml!')
    }

def jsonify(map):
    return json.loads(map.replace("\'", "\""))
