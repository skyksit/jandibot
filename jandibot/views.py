# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 19:10:15 2018

@author: skyksit
"""
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import jandibot.rainy
import apps.jandi as jandi
from importlib import import_module

from jandibot.settings import (
    CMD_PREFIX, CMD_LENGTH, APPS, WEBHOOK_URLS
)

LOGGER = logging.getLogger('django')
LOGGER.info("core.views logger")

APPLIST = {}

def index(request):
    '''
    index function
    '''
    LOGGER.info("index log")
    return HttpResponse("jandibot App index.")

def extract_command(text):
    '''
    argument (String) : Jandi text /ns !weather seoul
    return command, message
    '''
    #remove keyword
    text = text[text.index(' ')+1:]

    if CMD_PREFIX != text[0]:
        return (None, None)

    tokens = text.split(' ', 1)
    if len(tokens) > 1:
        return tokens[0][CMD_LENGTH:], tokens[1]
    else:
        return (text[CMD_LENGTH:], '')

def load_apps():
    ''' loading app list '''
    for name in APPS:
        app = import_module('apps.%s' % name)
        for command in app.run.commands:
            APPLIST[command] = app

@csrf_exempt
def webhook(request):
    '''
    outgoing jandi message
    '''
    json_data = json.loads(request.body)

    load_apps()
    
    jandiapp = jandi.jandi(json_data)

#    LOGGER.info("room_name = {0}".format(jandiapp.get_room_name()))
#    LOGGER.info("writer_name = {0}".format(jandiapp.get_writer_name()))
#    LOGGER.info("text = {0}".format(jandiapp.get_text()))

    connect_info_list = []

    command, query = extract_command(jandiapp.get_text())

    LOGGER.info("command = {0}".format(command))
    LOGGER.info("query = {0}".format(query))

    if not command:
        return

    app = APPLIST.get(command)

    title, description, image = app.run(query)
    
    connect_info_list.append(jandiapp.build_connect_info(title, description, image))

#    elif command == "비와":
#        connect_info_list.append(jandiapp.build_connect_info(command, jandibot.rainy.getweather(), None))
#    else:
#        connect_info_list.append(jandiapp.build_connect_info(command, payloads, None))


    msg = "{0}님 답변드릴께요".format(jandiapp.get_writer_name())
    jandiapp.set_title(msg)

    webhook_url = WEBHOOK_URLS.get(jandiapp.get_room_name())

    LOGGER.info("jandiapp.get_title() = {0}".format(jandiapp.get_title()))
    LOGGER.info("connect_info_list = {0}".format(connect_info_list))
    LOGGER.info("webhook_url = {0}".format(webhook_url))
    
    jandiapp.send_message(jandiapp.get_title(), None, webhook_url, connect_info_list)

    return HttpResponse("created_at_time")
