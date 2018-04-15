"""Trello API using python: https://developers.trello.com"""

import requests
import json
import datetime
import os

# secret keys 
ALPHA = os.environ.get('ALPHA')
BRAVO = os.environ.get('BRAVO')
KEY = os.environ.get('KEY')
TOKEN = os.environ.get('TOKEN')

# API urls & queries 
ACTIONS_URL = "https://api.trello.com/1/boards/{}/actions"
ACTIONS_QUERY = {"key": KEY, "token": TOKEN, "limit": 500}

TODAY_DATE = datetime.date.today()


def _get_data_from_API(api_url, query, ID):
    api_url = api_url.format(ID)
    res = requests.request('GET', api_url, params=query)
    json_data = json.loads(res.text)
    return json_data


def _datetime_converter(input_time):
    converted_time = datetime.datetime.strptime(input_time, '%Y-%m-%dT%H') + datetime.timedelta(hours=9)
    converted_date = converted_time.date()
    return converted_date


def _check_date_in_period(date, period):
    date_diff = TODAY_DATE - _datetime_converter(date)
    return date_diff.days <= int(period)


def get_trello(user_initial, period, board):
    if board == 'a':
        BOARD_ID = ALPHA
    elif board == 'b':
        BOARD_ID = BRAVO

    actions_data = _get_data_from_API(ACTIONS_URL, ACTIONS_QUERY, BOARD_ID)

    # gathering info for the user by matching userlabel.
    completed_tasks = []
    today_tasks = []
    idea_tasks = []
    paused_tasks = []

    actions_all_needed = [act for act in actions_data if
                          _check_date_in_period(act['date'][: -11], period) and
                          (act['type'] == 'createCard' or
                           'Checklist' in act['type'] or
                           'listAfter' in act['data'])]
    # seperate tasks
    for act in actions_all_needed:
        act_user_initial = act['memberCreator']['initials'].lower()
        if user_initial.lower() == act_user_initial:
            if 'list' in act['data']:
                if act['data']['list']['name'] == '오늘 할 일':
                    today_tasks.append(act['data']['card']['name'])
                elif act['data']['list']['name'] == '완료':
                    completed_tasks.append(act['data']['card']['name'])
                elif act['data']['list']['name'] == '일시정지':
                    paused_tasks.append(act['data']['card']['name'])
                elif act['data']['list']['name'] == '아이디어':
                    idea_tasks.append(act['data']['card']['name'])
            elif 'listAfter' in act['data']:
                if act['data']['listAfter']['name'] == '오늘 할 일':
                    today_tasks.append(act['data']['card']['name'])
                elif act['data']['listAfter']['name'] == '완료':
                    completed_tasks.append(act['data']['card']['name'])
                elif act['data']['listAfter']['name'] == '일시정지':
                    paused_tasks.append(act['data']['card']['name'])
                elif act['data']['listAfter']['name'] == '아이디어':
                    idea_tasks.append(act['data']['card']['name'])

    completed_msg = '*완료*\n' + '\n'.join(completed_tasks) + '\n\n' if completed_tasks else ''
    today_msg = '*오늘 할 일*\n' + '\n'.join(today_tasks) + '\n\n' if today_tasks else ''
    idea_msg = '*아이디어*\n' + '\n'.join(idea_tasks) + '\n\n' if idea_tasks else ''
    paused_msg = '*일시정지*\n' + '\n'.join(paused_tasks) + '\n\n' if paused_tasks else ''

    results = completed_msg + today_msg + idea_msg + paused_msg
    return results
