import json
import dynamo

def lambda_handler(event, context):
    for record in event['Records']:
        print(record['body'])
        dynamo.update_system_status(jsonify(record['body']))
    return {
        'statusCode': 200,
        'body': json.dumps('folding-S-symbiote-watcher coml!')
    }


def jsonify(map):
    return json.loads(map.replace("\'", "\""))
