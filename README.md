# check-citizenship
Automated checking for updates in Canadian citizenship application tracking (https://tracker-suivi.apps.cic.gc.ca/en/login).


## Installation on AWS

1. Create an S3 bucket.
2. Upload files to S3 bucket:
   - nodejs/layers/chromium.zip (source: https://github.com/Sparticuz/chromium/actions (version 107))
   - nodejs/layers/puppeteer-core.zip (source: installed puppeteer-core locally, npm install --save puppeteer-core@18.1.0)
   - py-code/layers/python-requests.zip (source: installed requests locally)
3. Create 3 Lambda function layers based on the files.
4. Create 3 Python Lambda functions:
   - citizenship-status-bot (code in py-code/citizenship-status-bot)
   - citizenship-status-bot-send (code in py-code/citizenship-status-bot-send)
   - citizenship-status-subscribed (code in py-code/citizenship-status-subscribed)
5. Put the S3 bucket name as an environment variable for functions. 
5. Attach python-requests layer to all Python functions.
6. Create a nodejs Lambda function:
   - citizenship-status-get (code in nodejs/citizenship-status-get)
7. Set up IAM policies:
   - Lambda functions to have access to S3 bucket
   - Lambda functions to be able to invoke each other
8. Set up inbound API for citizenship-status-bot.
9. Set up a new telegram bot. Define the AWS API in the bot. Put the bot's token as an environment variable for citizenship-status-bot and citizenship-status-bot-send.
10. Schedule citizenship-status-subscribed in EventBridge. 
