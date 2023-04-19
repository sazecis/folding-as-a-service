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

FOLDING_TYPE_CPU = 'only_cpu'
FOLDING_TYPE_CPU_GPU = 'cpu_gpu'

MAP_KEY_INSTANCE_TYPE = 'instance_type'
MAP_KEY_FOLDING_TYPE = 'folding_type'

folding_config = {
    REGION: {
        SG_NODE: os.environ['SEC_GROUP'],
        SUBNET: {
            REGION + 'a': os.environ['SUBNET_A'],
            REGION + 'b': os.environ['SUBNET_B'],
            REGION + 'c': os.environ['SUBNET_C']
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
        MAP_KEY_INSTANCE_TYPE: 'g4dn.xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU
    },
    CREDIT_TYPE_3: {
        MAP_KEY_INSTANCE_TYPE: 'g4dn.xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU_GPU
    },
    CREDIT_TYPE_4: {
        MAP_KEY_INSTANCE_TYPE: 'g4dn.xlarge',
        MAP_KEY_FOLDING_TYPE: FOLDING_TYPE_CPU_GPU
    }
}


def getNodeSecurityGroup():
    return folding_config[REGION][SG_NODE]


def getSubnet(az):
    return folding_config[REGION][SUBNET][az]


def getFolderInstanceType(credit):
    return credit_map[credit][MAP_KEY_INSTANCE_TYPE]


def getFoldingConfigType(credit):
    return credit_map[credit][MAP_KEY_FOLDING_TYPE]

def getTableName():
    return os.environ['TABLE_NAME']
