import boto3
import os
import dynamo
import heartbeat

REGION = os.environ['AWS_REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    item = event['Payload']
    if 'SpotInstanceRequestId' in item['instance_data']:
        instance_id = [item['instance_data']['InstanceId']]
        ec2.stop_instances(
            InstanceIds=instance_id
        )
    item = dynamo.pause_system(item)
    item['idle_wait'] = os.environ['FOLDING_IDLE_WAIT_PERIOD']

    heartbeat.send_hearthbeat(item)

    return item