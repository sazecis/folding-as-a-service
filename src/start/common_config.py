import os

REGION = os.environ['AWS_REGION']
PROFILE = os.environ['INSTANCE_PROFILE']

KEY = "key"
SG_NODE = "sg_node"
SUBNET = "subnet"

CREDIT_TYPE_0 = '0'
CREDIT_TYPE_1 = '1'
CREDIT_TYPE_2 = '3'
CREDIT_TYPE_3 = '5'
CREDIT_TYPE_4 = '10'

FOLDING_TYPE_CPU = "only_cpu"
FOLDING_TYPE_CPU_GPU = 'cpu_gpu'

MAP_KEY_INSTANCE_TYPE = 'instance_type'
MAP_KEY_FOLDING_TYPE = 'folding_type'

folding_config = {
    'eu-north-1': {
        KEY: "stockholm",
        SG_NODE: 'sg-04ae3066b82012a4f',
        SUBNET: {
            'eu-central-1a': 'subnet-0a2792d885063a965',
            'eu-central-1b': 'subnet-01379ab4c7569b6a1',
            'eu-central-1c': 'subnet-07597e07f14481e28'
        }
    },
    'eu-west-1': {
        KEY: "ireland",
        SG_NODE: 'sg-042e10b7535782ae1',
        SUBNET: 'subnet-0588f024270d5d302',
    },
    'eu-central-1': {
        KEY: "frankfurt",
        SG_NODE: os.environ['SEC_GROUP'],
        SUBNET: {
            'eu-central-1a': os.environ['SUBNET_A'],
            'eu-central-1b': os.environ['SUBNET_B'],
            'eu-central-1c': os.environ['SUBNET_C']
        },
    }
}

credit_map = {
    CREDIT_TYPE_0: {
        MAP_KEY_INSTANCE_TYPE: 't3.micro',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU_GPU
    },
    CREDIT_TYPE_1: {
        MAP_KEY_INSTANCE_TYPE: 'c5.large',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU
    },
    CREDIT_TYPE_2: {
        MAP_KEY_INSTANCE_TYPE: 'c5.xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU
    },
    CREDIT_TYPE_3: {
        MAP_KEY_INSTANCE_TYPE: 'g4dn.xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU_GPU
    },
    CREDIT_TYPE_4: {
        MAP_KEY_INSTANCE_TYPE: 'g4dn.2xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU_GPU
    }
}


def getKey():
    return folding_config[REGION][KEY]


def getNodeSecurityGroup():
    return folding_config[REGION][SG_NODE]


def getSubnet(az):
    return folding_config[REGION][SUBNET][az]


def getFolderInstanceType(credit):
    return credit_map[credit][MAP_KEY_INSTANCE_TYPE]


def getFoldingConfigType(credit):
    return 'config_' + credit_map[credit][MAP_KEY_FOLDING_TYPE] + '.xml'

def getTableName():
    return os.environ['TABLE_NAME']
