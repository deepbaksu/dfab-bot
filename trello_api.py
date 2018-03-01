"""Trello API using python: https://developers.trello.com"""

import requests
import json
import datetime
import os

ALPHA = os.environ.get('ALPHA')
BRAVO = os.environ.get('BRAVO')
KEY = os.environ.get('KEY')
TOKEN = os.environ.get('TOKEN')

def get_trello(username, period, board):
    if board == 'a':
        BOARD_ID = ALPHA
    elif board == 'b':
        BOARD_ID = BRAVO
    cards_url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    boards_url = f'https://api.trello.com/1/boards/{BOARD_ID}'
    cards_query = {"key": KEY, "token": TOKEN}
    boards_query = {"actions": "1000", "boardStars": "none", "cards": "none", "checklists": "none",
                   "fields": "name, desc, descData, closed, idOrganization, pinned, url, shortUrl, prefs, labelNames",
                   "lists": "open", "members": "none", "memberships": "none", "membersInvited": "none",
                   "membersInvited_fields": "all", "key": KEY, "token": TOKEN}
    cards_res = requests.request("GET", cards_url, params=cards_query)
    boards_res = requests.request("GET", boards_url, params=boards_query)

    cards_data = json.loads(cards_res.text)
    boards_data = json.loads(boards_res.text)

    # getting ids of '완료', '오늘 할 일' boards
    for list in boards_data['lists']:
        if list['name'] == '완료':
            complete = list['id']
        elif list['name'] == '오늘 할 일':
            today = list['id']
        elif list['name'] == '일시정지':
            pause = list['id']
        elif list['name'] == '아이디어':
            idea = list['id']

    # gathering info for the user by matching userlabel.
    completed_tasks = []
    today_tasks = []
    idea_tasks = []
    paused_tasks = []

    for cd in cards_data:
        # consider the case labels doesn't exist.
        if cd['labels']:
            if cd['labels'][0]['name'].lower() == username.lower():
                today_date = datetime.date.today()
                if cd['idList'] == complete:
                    # Converted American to Korean time
                    end_time = datetime.datetime.strptime(cd['dateLastActivity'][: -11], '%Y-%m-%dT%H') + \
                               datetime.timedelta(hours=9)
                    time_diff = today_date - end_time.date()
                    if time_diff.days <= int(period):
                        completed_tasks.append(cd['name'])
                elif cd['idList'] == today:
                    today_tasks.append(cd['name'])
                elif cd['idList'] == pause:
                    end_time = datetime.datetime.strptime(cd['dateLastActivity'][: -11], '%Y-%m-%dT%H') + \
                               datetime.timedelta(hours=9)
                    time_diff = today_date - end_time.date()
                    if time_diff.days <= int(period):
                        paused_tasks.append(cd['name'])
                elif cd['idList'] == idea:
                    end_time = datetime.datetime.strptime(cd['dateLastActivity'][: -11], '%Y-%m-%dT%H') + \
                               datetime.timedelta(hours=9)
                    time_diff = today_date - end_time.date()
                    if time_diff.days <= int(period):
                        idea_tasks.append(cd['name'])

    completed_msg = '*완료*\n' + '\n'.join(completed_tasks) + '\n\n' if completed_tasks else ''
    today_msg = '*오늘 할 일*\n' + '\n'.join(today_tasks) + '\n\n' if today_tasks else ''
    idea_msg = '*아이디어*\n' + '\n'.join(idea_tasks) + '\n\n' if idea_tasks else ''
    paused_msg = '*일시정지*\n' + '\n'.join(paused_tasks) + '\n\n' if paused_tasks else ''

    results = completed_msg + today_msg + idea_msg + paused_msg
    return results
