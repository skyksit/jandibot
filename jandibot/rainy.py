# coding: utf-8
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup as Soup

#경기도 성남시 분당구 삼평동
URL = 'http://www.weather.go.kr/wid/queryDFSRSS.jsp?zone=4113565500'

DAY_STR = ('오늘', '내일', '모레')


def getweather():
    '''3일 이내에 비가 오는지 여부를 알려드립니다.'''
    res = requests.get(URL).text
    soup = Soup(res, features='xml')
    data = soup.body.find_all('data')
    for each in data:
        day_diff = each.day.text
        if '비' in each.wfKor.text:
            return '%s %s시부터 비가 올예정입니다.' % (DAY_STR[int(day_diff)], each.hour.text)
    return '이틀 이내에는 비가 오지 않습니다.'
