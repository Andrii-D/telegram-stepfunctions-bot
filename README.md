# Telegram bot on AWS Step Functions
Serverless Telegram bot made on 4 AWS Lambda chained by AWS Step Functions. All of this written on Serverless Framework using plugins.

This is an example on how to build a simple Telegram bot backend using AWS Lambda functions and AWS Dynamo DB to store messages and AWS Step Function to chain Lambdas.

## Deploying

1. Setup AWS credentials
2. Install Serverless Framework
3. Install two plugins: `serverless-step-functions` and `serverless-pseudo-parameters`
4. Clone this repo
5. Deploy: `sls deploy`

## Architecture

All messages from your Bot will come to the State Machine first.
State machine will invoke two Lambda function in parallel with same payload:
`log` - will just save payload to DynamoDB and `receive` - will parse the payload and check for the specific auth message.
`receive` will pass the result to the next state: `AuthOrNot` - which is not a Lambda function but just a decider. It will check the result of previous function and either invoke `authorize` or `respond` Lambda function.
`authorize` is aimed to send a callback to your website to authorize the user if needed. The `respond` function will just send a response to the chatbot.
