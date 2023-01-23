import datetime

CPU = 'cpu'
GPU = 'gpu'
NO_JOB = 'no_job_'
LINE = 'line'
DATA = 'data'
IDLE_STATUS_STRING = 'idle'
FOLDING_STATUS_STRING = 'folding'
INIT_STATUS_STRING = 'initializing'
OVERALL_STATUS_STRING = 'overall_status'

def getFoldingStatus():
	with open('/var/lib/fahclient/log.txt') as myfile:
		is_cpu = False
		is_gpu = False
		for line in myfile:
			if not is_cpu:
				if 'type=\'CPU\'' in line:
					is_cpu = True
			else:
				if 'type=\'GPU\'' in line:
					is_gpu = True
				break

		raw = {
			CPU: None,
			GPU: None,
			NO_JOB + CPU: None, 
			NO_JOB + GPU: None
		}

		info = {}
		logs = list(myfile)
		initializing = True
		for line in logs:
			if 'Completed' in line or 'Exception: Could not get an assignment' in line or 'Failed to get assignment' in line:
				initializing = False				
		if initializing:
			info[OVERALL_STATUS_STRING] = INIT_STATUS_STRING
			return info
		for i in range(-10, -1):
			if 'Completed' in logs[i]:
				if 'FS00' in logs[i]:
					raw[CPU] = { LINE: i, DATA: logs[i] }
				if 'FS01' in logs[i]:
					raw[GPU] = { LINE: i, DATA: logs[i] }
			if 'Exception: Could not get an assignment' in logs[i] or 'Failed to get assignment' in logs[i]:
				if 'FS00' in logs[i]:
					raw[NO_JOB + CPU] = { LINE: i, DATA: logs[i] }
				if 'FS01' in logs[i]:
					raw[NO_JOB + GPU] = { LINE: i, DATA: logs[i] }

		
		if is_gpu:
			info[GPU] = getInfo(GPU, raw)
			if info[GPU]['status'] == FOLDING_STATUS_STRING:
				info[OVERALL_STATUS_STRING] = FOLDING_STATUS_STRING
			else: 
				info[OVERALL_STATUS_STRING] = IDLE_STATUS_STRING
		info[CPU] = getInfo(CPU, raw)
		if GPU not in info:
			if info[CPU]['status'] == FOLDING_STATUS_STRING:
				info[OVERALL_STATUS_STRING] = FOLDING_STATUS_STRING
			else:
				info[OVERALL_STATUS_STRING] = IDLE_STATUS_STRING

		info['log_time'] = str(datetime.datetime.now())

		return info

def getInfo(folding_type, raw):
	info = None
	if raw[folding_type] is None or (raw[NO_JOB + folding_type] is not None and raw[NO_JOB + folding_type][LINE] > raw[folding_type][LINE]):
		info = getIdleInfo()
	else:
		info = getFoldingInfo(raw[folding_type][DATA])
	return info

def getFoldingInfo(data):
	parts = data.split(':')[-1].split(' ')
	return {'status': FOLDING_STATUS_STRING,
				'completed': parts[1],
				'total': parts[4]
		}

def getIdleInfo():
	return {'status': IDLE_STATUS_STRING,
			'completed': 'NA',
			'total': 'NA'
		}