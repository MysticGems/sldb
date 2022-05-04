This is intended as a replacement for the SL Experience key-value store, using AWS resources and accessible via https. It's not as secure, and slower, but it does work on land where an Experience hasn’t been enabled. It should be possible to run all but very popular services on the [AWS free tier](https://aws.amazon.com/free/), but it is always a good idea to set up a [billing alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) to avoid unpleasant surprises.

# Components

## `sl/library.lsl`

Example LSL script fragments demonstrating use. Returned values from the http call are formatted like the returned values from an Experience to facilitate use as a drop-in replacement.

## `aws/lambda_function.py`

This is the Python Lambda function that handles the https request, queries the database, and returns the results.

## `aws/template.yml`

AWS CloudFormation template to build the necessary resources, including the database.

# Use

Run the CloudFormation template in your AWS account. It will build a Lambda, DynamoDB table, and necessary IAM and logging resources. You will need to provide a 20-128 character secret value. Make note of this and of the URL that is assigned to your Lambda function.

Incorporate the contents of `library.lsl` into your LSL script(s). You will need to provide the URL and secret value in the script (as `SECURE_HEADER_VALUE` and `SLDB_URL` in the example). Make sure to set your script as no-mod to protect the secret value from discovery.

The service is meant to operate as much as possible like the Experience key-value store, so results will be returned as HTTP 200s with comma delimited lists as for [llReadKeyValue()](https://wiki.secondlife.com/wiki/LlReadKeyValue) and [llUpdateKeyValue()](https://wiki.secondlife.com/wiki/LlUpdateKeyValue).

The size of values is limited to 4095 characters; maximum length of keys is 1011 characters. Table size is subject only to the [AWS limits](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html).