import os
import boto3
import time
import logging
import socket    
import foldingenv
import folding_s_symbiote_inner_status
 
log = logging.getLogger("folding-S-symbiote.log")

sqs = boto3.client('sqs')

idle_count = 0
IDLE_THRESHOLD = 3

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
