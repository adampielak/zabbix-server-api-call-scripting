#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os
import sys


dir_path = os.path.dirname(os.path.realpath(__file__))

required_path = dir_path + '/required'

sys.path.append(required_path)

from json_format import print_json_format
from logging_decorator import logging_decorator
from zabbix.api import ZabbixAPI


# zabbix-server地址，用户名和密码
url = 'http://172.16.161.157:9999/zabbix/api_jsonrpc.php'
user = 'Admin'
password = 'zabbix'


@logging_decorator(beforeLog='Trying to connect to {0} using username: {1} and password: {2}'.format(
    url, user, password), afterLog='Connected successfully', json_format_result=False)
def connect_to_zabbix():
    return ZabbixAPI(url=url, user=user, password=password)


# exec_path是/usr/lib/zabbix/alertscripts目录下的脚本名称
create_mediatype_params = {
    'description': 'newscript',
    'type': 1,
    'exec_path': 'newscript.sh',
    'exec_params': '{ALERT.SENDTO}\n{ALERT.SUBJECT}\n{ALERT.MESSAGE}\n',
    'status': 0
}


@logging_decorator(beforeLog='Creating new media type using params', afterLog='Created successfully', params=create_mediatype_params)
def create_mediatype(zapi):
    return zapi.do_request('mediatype.create', create_mediatype_params)


get_user_params = {
    'output': 'extend'
}


@logging_decorator(beforeLog='Getting users using params', afterLog='Gotten successfully', params=get_user_params)
def get_user(zapi):
    return zapi.do_request('user.get', get_user_params)


add_user_media_params = {
    'users': [],
    'medias': {
        "sendto": "support@company.com",
        "active": 0,
        "severity": 63,
        "period": "1-7,00:00-24:00"
    }
}


@logging_decorator(beforeLog='Adding user media using params', afterLog='Added successfully', params=add_user_media_params)
def add_user_media(zapi):
    return zapi.do_request('user.addmedia', add_user_media_params)


create_action_params = {
    'name': 'Trigger action',
    "eventsource": 0,
    'status': 0,
    "esc_period": 60,
    'def_shortdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}',
    'def_longdata':
        """Trigger: {TRIGGER.NAME}<br/>
Trigger status: {TRIGGER.STATUS}<br/>
Trigger severity: {TRIGGER.SEVERITY}<br/>
Trigger URL: {TRIGGER.URL}<br/>
<br/>
Item values:<br/>
<br/>
1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}<br/>
2. {ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}<br/>
3. {ITEM.NAME3} ({HOST.NAME3}:{ITEM.KEY3}): {ITEM.VALUE3}<br/>
<br/>
Original event ID: {EVENT.ID}
""",
    'recovery_msg': 1,
    'r_shortdata': '{TRIGGER.NAME}: {TRIGGER.STATUS}',
    'r_longdata':
        """Trigger: {TRIGGER.NAME}<br/>
Trigger status: {TRIGGER.STATUS}<br/>
Trigger severity: {TRIGGER.SEVERITY}<br/>
Trigger URL: {TRIGGER.URL}<br/>
<br/>
Item values:<br/>
<br/>
1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}<br/>
2. {ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): {ITEM.VALUE2}<br/>
3. {ITEM.NAME3} ({HOST.NAME3}:{ITEM.KEY3}): {ITEM.VALUE3}<br/>
<br/>
Original event ID: {EVENT.ID}
""",
    'filter': {
        'evaltype': 2,
        'conditions': [
            {
                'conditiontype': 4,
                "operator": 5,
                'value': 0
            }
        ]
    },
    'operations': [
        {
            "operationtype": 0,
            "esc_step_from": 1,
            "esc_step_to": 1,
            'esc_period': 0,
            'opmessage_usr': [
                {
                    'userid': ''
                }
            ],
            'opmessage': {
                "default_msg": 1,
                "mediatypeid": "14"
            }
        }
    ]
}


@logging_decorator(beforeLog='Creating action using params', afterLog='Created successfully', params=create_action_params)
def create_action(zapi):
    return zapi.do_request('action.create', create_action_params)


def validate_user(users, username='Zabbix'):
    if len(users):
        for user in users:
            if user['name'] == username:
                print('Got user named {0}'.format(username))
                return (True, user)
        print('There should be one user named {0}'.format(username))
        return (False, None)
    else:
        print('There should be at least one user before configuring Email server')
        return (False, None)


def main():
    # 连接zabbix server
    zapi = connect_to_zabbix()
    # 创建媒介类型
    mediatypeid = create_mediatype(zapi)['result']['mediatypeids'][0]
    # 获取用户
    user_result = get_user(zapi)
    result_tuple = validate_user(user_result['result'])
    if (result_tuple[0]):
        # 用户增加告警媒介
        add_user_media_params['users'].append(result_tuple[1])
        add_user_media_params['medias']['mediatypeid'] = mediatypeid
        add_user_media(zapi)
        # 添加报警动作
        create_action_params['operations'][0]['opmessage_usr'][0]['userid'] = result_tuple[1]['userid']
        create_action_params['operations'][0]['opmessage']['mediatypeid'] = mediatypeid
        create_action(zapi)


if __name__ == '__main__':
    main()
