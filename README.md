# check-citizenship
Automated checking for updates in citizenship tracking


## Installation on AWS

1. S3 bucket: config
2. Create two Lambda functions: citizenship-status-get and citizenship-status-email. Paste their code from nodejs directory. 
3. The function citizenship-status-get should have two layers:
  1. chromium.zip from https://github.com/Sparticuz/chromium/actions (version 107) uploaded to S3.
  2. install puppeteer-core locally (npm install --save puppeteer-core@18.1.0), zip up the nodejs folders and upload to S3. 
4. Execution role and policies:
5. Schedule citizenship-status-get in EventBridge. 
