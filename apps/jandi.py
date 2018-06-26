# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Created on Thu Apr 26 19:10:15 2018

@author: skyksit
"""
import json
import http.client

import logging
LOGGER = logging.getLogger('django')

class jandi:
    in_json_data = ''
    in_token = ''
    in_team_name = ''
    in_room_name = ''
    in_writer_name = ''
    in_text = ''
    in_keyword = ''
    in_created_at_time = ''
    
    out_webhook_url = ''
    
    out_font_color = '#1DDB16'
    out_body = ''#jandi message's main title
    out_connect_info_list = []
    
    headers = {
        'Accept': 'application/vnd.tosslab.jandi-v2+json',
        'Content-Type': 'application/json'
    }
    
    def __init__(self, in_json):
        '''
        Create data by receiving request
        Args:
            in_json (json): message's request
        '''
        self.in_json_data = in_json
        self.in_token = in_json['token']
        self.in_team_name = in_json['teamName']    #jandi team list name : ex)NS홈쇼핑, groupit
        self.in_room_name = in_json['roomName']   #jandi room name
        self.in_writer_name = in_json['writerName']
        self.in_text = in_json['text']        #all text (include keyword)
        self.in_keyword = in_json['keyword']  #outgoing Webhook Start keyword
        self.in_created_at_time = in_json['createdAt']
        
    def set_webhook_url(self, out_url):
        '''
        Set address to send message
        Args:
            webhook_url (str): message's webhook url
        '''
        self.out_webhook_url = out_url
        
    def get_webhook_url(self):
        return self.out_webhook_url

    def set_font_color(self, out_color):
        '''
        sets the text color of the message
        Args:
            color (str): message's font color
        '''
        self.out_font_color = out_color
    
    def set_title(self, out_body):
        '''
        sets the title of the message
        Args:
            body title (str): message's body title
        '''
        self.out_body = out_body
        
    def get_title(self):
        return self.out_body

    def get_room_name(self):
        return self.in_room_name

    def get_writer_name(self):
        return self.in_writer_name

    def get_text(self):
        return self.in_text

    def get_headers(self):
        return self.headers
        
    def build_connect_info(self, title, description=None, image_url=None):
        '''
        jandi messengers can send several connection information
        Args:
            title (str): connect_info's title
            description (str): connect_info's description
            image_url (str): connect_info's image_url
        Returns:
            (dictionary): connect info
        '''
        connect_info = {
            'title': title
        }
        if description is not None:
            connect_info['description'] = description
        if image_url is not None:
            connect_info['imageUrl'] = image_url
        return connect_info
    
    def add_connect_info(self, title, description=None, image_url=None, connect_info_list=None):
        '''
        Add connection information
        Args:
            title (str): connect_info's title
            description (str): connect_info's description
            image_url (str): connect_info's image_url
            connect_info (list): connect_info
        Returns:
            (list): connect info
        '''
        connect_info_list.append(self.build_connect_info(title, description, image_url))
        return connect_info_list

    def build_message(self, title, color=None, connect_info_list=None):
        '''
        to build message for instant messaging
        Args:
            title (str): body's title
            color (str): font color
            connect_info (list): connect_info's
        Returns:
            (dictionary): message
        '''
        payload = {
            'body': title
        }
        if color is not None:
            payload['connectColor'] = color
        else:
            payload['connectColor'] = self.out_font_color
    
        if connect_info_list is not None:
            payload['connectInfo'] = connect_info_list
        return payload

    def send_message(self, title, color=None, webhook_url=None, connect_info_list=None):
        '''
        Send a message to jandi
        '''
        try:
            conn = http.client.HTTPSConnection('wh.jandi.com')
            
            payload = json.dumps(self.build_message(title, color, connect_info_list), ensure_ascii=False)
            
            if webhook_url is not None:
                self.set_webhook_url(webhook_url)

            LOGGER.info("self.get_webhook_url() = {0}".format(self.get_webhook_url()))
            LOGGER.info("payload = {0}".format(payload))
            LOGGER.info("self.headers = {0}".format(self.get_headers()))
            
            conn.request('POST', self.get_webhook_url(), payload.encode('utf-8'), self.get_headers())
            conn.getresponse()
        except Exception as err:
            LOGGER.error("jandi.send_message Exception = {0}".format(err))
        finally:
            conn.close()
