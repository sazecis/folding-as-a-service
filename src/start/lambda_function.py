import os
import botocore
import boto3
import common_config
import spot
import dynamo
import decimal

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

    if 'MyIp' in input:
        my_ip = str(input['MyIp'])
    else:
        my_ip = '0/0'

    config = common_config.getFoldingConfigType(str(credit))
    ami = getAmi(credit)
    spot_available = False
    for available_spot in spot.get_spot_prices(folder_instance_type).items():
        best_spot = available_spot
        node_price = best_spot[1]
        try:
            node_instance = create_spot_instances(ami, folder_instance_type, init_script_folders(
                config, my_ip), user, node_price, best_spot[0])
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
    return system_info


def filterRelevantData(instance_data, price):
    print(instance_data)
    data = {
        'InstanceId': checkForEmptyObject(instance_data['InstanceId']),
        'InstanceType': checkForEmptyObject(instance_data['InstanceType']),
        'LaunchTime': checkForEmptyObject(instance_data['LaunchTime']).__str__(),
        'PrivateIpAddress': checkForEmptyObject(instance_data['PrivateIpAddress']),
        'Price': price,
        'PublicIpAddress': getItemFromDictionary(instance_data, 'PublicIpAddress'),
        'SpotInstanceRequestId': getItemFromDictionary(instance_data, 'SpotInstanceRequestId')
    }

    return data

def checkForEmptyObject(object):
    if object is None:
        return 'NA'
    else:
        return object

def getItemFromDictionary(dictionary, item):
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
    return filterRelevantData(instance['Instances'][0], price)

def init_script_folders(config, my_ip):
    init_script = ('#!/bin/bash' + '\n'
                   '@echo on' + '\n'
                   'sudo su' + '\n'
                   'yum -y install git' + '\n'
                   'mkdir /usr/bin/faas' + '\n'
                   'cd /usr/bin/faas' + '\n'
                   'git clone https://github.com/sazecis/folding-as-a-service.git' + '\n'
                   'wget ' + FOLDING_AT_HOME_RPM_URL + '\n'
                   'rpm -i --nodeps ' + FOLDING_AT_HOME_RPM_NAME + '\n'
                   '/etc/init.d/FAHClient stop' + '\n'
                   'python3 folding-as-a-service/src/scripts/folding_config_creator.py ' + config + ' ' + my_ip + '\n'
                   'cp config.xml /etc/fahclient/config.xml' + '\n'
                   'chmod 0444 /etc/fahclient/config.xml' + '\n'
                   '/etc/init.d/FAHClient start' + '\n'
                   'pip3 install boto3' + '\n'
                   'aws configure set default.region ' + common_config.REGION + '\n'
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
                   'sleep 10' + '\n'
                   'reboot' + '\n'
                   )
    return init_script


def getAmi(credit):
    if credit > 3:
        return 'ami-0b88c2f986a9d4947'  # deepofficial

    responsessm = ssm.get_parameter(
        Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
    )
    return str(responsessm['Parameter']['Value'])
