import decimal
import os
import ec2

RUNNING_STATE = 'running'
BAD_STATE = 'bad'

PERIOD = int(int(os.environ['CREDIT_CALCULATION_PERIOD']) / 60)

def calculate_remaining_credit(remaining_credit, spot_price, node_state):
    if node_state == RUNNING_STATE:
        remaining_credit = remaining_credit - period_price(spot_price)
    if remaining_credit <= 0:
        remaining_credit = 0
    return str(remaining_credit)
    
def period_price(spot_price):
    return (spot_price / 60) * PERIOD
    