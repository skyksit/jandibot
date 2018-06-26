# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 19:10:15 2018

@author: skyksit
"""
import json
import http.client

color_ok = '#1DDB16'

def build_connect_info(title, description=None, image_url=None):
    '''
    to build content for instant messaging
    '''
    connect_info = {
        'title': title
    }

    if description is not None:
        connect_info['description'] = description

    if image_url is not None:
        connect_info['imageUrl'] = image_url

    return connect_info

def build_message(msg, color, connect_info_list=None):
    '''
    to build message for instant messaging
    '''
    payload = {
        'body': msg,
        'connectColor': color,
    }

    if connect_info_list is not None:
        payload['connectInfo'] = connect_info_list

    return payload

def send_message(msg, color, webhook_url, connect_info_list=None):
    '''
    Send a message to jandi
    '''
    try:
        conn = http.client.HTTPSConnection('wh.jandi.com')
        headers = {
            'Accept': 'application/vnd.tosslab.jandi-v2+json',
            'Content-Type': 'application/json'
        }

        payload = json.dumps(build_message(msg, color, connect_info_list))
        conn.request('POST', webhook_url, payload, headers)
        conn.getresponse()
    except Exception as err:
        print(err)
    finally:
        conn.close()
