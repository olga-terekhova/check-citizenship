import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By


def get_credentials():
    f = open('cred.config')
    data = json.load(f)
    # print(data)
    cred_dict = []
    for i in data['credentials']:
        # print(i)
        cred_dict.append(i)
    f.close()
    return cred_dict


def check_status_person(credentials):
    # print(credentials['login'])
    # print(credentials['password'])
    print('\n\n' + credentials['name'])
    service = Service('C:/Users/terem/Downloads/chromedriver_win32/chromedriver.exe')
    service.start()

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Remote(service.service_url, options=chrome_options)
    driver.get('https://cst-ssc.apps.cic.gc.ca/en/login')

    # wait for the Sign in button element to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("xpath", "//button[text()[contains(., 'Sign into your tracker account')]]"))
        )
        button_element = driver.find_element("xpath", "//button[text()[contains(., 'Sign into your tracker account')]]")
        print(button_element.text)
        time.sleep(2)
        driver.execute_script("arguments[0].scrollIntoView();", button_element)
        time.sleep(2)
        button_element.click()
        time.sleep(2)

    except TimeoutException:
        print('Timeout')
        return

    # wait for the UCI element to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("id", "uci"))
        )
        login_element = driver.find_element('id', 'uci')
        login_element.send_keys(credentials['login'])
    except TimeoutException:
        print("Timeout")
        # driver.quit()
        return

    # wait for the Password element to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("id", "password"))
        )
        pwd_element = driver.find_element('id', 'password')
        pwd_element.send_keys(credentials['password'])
    except TimeoutException:
        print("Timeout")
        # driver.quit()
        return

    # wait for the Submit button element to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(("xpath", "//button[text()[contains(., 'Sign in')]]"))
        )
        submit = driver.find_element("xpath", "//button[text()[contains(., 'Sign in')]]")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        time.sleep(2)
        submit.click()
    except TimeoutException:
        print("Timeout")
        # driver.quit()
        return

    # wait for the last updated date block to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("xpath", "//dd[contains(@class,'date-text')]"))
        )
        last_updated = driver.find_element("xpath", "//dd[contains(@class,'date-text')]").text
        # parent = app_status_header.find_element("xpath", "..")
        # times = parent.find_elements("tag name", "time")
        # last_updated = times[0].text
        print(last_updated)
    except TimeoutException:
        print("Timeout")
        # driver.quit()
        return

    # wait for the Activities block to appear
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("xpath", "//li[@class='activity']"))
        )
        activities = driver.find_elements("xpath", "//li[@class='activity']")
        for acti in activities:
            activity_date = acti.find_element("xpath", ".//div[@class='date']")
            activity_title = acti.find_element("xpath", ".//div[@class='activity-title']")
            activity_text = acti.find_element("xpath", ".//p[@class='activity-text']")
            print(activity_date.text, '-', activity_title.text, '-', activity_text.text)
    except TimeoutException:
        print("Timeout")
        # driver.quit()
        return


def check_status_all():
    for i in get_credentials():
        if i['check'] == 'TRUE':
            check_status_person(i)
    # check_status_person(get_credentials()[0])


check_status_all()
