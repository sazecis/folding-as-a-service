import boto3
import json
import os
import dynamo
import heartbeat

REGION = os.environ['AWS_REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    print(event[0])    
    item = event[0]['Payload']
    heartbeat.send_hearthbeat(item)

    if 'SpotInstanceRequestId' in item['instance_data']:
        spot_request_id = [item['instance_data']
                           ['SpotInstanceRequestId']]
        instance_id = [item['instance_data']['InstanceId']]
        ec2.cancel_spot_instance_requests(
            SpotInstanceRequestIds=spot_request_id)
        ec2.terminate_instances(InstanceIds=instance_id)
    dynamo.terminate_system(item)

    remaining_credit = item['remaining_credit']
    basic_credit = item['basic_credit']
    remaining_credit_percent = remaining_credit * 100 / basic_credit
    if remaining_credit_percent > 10:
        item['system_status'] = 'remained_credits'
    else:
        item['system_status'] = 'terminated'

    return item
