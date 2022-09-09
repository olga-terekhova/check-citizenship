import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.by import By

def get_credentials():
    f = open('cred.config')
    data = json.load(f)
    #print(data)
    cred_dict = []
    for i in data['credentials']:
        #print(i)
        cred_dict.append(i)
    f.close()
    return cred_dict

def check_status_person(credentials):
    print(credentials['login'])
    print(credentials['password'])
    service = Service('C:/Users/terem/Downloads/chromedriver_win32/chromedriver.exe')
    service.start()
    driver = webdriver.Remote(service.service_url)
    driver.get('https://cst-ssc.apps.cic.gc.ca/en/login')
    time.sleep(5)  # Let the user actually see something!
    login_element = driver.find_element('id', 'uci-input')
    login_element.send_keys(credentials['login'])
    time.sleep(1)
    pwd_element = driver.find_element('id', 'password-input')
    pwd_element.send_keys(credentials['password'])
    submit = driver.find_element('id', 'sign-in-submit-btn')
    submit.click()
    time.sleep(5)
    app_history = driver.find_element("xpath", "//h2[text()='Application history']")
    grandparent = app_history.find_element("xpath","../..")
    #print(grandparent.tag_name)
    times = grandparent.find_elements("tag name", "time")
    #print(times[0].tag_name)
    #print(len(times))
    for t in times:
        if t.value_of_css_property("white-space") == 'nowrap':
            print(t.text)
            print(t.get_attribute('datetime'))
            grandparent_time = t.find_element("xpath", "../..")
            status = grandparent_time.find_element("tag name", "h3")
            print(status.text)
    time.sleep(5)  # Let the user actually see something!

    # get status


    driver.quit()

def check_status_all():
    #for i in get_credentials():
    #    check_status_person(i)
    check_status_person(get_credentials()[0])

check_status_all()