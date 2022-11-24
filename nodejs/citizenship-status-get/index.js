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

async function checkPerson (credPerson) {
    var namePerson = credPerson.name;
    var loginPerson = credPerson.login;
    var passwordPerson = credPerson.password;
    
    var res;
    let browser;

    try {
        browser = await puppeteer.launch({
          args: chromium.args,
          defaultViewport: chromium.defaultViewport,
          executablePath: await chromium.executablePath,
          headless: chromium.headless,
          ignoreHTTPSErrors: true,
        });
        const page = await browser.newPage();
        await page.goto("https://cst-ssc.apps.cic.gc.ca/en/login", { waitUntil: 'networkidle2' });
        await save_screenshot(page, 'log/step1'+namePerson+'.png', true);
        await save_page(page, 'log/step1' + namePerson + '.html');
        
        
        const signInButton = await page.waitForXPath("//button[text()[contains(., 'Sign into your tracker account')]]");
        await signInButton.click( {waitUntil: 'domcontentloaded'});
        await save_screenshot(page, 'log/step2'+ namePerson+'.png', true);
        await save_page(page, 'log/step2' + namePerson + '.html');
        
        const uci = await page.waitForSelector('#uci');
        await uci.type(loginPerson);
        const password = await page.waitForSelector('#password');
        await password.type(passwordPerson);
        const submitButton = await page.waitForXPath("//button[text()[contains(., 'Sign in')]]");
        await submitButton.click({waitUntil: 'domcontentloaded'});
        
        const lastUpdateDateEl = await page.waitForXPath("//dd[contains(@class,'date-text')]");
        await save_screenshot(page, 'log/step3'+ namePerson+'.png', true);
        await save_page(page, 'log/step3' + namePerson + '.html');
        
        let lastUpdateDateVal = await (await lastUpdateDateEl.getProperty('textContent')).jsonValue();
        const lastUpdateDate = lastUpdateDateVal.trim();
        
        var activities = await page.$x("//li[@class='activity']");
        let result_activities = [];
         for (let acti in activities){
            let acti_element = activities[acti];
            const acti_date_el = await page.evaluate( (el) =>  {
                let elements = el.getElementsByClassName('date');
                let result = '';
                if(elements.length>0) {
                    result = elements[0].textContent.trim();
                }
                return result;
            }, acti_element);
            const acti_status_el = await page.evaluate( (el) =>  {
                let elements = el.getElementsByClassName('activity-title');
                let result = '';
                if(elements.length>0) {
                    result = elements[0].textContent.trim();
                }
                return result;
            }, acti_element);
            const acti_text_el = await page.evaluate( (el) =>  {
                let elements = el.getElementsByClassName('activity-text');
                let result = '';
                if(elements.length>0) {
                    result = elements[0].textContent.trim();
                }
                return result;
            }, acti_element);
            let acti_object = {activity_date: acti_date_el, activity_status: acti_status_el, activity_text: acti_text_el};
            result_activities.push(acti_object);
        }
        let result_person = {name: namePerson, status: "ok",  lastUpdateDate: lastUpdateDate, timeline: result_activities};
        res = JSON.stringify(result_person);
        
        let res_area = await page.$x("//section[@class='application-history-container']"); 
        await save_screenshot(res_area[0], 'timeline-pic/'+namePerson+'.png', false);
        await save_json(res, 'timeline-text/' + namePerson + '.json');
    }
    catch (e){
        console.log(e);
        console.log("Error");
        res = {name: namePerson, status: "error"};
    }
    finally {
        await browser.close();
    }
    return res;
}

async function checkPeople (event) {
    var s3 = new AWS.S3();
    let contentFile;
    let response='';
    try {
        const file = await s3
         .getObject({ Bucket: BUCKET_NAME, Key: PROJECT_PATH + 'config/cred.config' })
         .promise();
        contentFile = file.Body.toString();
        let credFile = JSON.parse(contentFile);
        let credentials = credFile.credentials;
        let results = [];
        let namelist = [];
        for (let cred in credentials){
            if (credentials[cred].check == 'TRUE') {
                results.push(await checkPerson(credentials[cred]));
                namelist.push(credentials[cred].name);
            }
        } 
        
        response = {
            statusCode: 200,
            body: results,
            };
            
        
            
        if ('output' in event) { 
            console.log('output in event');
            if (event['output'] == 'bot'){
               console.log('output bot');
               let payloadParams =  event['chat'] ;
               payloadParams["credlist"] = namelist;

               let lambdaParams = {
                   FunctionName: 'citizenship-status-bot-send', 
                   InvocationType: 'Event', 
                   Payload: JSON.stringify(payloadParams),
               };
               console.log(lambdaParams);
               let lambda = new AWS.Lambda();
               //lambda.invoke(lambdaParams);
               let lambdaResult = await lambda.invoke(lambdaParams).promise();
    
                
            }
        }
        else {
           let lambdaParams = {
               FunctionName: 'citizenship-status-email',
               InvocationType: 'Event',
               };
           let lambda = new AWS.Lambda();
           console.log('Not bot - stub for email');
           const lambdaResult = await lambda.invoke(lambdaParams).promise();
           
           
        }
        
    } catch (err) {
        response = {
            statusCode: 500,
            body: err,
        };
    }
    return response;
}

exports.handler = async (event) => {
    return await checkPeople(event);
}; 
