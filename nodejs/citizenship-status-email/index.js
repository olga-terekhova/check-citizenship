var AWS = require("aws-sdk");
var ses = new AWS.SES({ region: "ca-central-1" });
var emailAddress = process.env.email;
const BUCKET_NAME = process.env.bucket_name;  // name of the AWS S3 bucket to store configs and results
const PROJECT_PATH = 'projects/citizenship/'; // path in the S3 bucket to the project directory 

exports.handler = async function (event) {  
  var s3 = new AWS.S3();
  let S3_params_text = { Bucket: BUCKET_NAME, Delimiter: '/', Prefix: PROJECT_PATH + 'output/timeline-text/' };
  const listKeysText = await s3.listObjectsV2(S3_params_text).promise();
  
  let keysTextContents = listKeysText.Contents;
  let str_update = '';
  
  for (let t in keysTextContents){
    let key = keysTextContents[t].Key;
    let file = await s3
         .getObject({ Bucket: BUCKET_NAME, Key: key })
         .promise();
        let contentFile = file.Body.toString();
        let jsonResult = JSON.parse(contentFile);
        str_update+=(jsonResult.name + ': ' + jsonResult.lastUpdateDate + ' | ');
        
  }
  console.log(str_update);
  
  var params = {
    Destination: {
      ToAddresses: [emailAddress],
    },
    Message: {
      Body: {
        Text: { Data: "Citizenship Tracker Update - " + str_update },
      },

      Subject: { Data: "Citizenship Tracker Update - " + str_update },
    },
    Source: emailAddress,
  };
  let emailSent = ses.sendEmail(params).promise();
  return "ok";
  
};