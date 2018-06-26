# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Created on Tue May 23 09:52:49 2017

@author: skyksit
"""
import re
import os
import time

import logging
LOGGER = logging.getLogger('django')

from jandibot.settings import (
    IOSINFO
)

from apps.decorators import on_command

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

HELP_MSG = [
    '앱스토어에서 NS APP 의 정보를 가져옵니다 ',
    '!ios, !IOS 로 검색 가능합니다'
]

#envirment setting start
LOCAL_DRIVER_URL = 'D:/Anaconda3/envs/envscraping/Scripts/chromedriver.exe'
ITUNES_ADMIN_URL = "https://itunesconnect.apple.com/login"

# Create a new instance of the webBROWSER
CHROME_BIN = os.environ.get('GOOGLE_CHROME_SHIM', None)
if CHROME_BIN is not None:
    opts = ChromeOptions()
    opts.binary_location = CHROME_BIN
    opts.add_argument('headless')
    opts.add_argument("lang=ko_KR")
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    BROWSER = webdriver.Chrome(executable_path="chromedriver", chrome_options=opts)
else:
    BROWSER = webdriver.Chrome(LOCAL_DRIVER_URL)

NOW = time.localtime()
NOWTEXT = "%04d/%02d/%02d %02d:%02d:%02d" % (NOW.tm_year, NOW.tm_mon,
                                             NOW.tm_mday, NOW.tm_hour, NOW.tm_min, NOW.tm_sec)
BROWSER.get(ITUNES_ADMIN_URL)
WAIT = ui.WebDriverWait(BROWSER, 3)
#envirment setting end

def extract_info(info):
    str_id = ''
    str_password = ''
    list_info = info.split(',')
    str_id = list_info[0]
    str_password = list_info[1]
    return str_id, str_password

#go to application list Method
def goto_app_list():
    '''
    argument 와 return 은 없고 app list 를 보여주는 페이지로 이동하는 function
    '''
    WAIT.until(EC.presence_of_element_located((By.XPATH, "//a[@title='모든 애플리케이션']")))
    BROWSER.find_element_by_xpath("//a[@title='모든 애플리케이션']").click()

def main():
    '''
    access to itunes and send to jandi message
    '''
    list_webhook_data = []
    LOGGER.info("step1. get Id / password")
    str_id, str_password = extract_info(IOSINFO)
    LOGGER.info("step2. Itunes Login")
    #Login process
    try:
        #itunes login page는 script 로 내부 페이지를 그리는데 그 시간동안 기다려야 한다
        #wait 와 time.sleep 으로 강제 대기시간을 걸어놓음
        time.sleep(3)
        WAIT.until(EC.frame_to_be_available_and_switch_to_it
                   ((By.ID, "aid-auth-widget-iFrame")))
        BROWSER.find_element_by_xpath("//*[@id='account_name_text_field']").\
            send_keys(str_id)
        BROWSER.find_element_by_xpath("//*[@id='account_name_text_field']").send_keys(Keys.RETURN)
        time.sleep(2)
        BROWSER.find_element_by_id("password_text_field").send_keys(str_password)
        BROWSER.find_element_by_id("password_text_field").send_keys(Keys.RETURN)

        LOGGER.info("step3. get the Sale Info")
        #go to sales report page
        time.sleep(3)
        WAIT.until(EC.presence_of_element_located((By.XPATH, \
                                                   "//*[@id='main-nav']/div[1]/div[3]/a")))
        BROWSER.find_element_by_xpath("//*[@id='main-nav']/div[1]/div[3]/a").click()
        LOGGER.info("step3-1. click the Sale Info")
        WAIT.until(EC.presence_of_element_located((By.XPATH, "//td[@class='apple-id']")))
        app_ids = BROWSER.find_elements_by_xpath("//td[@class='apple-id']")
        app_names = BROWSER.find_elements_by_xpath\
            ("//td[@class='content']/ul/li/span[@class='title']")
        app_id_list = []
        app_name_list = []

        for idx, app_id in enumerate(app_ids):
            app_id_list.append(app_id.text)
        for idx, app_name in enumerate(app_names):
            app_name_list.append(app_name.text)

        for idx, app_id in enumerate(app_id_list):
            #app version
            v_appver_info = ""
            str_list_appinfo = []
            #total active apps count
            t_actappcnt = 0

            BROWSER.get("https://analytics.itunes.apple.com/#/metrics?"
                        "interval=r&datesel=d30&zoom=day&measure=rollingActiveDevices"
                        "&type=line&app=%s&view_by=3" % app_id_list[idx])
            WAIT.until(EC.presence_of_element_located((By.XPATH, "//tr[@ng-repeat]")))
            e_appvers = BROWSER.find_elements(By.XPATH, "//tr[@ng-repeat]")

            #sum active apps count
            for idx2, e_appver in enumerate(e_appvers):
                e_tmps = e_appver.find_elements_by_tag_name('td')
                t_actappcnt += int(re.sub("[^\d\.]", "", e_tmps[2].text))

            for idx2, e_appver in enumerate(e_appvers):
                e_tmps = e_appver.find_elements_by_tag_name('td')
                if idx2 == 4:
                    break
                if int(re.sub("[^\d\.]", "", e_tmps[2].text)) == 0:
                    continue
                iapprate = int(re.sub("[^\d\.]", "", e_tmps[2].text))*100 / t_actappcnt
                str_list_appinfo.append("app_ver : ")
                str_list_appinfo.append(e_tmps[1].text)
                str_list_appinfo.append(" - 활성화APP(30일내) :")
                str_list_appinfo.append(e_tmps[2].text)
                str_list_appinfo.append(" - 비율 : %0.1f%% \n" % iapprate)

            v_appver_info = "".join(str_list_appinfo)
            list_webhook_data.append({'title':app_name_list[idx], 'description': v_appver_info})

        LOGGER.info("step4. Send App info")
#       msg = u''+NOWTEXT+' itunes appstore 정보입니다'
    except TimeoutException as err:
        LOGGER.info(str(err))
    except Exception as err:
        LOGGER.info(str(err))
    else:
        LOGGER.info("~~~~~~~~~~~~~~~~~~~")
    finally:
        LOGGER.info("End Job")
        BROWSER.quit()
        return list_webhook_data

@on_command(['ios', 'IOS'])
def run(query):
    '''get to info of appstore NS apps'''
    title = u''+NOWTEXT+' itunes appstore 정보입니다'
    description = ''
    image = ''

    if query:
        description = '\n'.join(HELP_MSG)
    else:
        if len(query) > 1:
            description = '\n'.join(HELP_MSG)
        else:
            description = main()

    return title, description, image

if __name__ == '__main__':
    main()
