# Setup Instructions

**Pre-Requisites**
Set-up the Splunk Add-On for Amazon Web Services as per documentation https://docs.splunk.com/Documentation/AddOns/released/AWS/Description. Make sure the AWS policy and roles have been created to allow the Add-on by minimum access to your SQS and AWS S3 bucket. Instructions for this are here - 
https://docs.splunk.com/Documentation/AddOns/latest/AWS/ConfigureAWS
https://docs.splunk.com/Documentation/AddOns/released/AWS/ConfigureAWSpermissions

You will also need to ensure that the Add-On is ready to create new inputs, so please configure the settings as described here:
https://docs.splunk.com/Documentation/AddOns/released/AWS/Setuptheadd-on


**Stage 1: Initial S3 Bucket configuration**

1) Create a new S3 Bucket, or select an existing bucket that where the logs will be written. (Make a note of the bucket name for later for step 3)

2) Create a new SNS topic (make note of the ARN for the next step)

3) Edit the SNS Policy - replace it with with the one below (changing the "SNS-topic-ARN" and "bucket-name" to the relevant ones from steps 1 & 2)

<pre>
{
	"Version": "2008-10-17",
	"Id": "example-ID",
	"Statement": [
				{"Sid": "example-statement-ID",
				 "Effect": "Allow",
				 "Principal": {"AWS":"*" },
				 "Action": ["SNS:Publish"],
				 "Resource": "SNS-topic-ARN",
				 "Condition": {"ArnLike": { "aws:SourceArn": "arn:aws:s3:*:*:bucket-name" }}
				}]
}
</pre>

4) Return to S3 selecting the properties of the Bucket, and navigate to the "Events" options. Create a new notification. Select the action as "All object create events", and send a notification via SNS to the one created above in step 2.

5) Create a new SQS Queue - name it with ending DLQ (e.g. my-bucket-sqs-dlq) - use all other default settings

6) Create another SQS Queue naming it same as above without dlq. Use all defaults, but now select the checkbox "Use Redrive policy" and select the dlq created above. Set retry as 500.

7) Subscribe the new SQS Queue (not the DLQ one) to the SNS Topic created in step 2


**Stage 2: Set up routing SQS queues**

You will need to create SQS queues for each of the sources of logs in the S3 Bucket. For example, if you may have CloudTrail, Config, S3 Access logs and VPC Flow logs going into the bucket, you will need to repeat these steps for each source. You may also want to set a default SQS queue to capture any logs that are not categorised.

1) Create a new SQS Queue - name it with ending DLQ (e.g. my-CloudTrail-sqs-dlq) - use all other default settings for the queue

2) Create another SQS Queue naming it same as above without dlq. Use all defaults, but now select the checkbox "Use Redrive policy" and select the dlq created above. Set retry as 500.

Repeat steps 1 and 2 for each of the sources

**Stage 3: Setup Lambda Function**

1) Create a new Lambda Function (Author from scratch), using Python 3.8 Runtime, default permissions
2) Copy the sample function into the inline editor
3) Navigate to the function permissions, and open the execution role / edit it
4) In addition to the policies already assigned by default, edit the policy and ensure that the role has permissions to do the following:
- Required permissions for SQS: GetQueueUrl, ReceiveMessage, DeleteMessage, GetQueueAttributes, ListQueues, SendMessage, SendMessageBatch
5) On the Lambda configuration, click Add Trigger, and select SQS. In the drop down, select the SQS queue created in Stage 1, step 6 

**Stage 4: Setup Lambda Function Environment variables**

These instructions are for the specific settings already defined in the function example. If you change the template, then these will of course change.

1) In the environment variables section for the function, add the following variables:


<table><tr><td><strong>Variable</strong></td><td><strong>Value</strong></td></tr>
<tr><td>EXCLUDELIST</td><td>Enter a list of objects or partial names to not read into Splunk. The format of this should be as follows: ["object1","object2"] where object1 and object2 are the names/partial names of the object keys to exclusion list. Make sure that the names are in double quotes, and in a list with square brackets. If no exclusion is needed, do not set this variable </td></tr>
<tr><td>CloudTrailQueueName</td><td>Name of the SQS queue set up in Stage 2 for CloudTrails</td></tr>
<tr><td>ConfigQueueName</td><td>Name of the SQS queue set up in Stage 2 for Config</td></tr>
<tr><td>vpcflowlogsQueueName</td><td>Name of the SQS queue set up in Stage 2 for vpc flow logs</td></tr>
<tr><td>defaultQueueName</td><td>Name of the SQS queue set up in Stage 2 for any other logs not matching any of the others above</td></tr>
</table>

**Stage 5: Setup the inputs on your Splunk Add-on for AWS**

Follow the instructions in the Splunk documentation to add new inputs for the queues set up in Step 2. Ensure that the sourcetypes are set appropriately to the sourcetype being ingested.


Your function should now be ready to execute.



