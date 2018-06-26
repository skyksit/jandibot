# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import os
import time
import socket
import errno
import logging
LOGGER = logging.getLogger('django')

from jandibot.settings import (
    IOSINFO
)

from selenium import common
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

#envirment setting start
LOCAL_DRIVER_URL = 'D:/Anaconda3/envs/envscraping/Scripts/chromedriver.exe'
ITUNES_ADMIN_URL = "https://itunesconnect.apple.com/login"

# Create a new instance of the webBROWSER
CHROME_BIN = os.environ.get('GOOGLE_CHROME_SHIM', None)

def extract_info(info):
    str_id = ''
    str_password = ''
    list_info = info.split(',')
    str_id = list_info[0]
    str_password = list_info[1]
    return str_id, str_password

@sched.scheduled_job('cron', hour='8-18', minute='0,10,20,30,40,50')
def main():
    list_webhook_data = []
    
    NOW = time.localtime()
    NOWTEXT = "%04d/%02d/%02d %02d:%02d:%02d" % (NOW.tm_year, NOW.tm_mon,
                                                 NOW.tm_mday, NOW.tm_hour, NOW.tm_min, NOW.tm_sec)
    print("NOW = {0}".format(NOWTEXT))
    print("CHROME_BIN = {0}".format(CHROME_BIN))
    

    BROWSER = None
    while not BROWSER:
        try:
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
        except common.exceptions.WebDriverException:
            time.sleep(5)

    try:
        BROWSER.get(ITUNES_ADMIN_URL)
        WAIT = ui.WebDriverWait(BROWSER, 10)
        
        print("step1. get Id / password")
        str_id, str_password = extract_info(IOSINFO)
        print("step2. Itunes Login")
    
        time.sleep(5)
        WAIT.until(EC.frame_to_be_available_and_switch_to_it
                   ((By.ID, "aid-auth-widget-iFrame")))
        BROWSER.find_element_by_xpath("//*[@id='account_name_text_field']").\
            send_keys(str_id)
        BROWSER.find_element_by_xpath("//*[@id='account_name_text_field']").send_keys(Keys.RETURN)
        time.sleep(5)
        BROWSER.find_element_by_id("password_text_field").send_keys(str_password)
        BROWSER.find_element_by_id("password_text_field").send_keys(Keys.RETURN)
    
        print("step3. get the Sale Info")
        time.sleep(5)
        WAIT.until(EC.presence_of_element_located((By.XPATH, \
                                                   "//*[@id='main-nav']/div[1]/div[3]/a")))
        BROWSER.find_element_by_xpath("//*[@id='main-nav']/div[1]/div[3]/a").click()
    
        print("step3-1. click the Sale Info")
    
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
            time.sleep(10)
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

        print("step4.list_webhook_data = {0}".format(list_webhook_data))
    except socket.error as e:
        if e.errno != errno.ECONNRESET:
        # Handle the exception...
            print("Connection reset")
        else:
            raise
    finally:
        time.sleep(10)
        BROWSER.quit()

sched.start()