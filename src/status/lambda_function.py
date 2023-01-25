import os
import decimal
import dynamo
import credit
import ec2
import heartbeat

REMAINING_CREDIT = 'remaining_credit'
INSTANCE_DATA = 'instance_data'
PRICE = 'Price'
SYSTEM_STATUS = 'system_status'
PUBLIC_IP = 'PublicIpAddress'

def lambda_handler(event, context):
    print(event)
    item = dynamo.get_item_data(event['Payload'])

    instance_data = ec2.getInstanceDetailedData(item[INSTANCE_DATA])
    node_state = ec2.getInstanceState(instance_data)
    remaining_credit = decimal.Decimal(item[REMAINING_CREDIT])
    spot_price = decimal.Decimal(item[INSTANCE_DATA][PRICE])
    public_ip = ec2.getPublicIp(instance_data)

    item[REMAINING_CREDIT] = credit.calculate_remaining_credit(remaining_credit, spot_price, node_state)
    item[SYSTEM_STATUS] = node_state
    item[INSTANCE_DATA][PUBLIC_IP] = public_ip

    dynamo.update_item_data(item)

    item['credit_period'] = os.environ['CREDIT_CALCULATION_PERIOD']
    if 'ERROR_TEST' in os.environ and os.environ['ERROR_TEST']:
        raise Exception('Test exception')
    
    heartbeat.send_hearthbeat(item)

    print(item)
    return item
