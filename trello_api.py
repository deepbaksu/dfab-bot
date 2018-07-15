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

ACTIONS_URL = "https://api.trello.com/1/boards/{}/actions"
ACTIONS_QUERY = {"key": KEY, "token": TOKEN, "limit": 300}

CARDS_LIST_URL = "https://api.trello.com/1/boards/{}/lists"
CARDS_LIST_QUERY = {"cards": "all","card_fields": "all","filter": "open",
                    "fields": "all", "key": KEY, "token": TOKEN}

TODAY_DATE = datetime.date.today()


def _get_data_from_API(api_url, query, ID):
    api_url = api_url.format(ID)
    res = requests.request('GET', api_url, params=query)
    res.raise_for_status()
    json_data = json.loads(res.text)
    return json_data


def _datetime_converter(input_time):
    converted_time = datetime.datetime.strptime(input_time, '%Y-%m-%dT%H') + datetime.timedelta(hours=9)
    converted_date = converted_time.date()
    return converted_date


def _check_date_in_period(date, period):
    date_diff = TODAY_DATE - _datetime_converter(date)
    return date_diff.days <= int(period) - 1


def get_trello(user_initial, period, board):
    if board == 'a':
        BOARD_ID = ALPHA
    elif board == 'b':
        BOARD_ID = BRAVO

    actions_data = _get_data_from_API(ACTIONS_URL, ACTIONS_QUERY, BOARD_ID)
    card_list = _get_data_from_API(CARDS_LIST_URL, CARDS_LIST_QUERY, BOARD_ID)

    # gathering card lists for each board.
    idea_cards = {cd['id']: cd['name'] for cd in card_list[0]['cards']}
    today_cards = {cd['id']: cd['name'] for cd in card_list[1]['cards']}
    complete_cards = {cd['id']: cd['name'] for cd in card_list[2]['cards']}
    paused_cards = {cd['id']: cd['name'] for cd in card_list[3]['cards']}

    # gathering info for the user by matching userlabel.
    completed_tasks = []
    today_tasks = []
    idea_tasks = []
    paused_tasks = []
    added_tasks = [] # to prevent duplicate

    actions_all_needed = [act for act in actions_data if
                          _check_date_in_period(act['date'][: -11], period) and
                          (act['type'] == 'createCard' or
                           act['type'] == 'updateCard' or
                           'listAfter' in act['data'] or
                           'Check' in act['type'])]

    # seperate tasks
    for act in actions_all_needed:
        act_user_initial = act['memberCreator']['initials'].lower()
        card_data = act['data']
        card_id = card_data['card']['id']
        if card_id in added_tasks:
            continue
        if user_initial.lower() == act_user_initial:
            added_tasks.append(card_id)
        else:
            continue
        if card_id in today_cards:
            today_tasks.append(today_cards[card_id])
        elif card_id in complete_cards:
            completed_tasks.append(complete_cards[card_id])
        elif card_id in paused_cards:
            paused_tasks.append(paused_cards[card_id])
        elif card_id in idea_cards:
            idea_tasks.append(idea_cards[card_id])

    completed_msg = '*완료*\n' + '\n'.join(completed_tasks) + '\n\n' if completed_tasks else ''
    today_msg = '*오늘 할 일*\n' + '\n'.join(today_tasks) + '\n\n' if today_tasks else ''
    idea_msg = '*아이디어*\n' + '\n'.join(idea_tasks) + '\n\n' if idea_tasks else ''
    paused_msg = '*일시정지*\n' + '\n'.join(paused_tasks) + '\n\n' if paused_tasks else ''

    results = completed_msg + today_msg + idea_msg + paused_msg
    return results


if __name__ == '__main__':
    userId = 'wk'
    period = 2
    boardId = 'a'
    result = get_trello(userId, period, boardId)
    print(result)
