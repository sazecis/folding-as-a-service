import boto3
import os
 
REGION = os.environ['AWS_REGION']
ec2 = boto3.client('ec2', region_name=REGION)

def getInstanceDetailedData(instance_data):
    return ec2.describe_instances(InstanceIds=[instance_data['InstanceId']])['Reservations'][0]['Instances'][0]

def getInstanceState(instance_data):
    return instance_data['State']['Name']

def getPublicIp(instance_data):
    return instance_data['PublicIpAddress']
