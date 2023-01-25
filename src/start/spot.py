import boto3
import common_config
import decimal

ec2 = boto3.client('ec2', region_name=common_config.REGION)


def get_spot_prices(instance_type):
    data = ec2.describe_spot_price_history(
        InstanceTypes=[
            instance_type
        ],
        MaxResults=5,
        ProductDescriptions=[
            'Linux/UNIX',
        ],
    )
    historyPrices = {}
    histories = data['SpotPriceHistory']
    print(histories)
    for history in histories:
        historyPrices[history['AvailabilityZone']] = decimal.Decimal(
            history['SpotPrice']) + decimal.Decimal(0.005)
    return dict(sorted(historyPrices.items(), key=lambda x: x[1]))
