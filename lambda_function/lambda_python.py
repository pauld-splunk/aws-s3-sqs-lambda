'''  Copyright 2020 Paul Davies

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.'''


import json
import boto3
import os
sqs = boto3.client('sqs')
def lambda_handler(event, context):
    
    sqs_records = event["Records"]

    try:
        blacklist=json.loads(os.environ['BLACKLIST'])
    except:
        blacklist=[]

    for payload_record in sqs_records:
        
        body = json.loads(payload_record['body']) 

        message = json.loads(body['Message'])

        s3_records = message["Records"]


        for s3_record in s3_records:
            mykey = s3_record["s3"]["object"]["key"]
            arn = s3_record["s3"]["bucket"]["arn"]

            skip=0
            for item in blacklist:
                if (item in mykey):
                    skip=1
                    print(f'Not forwarding object <{mykey}> from bucket <{arn}> as it is in blacklist')
                    
            
            if ("CloudTrail" in mykey):
                forwardQueue = sqs.get_queue_url(QueueName=os.environ['CloudTrailQueueName'])
            elif ("Config" in mykey):
                forwardQueue = sqs.get_queue_url(QueueName=os.environ['ConfigQueueName'])
            elif ("vpcflowlogs" in mykey):
                forwardQueue = sqs.get_queue_url(QueueName=os.environ['vpcflowlogsQueueName'])
            else:
                forwardQueue = sqs.get_queue_url(QueueName=os.environ['defaultQueueName'])
            
            if skip!=1:
                forwardQueueUrl = forwardQueue['QueueUrl']
                sqs.send_message(QueueUrl=forwardQueueUrl, MessageBody=(json.dumps(body)))


 