# Folding as a Service
This SAM template is an open-source solution for running the Folding@home project on AWS, using EC2 spot instances for both CPU and GPU processing. The solution is designed to allow individuals and organizations to contribute their unused AWS credits or compute resources to the project, and make a difference in the fight against diseases.

## Prerequisites
Before deploying this SAM template, you will need to have the following tools installed on your local machine:

- [AWS CLI](https://aws.amazon.com/cli/)
- [SAM CLI](https://aws.amazon.com/serverless/sam/)

You will also need to configure your AWS credentials locally, by running `aws configure` and entering your Access Key and Secret Key.

## Deployment
To deploy the Folding as a Service SAM template, run the following commands:

Build
```
sam build
```

First time deploy creating a configuration file storing the settings of the stack
```
sam deploy --capabilities CAPABILITY_NAMED_IAM --guided --parameter-overrides ParameterKey=MyIp,ParameterValue=<MyIp CIDR range>
```

Deploy
```
sam deploy --capabilities CAPABILITY_NAMED_IAM --parameter-overrides ParameterKey=MyIp,ParameterValue=<MyIp CIDR range>
```

The `--capabilities CAPABILITY_NAMED_IAM` flag is necessary to allow the SAM template to create and manage IAM roles and policies during the deployment process.

After the deployment is complete, you can go to the AWS Management Console and look for the __FoldingStateMachine__ at the Step Functions AWS service. Click on the link to open the state machine, and then click on the "Start execution" button. This will open a dialog where you can provide an input JSON document in the following format:

```
{
  "Credit": "<1 | 3 | 5 | 10>",
  "User": "<arbitrary user name>"
}
```

The **"Credit"** field determines the amount of money you want to spend on the __Folding@home__ project (use one of the predifined ones), and the **"User"** field is an arbitrary name that you can use to identify your contributions. Once you have provided the input JSON, click **Start execution** to start the folding process.

Please note that you need to provide the input json document at the start of each execution.

## Troubleshooting

### MaxSpotInstanceCountExceeded - no available g4 instances
It might be that you need to request a quota increase for your **g4** instances when your StepFunction stucks in the __init__ section. Do that from your AWS Management Console by searching for **ServiceQuotas** or go at: (console.aws.amazon.com/servicequotas)
Request an increase to **20** at __Amazon Elastic Compute Cloud (Amazon EC2)__ for: **All G and VT Spot Instance Requests**.
