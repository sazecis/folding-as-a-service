import os
import decimal
import dynamo
import credit
import ec2

REMAINING_CREDIT = 'remaining_credit'
INSTANCE_DATA = 'instance_data'
PRICE = 'Price'
SYSTEM_STATUS = 'system_status'

def lambda_handler(event, context):
    print(event)
    item = dynamo.get_item_data(event['Payload'])
    instance_data = item[INSTANCE_DATA]
    node_state = ec2.getInstanceState(instance_data)
    remaining_credit = decimal.Decimal(item[REMAINING_CREDIT])
    spot_price = decimal.Decimal(item[INSTANCE_DATA][PRICE])
    item[REMAINING_CREDIT] = credit.calculate_remaining_credit(remaining_credit, spot_price, node_state)
    item[SYSTEM_STATUS] = ec2.getInstanceState(item[INSTANCE_DATA])
    dynamo.update_item_data(item)
    item['credit_period'] = os.environ['CREDIT_CALCULATION_PERIOD']
    if 'ERROR_TEST' in os.environ and os.environ['ERROR_TEST']:
        raise Exception('Test exception')
    print(item)
    return item
