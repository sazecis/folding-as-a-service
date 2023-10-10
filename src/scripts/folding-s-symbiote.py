import os
import boto3
import time
import logging
import socket    
import requests
import foldingenv
import folding_s_symbiote_inner_status
 
log = logging.getLogger("folding-S-symbiote.log")

idle_count = 0
IDLE_THRESHOLD = 3

response = requests.get(
    "http://169.254.169.254/latest/dynamic/instance-identity/document")

if response.status_code == 200:
    data = response.json()
    region = data.get("region", None)
else:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

sqs = boto3.client('sqs', region_name=region)

while True:
	folding_info = folding_s_symbiote_inner_status.getFoldingStatus()
	folding_status = folding_info[folding_s_symbiote_inner_status.OVERALL_STATUS_STRING]
	status_to_send = None
	if folding_status == folding_s_symbiote_inner_status.IDLE_STATUS_STRING:
		idle_count = idle_count + 1
		if idle_count > IDLE_THRESHOLD:
			status_to_send = folding_s_symbiote_inner_status.IDLE_STATUS_STRING
		else:
			status_to_send = folding_s_symbiote_inner_status.FOLDING_STATUS_STRING
	else:
		idle_count = 0
		status_to_send = folding_s_symbiote_inner_status.FOLDING_STATUS_STRING

	folding_info[folding_s_symbiote_inner_status.OVERALL_STATUS_STRING] = status_to_send

	hostname = socket.gethostname()    
	ip = socket.gethostbyname(hostname)    

	message = {
		'folder': foldingenv.FOLDER,
		'system_id': foldingenv.INSTANCE_ID,
		'system_ip': ip,
		'folding_info': folding_info
	}
	response = sqs.send_message(
		QueueUrl=foldingenv.QUEUE_URL,
		DelaySeconds=0,
		MessageAttributes={
		},
		MessageBody=(
			str(message)
		)
	)

	print(response['MessageId'])
	time.sleep(300)
