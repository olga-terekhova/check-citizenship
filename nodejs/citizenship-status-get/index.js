const AWS = require('aws-sdk');
const puppeteer = require("puppeteer-core");
const chromium = require("@sparticuz/chromium");
const BUCKET_NAME = process.env.bucket_name;  // name of the AWS S3 bucket to store configs and results
const PROJECT_PATH = 'projects/citizenship/'; // path in the S3 bucket to the project directory 

async function save_screenshot(elem, filename, isPage){
    var s3 = new AWS.S3();
    var key_name = PROJECT_PATH + 'output/' + filename;
    let screenshot;
    if (isPage == true) {
        screenshot = await elem.screenshot({fullPage: true});
    }
    else {screenshot = await elem.screenshot();}
    const params = { Bucket: BUCKET_NAME, Key: key_name, Body: screenshot };
    await s3.putObject(params).promise();
}

async function save_page(page, filename){
    var s3 = new AWS.S3();
    var key_name = PROJECT_PATH + 'output/' + filename;
    let dumpHTML = await page.content();
    const params = { Bucket: BUCKET_NAME, Key: key_name, Body: dumpHTML };
    await s3.putObject(params).promise();
    
}

async function save_json(str, filename){
    var s3 = new AWS.S3();
    var key_name = PROJECT_PATH + 'output/' + filename;
    const params = { Bucket: BUCKET_NAME, Key: key_name, Body: str };
    await s3.putObject(params).promise();
}

async function checkPerson (event) {
    var chat_id = event.chat.chat_id;
    var credPerson = event.cred;
    var namePerson = credPerson.name;
    var loginPerson = credPerson.login;
    var passwordPerson = credPerson.password;
    
    var res;
    let browser;
    let page;

    try {
        browser = await puppeteer.launch({
          args: chromium.args,
          defaultViewport: chromium.defaultViewport,
          executablePath: await chromium.executablePath,
          headless: chromium.headless,
          ignoreHTTPSErrors: true,
        });
        page = await browser.newPage();
        page.setViewport({width: 1500, height: 1080});
        
    }
    catch (e){
        console.log(e);
        console.log("Error");
        if ('output' in event) { 
            if (event['output'] == 'bot'){
               let payloadParams =  event ;
               payloadParams["result"] = {"success": "no", "text" : "Error checking. Browser not created."};

               let lambdaParams = {
                   FunctionName: 'citizenship-status-bot-send', 
                   InvocationType: 'Event', 
                   Payload: JSON.stringify(payloadParams),
               };
               let lambda = new AWS.Lambda();
               let lambdaResult = await lambda.invoke(lambdaParams).promise();
            }
        }
        return "fail";
    }
   
        
    try{
        await page.goto("https://tracker-suivi.apps.cic.gc.ca/en/login", { waitUntil: 'networkidle2' });
        await save_screenshot(page, 'log/'+ chat_id + '/step1'+loginPerson+'.png', true);
        await save_page(page, 'log/'+ chat_id + '/step1' + loginPerson + '.html');
        
        const uci = await page.waitForSelector('#uci');
        await uci.type(loginPerson);
        const password = await page.waitForSelector('#password');
        await password.type(passwordPerson);
        const submitButton = await page.waitForXPath("//button[text()[contains(., 'Sign in')]]");
        await submitButton.click({waitUntil: 'domcontentloaded'});
        
        const lastUpdateDateEl = await page.waitForXPath("//dd[contains(@class,'date-text')]");
        await save_screenshot(page, 'log/'+ chat_id + '/step3'+ loginPerson+'.png', true);
        await save_page(page, 'log/'+ chat_id + '/step3' + loginPerson + '.html');
        
        let lastUpdateDateVal = await (await lastUpdateDateEl.getProperty('textContent')).jsonValue();
        const lastUpdateDate = lastUpdateDateVal.trim();
        
        let result_person = {name: namePerson, login:loginPerson, status: "ok",  lastUpdateDate: lastUpdateDate};
        res = JSON.stringify(result_person);
        
        await save_screenshot(page, 'timeline-pic/'+ chat_id + '/' + loginPerson +'.png', true);
        let screenshot_path = PROJECT_PATH + 'output/' + 'timeline-pic/'+ chat_id + '/' + loginPerson +'.png';
        await save_json(res, 'timeline-text/' + chat_id + '/' + loginPerson + '.json');
        
        
        // SEND PAGE SCREENSHOT TO BOT
        if ('output' in event) { 
            if (event['output'] == 'bot'){
               let payloadParams =  event ;
               payloadParams["result"] = {"success": "yes", "text" :  result_person['lastUpdateDate'] , "image": { "key": screenshot_path, "bucket":BUCKET_NAME }};
               let lambdaParams = {
                   FunctionName: 'citizenship-status-bot-send', 
                   InvocationType: 'Event', 
                   Payload: JSON.stringify(payloadParams),
               };
               console.log(lambdaParams);
               let lambda = new AWS.Lambda();
               let lambdaResult = await lambda.invoke(lambdaParams).promise();
            }
        }
        
    }
    catch (e){
        console.log(e);
        console.log("Error");
        res = {name: namePerson, login: loginPerson, status: "error"};
        await save_screenshot(page, 'log/'+ chat_id + '/error'+ loginPerson+'.png', true);
        let screenshot_path = PROJECT_PATH + 'output/' + 'log/'+ chat_id + '/error'+ loginPerson+'.png';
        
        // SEND INFO ABOUT ERROR TO BOT
        if ('output' in event) { 
            if (event['output'] == 'bot'){
               let payloadParams =  event ;
               payloadParams["result"] = {"success": "no", "text" : "Error checking. Make sure credentials are valid and try checking manually in a browser.", "image": { "key": screenshot_path, "bucket":BUCKET_NAME }};
               let lambdaParams = {
                   FunctionName: 'citizenship-status-bot-send', 
                   InvocationType: 'Event', 
                   Payload: JSON.stringify(payloadParams),
               };
               let lambda = new AWS.Lambda();
               let lambdaResult = await lambda.invoke(lambdaParams).promise();
    
                
            }
        }
    }
    finally {
        await browser.close();
    }
    return res;
}


exports.handler = async (event) => {
    return await checkPerson(event);
}; 
