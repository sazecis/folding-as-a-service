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
    #minPrice = decimal.Decimal(1000)
    historyPrices = {}
    histories = data['SpotPriceHistory']
    print(histories)
    #bestSpot = None
    for history in histories:
        historyPrices[history['AvailabilityZone']] = decimal.Decimal(
            history['SpotPrice']) + decimal.Decimal(0.005)
        #historyPrices.append(decimal.Decimal(history['SpotPrice']) + decimal.Decimal(0.005))
        '''if historyPrice < minPrice:
            minPrice = historyPrice
            history['SpotPrice'] = historyPrice + decimal.Decimal(0.005)
            bestSpot = history
            print('spot price of ' + instance_type + ' in region ' +
                  common_config.REGION + ': ' + str(minPrice))'''
    '''sorted_histories = {}
    for price in sorted(historyPrices):
        SpotPrice
        AvailabilityZone'''
    return dict(sorted(historyPrices.items(), key=lambda x: x[1]))
