import os
import botocore
import boto3
import common_config
import spot
import dynamo
import decimal
import heartbeat

EMAIL = 'test@test.test'
PROJECT = 'folding.S.symbiote'

FOLDING_AT_HOME_RPM_NAME = 'fahclient-7.6.21-1.x86_64.rpm'
FOLDING_AT_HOME_RPM_URL = 'https://download.foldingathome.org/releases/public/release/fahclient/centos-6.7-64bit/v7.6/' + FOLDING_AT_HOME_RPM_NAME
QUEUE_URL = os.environ['QUEUE_URL']

PRIVATE_IP_ADDRESS = 'PrivateIpAddress'

ec2 = boto3.client('ec2', region_name=common_config.REGION)
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    print(event)
    input = event
    if 'Payload' in input:
        input = input['Payload']

    if 'test' in input:
        system_id = input['test']['system_id']
        system_ip = input['test']['system_ip']
        output = dynamo.get_test_data(system_id, system_ip)['Item']
        return output

    if 'Credit' in input:
        credit = decimal.Decimal(input['Credit'])
        folder_instance_type = common_config.getFolderInstanceType(str(credit))
    else:
        credit = decimal.Decimal(input['basic_credit'])
        folder_instance_type = input['instance_data']['InstanceType']

    if 'User' in input:
        user = str(input['User'])
    else:
        user = str(input['user'])

    my_ip = os.environ['MY_IP']

    config = common_config.getFoldingConfigType(str(credit))
    ami = get_ami(credit)
    spot_available = False
    for available_spot in spot.get_spot_prices(folder_instance_type).items():
        best_spot = available_spot
        node_price = best_spot[1]
        try:
            node_instance = create_spot_instances(ami, folder_instance_type, generate_ec2_user_data(
                config, user, my_ip), user, node_price, best_spot[0])
            spot_available = True
            break
        except botocore.exceptions.ClientError as error:
            print('No spot available in ' + best_spot[0])
            print(error)

    if not spot_available:
        system_info = {
            'spot_available': 'false',
            'Credit': str(credit),
            'User': user,
            'spot_wait': os.environ['SPOT_WAIT_PERIOD']
        }
        return system_info

    if 'Credit' in input:
        system_info = dynamo.add_new_system(
            EMAIL, user, node_instance, credit, credit, 'true')
    else:
        system_info = dynamo.add_new_system(
            EMAIL, user, node_instance, input['basic_credit'], input['remaining_credit'], 'true')

    system_info['folding_info'] = {}
    system_info['folding_info']['overall_status'] = 'initializing'
    if 'period' not in input:
        system_info['credit_period'] = os.environ['CREDIT_CALCULATION_PERIOD']
    else:
        system_info['credit_period'] = input['period']

    heartbeat.send_hearthbeat(system_info)

    return system_info


def filter_relevant_data(instance_data, price):
    print(instance_data)
    data = {
        'InstanceId': check_for_empty_object(instance_data['InstanceId']),
        'InstanceType': check_for_empty_object(instance_data['InstanceType']),
        'LaunchTime': check_for_empty_object(instance_data['LaunchTime']).__str__(),
        'PrivateIpAddress': check_for_empty_object(instance_data['PrivateIpAddress']),
        'Price': price,
        'PublicIpAddress': get_item_from_dictionary(instance_data, 'PublicIpAddress'),
        'SpotInstanceRequestId': get_item_from_dictionary(instance_data, 'SpotInstanceRequestId')
    }

    return data

def check_for_empty_object(object):
    if object is None:
        return 'NA'
    else:
        return object

def get_item_from_dictionary(dictionary, item):
    if item in dictionary:
        return dictionary[item]
    return 'NA'

def create_spot_instances(ami, instance_type, init_script, user, price, az):
    instance = ec2.run_instances(
        ImageId=ami,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[
            common_config.getNodeSecurityGroup(),
        ],
        SubnetId=common_config.getSubnet(az),
        IamInstanceProfile={
            'Arn': common_config.PROFILE
        },
        InstanceInitiatedShutdownBehavior='stop',
        InstanceMarketOptions={
            'MarketType': 'spot',
            'SpotOptions': {
                'MaxPrice': str(price),
                'SpotInstanceType': 'persistent',
                'InstanceInterruptionBehavior': 'stop'
            }
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': PROJECT + '.' + user
                    },
                ]
            },
            {
                'ResourceType': 'spot-instances-request',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': PROJECT + '.' + user
                    },
                ]
            },
            {
                'ResourceType': 'volume',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': PROJECT + '.' + user
                    },
                ]
            },
        ],
        UserData=init_script
    )
    return filter_relevant_data(instance['Instances'][0], price)

def generate_ec2_user_data(config, user, my_ip):
    init_script = ('#!/bin/bash' + '\n'
                   '@echo on' + '\n'
                   'sudo su' + '\n'
                   'yum -y install git' + '\n'
                   'mkdir /usr/bin/faas' + '\n'
                   'cd /usr/bin/faas' + '\n'
                   'git clone https://github.com/sazecis/folding-as-a-service.git' + '\n'
                   'wget ' + FOLDING_AT_HOME_RPM_URL + '\n'
                   'rpm -i --nodeps ' + FOLDING_AT_HOME_RPM_NAME + '\n'
                   'instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)' + '\n'
                   'touch /usr/bin/foldingenv.py' + '\n'
                   'echo \"QUEUE_URL=\'' + QUEUE_URL + '\'\" >> /usr/bin/foldingenv.py' + '\n'
                   'echo \"FOLDER=\'' + user + '\'\" >> /usr/bin/foldingenv.py' + '\n'
                   'echo \"INSTANCE_ID=\'$instance_id\'\" >> /usr/bin/foldingenv.py' + '\n'
                   'cp folding-as-a-service/src/scripts/folding-s-symbiote.py /usr/bin/folding-s-symbiote.py' + '\n'
                   'cp folding-as-a-service/src/scripts/folding_s_symbiote_inner_status.py /usr/bin/folding_s_symbiote_inner_status.py' + '\n'
                   'chmod 755 /usr/bin/folding-s-symbiote.py' + '\n'
                   'cp folding-as-a-service/src/scripts/folding-s-symbiote.sentinel.service /lib/systemd/system/folding-s-symbiote.sentinel.service' + '\n'
                   'systemctl daemon-reload' + '\n'
                   'systemctl enable --now --no-block folding-s-symbiote.sentinel.service' + '\n'
                   'sleep 90' + '\n'
                   'python folding-as-a-service/src/scripts/folding_config_creator.py ' + config + ' ' + my_ip + '\n'
                   'cp config.xml /etc/fahclient/config.xml' + '\n'
                   'systemctl restart FAHClient.service' + '\n'
                   'reboot' + '\n'
                   )
    return init_script


def get_ami(credit):
    if credit > 3:
        return get_gpu_ami()

    responsessm = ssm.get_parameter(
        Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
    )
    return str(responsessm['Parameter']['Value'])


def get_gpu_ami():
    result = ec2.describe_images(
        Filters=[
            {
                'Name': 'name',
                'Values': ['Deep Learning AMI GPU TensorFlow*Amazon Linux 2*']
            }
        ]
    )
    newlist = sorted(result['Images'],
                     key=lambda d: d['CreationDate'], reverse=True)
    return newlist[0]['ImageId']
