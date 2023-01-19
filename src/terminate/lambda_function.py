import boto3
import json
import os
import dynamo

REGION = os.environ['AWS_REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    print(event[0])
    item = event[0]['Payload']
    if 'SpotInstanceRequestId' in item['instance_data']:
        spot_request_id = [item['instance_data']
                           ['SpotInstanceRequestId']]
        instance_id = [item['instance_data']['InstanceId']]
        ec2.cancel_spot_instance_requests(
            SpotInstanceRequestIds=spot_request_id)
        ec2.terminate_instances(InstanceIds=instance_id)
    dynamo.terminate_system(item)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully finished request!')
    }
