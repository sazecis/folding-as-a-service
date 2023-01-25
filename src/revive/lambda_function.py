import botocore
import boto3
import os
import dynamo

REGION = os.environ['AWS_REGION']

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    item = event['Payload']
    if 'SpotInstanceRequestId' in item['instance_data']:
        instance_id = [item['instance_data']['InstanceId']]
        try:
            ec2.start_instances(
                InstanceIds=instance_id
            )
        except botocore.exceptions.ClientError as error:
            print(error)
            if "InsufficientInstanceCapacity" in str(error):
                item['spot_available'] = 'false'
                item['idle_wait'] = os.environ['FOLDING_IDLE_WAIT_PERIOD']
                return item

    item['spot_available'] = 'true'
    item['credit_period'] = os.environ['CREDIT_CALCULATION_PERIOD']
    return dynamo.revive_system(item)
    