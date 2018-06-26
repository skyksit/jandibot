# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
@author: skyksit
"""
import os
import re
import time
import random
import requests

from apps.decorators import on_command
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions

HELP_MSG = [
    'giphy 에서 smile 키워드로 검색하고 싶으면 \'/ns !움짤 smile\' 이라고 해주세요.',
    '검색어는 `영어`와 `한글` 둘 다 됩니다. 한글은 파파고에서 영어로 전환해서 찾아줍니다',
    '!움짤,!ㅇㅉ,!gif,!giphy 명령어로 사용이 가능합니다'
]

PAPAGO_URL = "https://papago.naver.com/"
LOCAL_DRIVER_URL = 'D:/Anaconda3/envs/envscraping/Scripts/chromedriver.exe'
URL = 'http://api.giphy.com/v1/gifs/search?'

def get_english(arg):
    '''한글을 받아서 파파고번역사이트에서 영어로 번역해서 리턴합니다'''
    rtn_str = ""
    try:
        chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
        if chrome_bin is not None:
            opts = ChromeOptions()
            opts.binary_location = chrome_bin
            opts.add_argument('headless')
            opts.add_argument("lang=ko_KR")
            opts.add_argument('--disable-gpu')
            opts.add_argument('--no-sandbox')
            browser = webdriver.Chrome(executable_path="chromedriver", chrome_options=opts)
        else:
            browser = webdriver.Chrome(LOCAL_DRIVER_URL)

        browser.implicitly_wait(3)
        browser.get(PAPAGO_URL)
        txt_source = browser.find_element_by_id('txtSource')
        txt_source.send_keys(arg)
        txt_source.send_keys(Keys.RETURN)
        time.sleep(5)
        txt_target = browser.find_element_by_id('txtTarget')
        rtn_str = txt_target.text
    finally:
        browser.quit()
        return rtn_str

def get_giphy_message(query):
    if re.search(r'[ㄱ-ㅎㅏ-ㅣ가-힣]', query, re.U):
        query = get_english(query)

    description = "{0} 로 이미지 검색했습니다".format(query)

    params = {
        'q': query,
        'api_key': 'dc6zaTOxFJmzC',
        'offset': random.randint(0, 1024),
        'limit': 1,
    }

    try:
        result = requests.get(URL, params=params).json()
    except:
        description = 'Could not connected to giphy.com. Try again later.'
    else:
        if result['pagination']['count'] < 1:
            description = 'No result found for %s Only English query is avaliable for giphy.com' % query
        else:
            el = result['data'][0]
            image_url = el['images']['original']['url']

            image = image_url[0:image_url.index('?')]
    return description, image

@on_command(['ㅇㅉ', '움짤', 'gif', 'giphy'])
def run(query):
    '''Search a image from giphy.com'''
    title = 'Giphy'
    description = ''
    image = ''

    if query:
        if len(query) < 1:
            description = '\n'.join(HELP_MSG)
        else:
            description, image = get_giphy_message(query)
    else:
        description = '\n'.join(HELP_MSG)

    return title, description, image

if '__main__' == __name__:
    print(get_english('웃긴고양이'))
