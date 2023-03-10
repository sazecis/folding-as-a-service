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

### CPU

Selecting credit 1 or 3 will create you an EC2 Spot instance only with CPU available for folding.

### GPU

Selecting credit 5 or 10 will crete you an EC2 Spot instance with CPU and GPU capable foldings.

## Seeing the results

To see your folding result you will need to look up the public IP address of your EC2 instance.

### Management console

On the daschboard of EC2 you can search for a running instance with the same name as the following: `folding.S.symbiote.<arbitrary user name>`. The `<arbitrary user name>` was provided by you at `StepFunction` start.
Select the instance and on the `Details` tab look for the `Public IPv4 address` value. Copy the IP to the clipboard.
In a new browser tab past the copied IP into the address bar and add port `7396` to it:
```
x.x.x.x:7396
```
And that's it you will see the Folding@home up and running.

## Troubleshooting

### MaxSpotInstanceCountExceeded - no available g4 instances
It might be that you need to request a quota increase for your **g4** instances when your StepFunction stucks in the __init__ section. Do that from your AWS Management Console by searching for **ServiceQuotas** or go at: <https://console.aws.amazon.com/servicequotas> url. Remember to select the region where you want your quota to be increased.
Request an increase to **20** at __Amazon Elastic Compute Cloud (Amazon EC2)__ for: **All G and VT Spot Instance Requests**.

### AWSServiceRoleForEC2Spot - missing
It might be that in your account you never worked before with spot instances and the service-linked role required is not yet created and you get for your `start` lambda the following error:
`An error occurred (AuthFailure.ServiceLinkedRoleCreationNotPermitted) when calling the RunInstances operation: The provided credentials do not have permission to create the service-linked role for EC2 Spot Instances.`
Solution run from your AWS CLI:
```
aws iam create-service-linked-role --aws-service-name spot.amazonaws.com
```
#### Or to create AWSServiceRoleForEC2Spot using the console:
Open the IAM console at https://console.aws.amazon.com/iam/.
- In the navigation pane, choose Roles.
- Choose Create role.
- On the Select type of trusted entity page, choose EC2, EC2 - Spot Instances, Next: Permissions.
- On the next page, choose Next:Review.
- On the Review page, choose Create role.