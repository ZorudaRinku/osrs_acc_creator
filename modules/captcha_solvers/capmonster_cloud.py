"""
Solves and returns the captcha answer via the capmonster.cloud service
Documentation: https://zennolab.atlassian.net/wiki/spaces/APIS/pages/33076/API+Methods
Requirements: pip install requests, json
"""
import sys
import time
import requests
import json
try:
    from modules.helper_modules.utility import get_site_settings, get_user_settings
except ImportError as error:
    print(error)

SITE_URL = get_site_settings()[1]
SITE_KEY = get_site_settings()[0]  # osrs site key
API_KEY = get_user_settings()[3]  # api key read from settings.ini

def capmonster_solver():
    """Solves repcatcha via Capmonster service"""
    print("Solving captcha, please wait...")
    createTaskJson = \
        {
            "clientKey": API_KEY,
            "task":
                {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": SITE_URL,
                    "websiteKey": SITE_KEY
                }
        } #Create json that will submit the recaptcha to Capmonster
    getTaskJson = \
        {
            "clientKey": API_KEY,
            "taskId": ""
        } #Create json that will retrieve the key from the task submitted prior
    while True:
        try:
            createTaskResponse = json.loads(requests.post("https://api.capmonster.cloud/createTask", json=createTaskJson).text) #Submit the recaptcha to Capmonster
            error = createTaskResponse["errorId"]
            taskId = createTaskResponse["taskId"]

            if error == "ERROR_RECAPTCHA_TIMEOUT": #Check if recaptcha has timed out
                print("Recaptcha timeout")
                return True

            getTaskJson["taskId"] = taskId
            for i in range(40): #Check to see if captcha is ready, if not loop for a maximum of 40 times (Capmonster limit).
                getTaskResponse = json.loads(
                    requests.post("https://api.capmonster.cloud/getTaskResult", json=getTaskJson).text) #Request from capmonster the recaptcha solved key
                if getTaskResponse["status"] == "ready":
                    print('Captcha solved. Continuing.')
                    response = getTaskResponse["solution"]["gRecaptchaResponse"]
                    return response, False
                else:
                    time.sleep(3) #Sleep if captcha is not solved.
            else:
                print("Exceeded request limit while trying to solve captcha")
                return True
        except Exception as e:
            print(e)
            print("Unexpected Error")
            return True
