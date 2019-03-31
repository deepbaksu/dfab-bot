import os
import logging
import json
import datetime
import requests

from slackclient import SlackClient


class TrelloAPIHandler:

    def __init__(self):
        pass

    def _get_data_from_API(self, api_url, query, ID):
        api_url = api_url.format(ID)
        res = requests.request('GET', api_url, params=query)
        res.raise_for_status()
        json_data = json.loads(res.text)
        return json_data

    def _datetime_converter(self, input_time):
        converted_time = datetime.datetime.strptime(input_time, '%Y-%m-%dT%H') + datetime.timedelta(hours=9)
        converted_date = converted_time.date()
        return converted_date

    def _check_date_in_period(self, date, period):
        date_diff = TODAY_DATE - self._datetime_converter(date)
        return date_diff.days <= int(period) - 1

    def get_trello(self, user_initial, period, board):
        if board == 'a':
            BOARD_ID = ALPHA
        elif board == 'b':
            BOARD_ID = BRAVO

        actions_data = self._get_data_from_API(ACTIONS_URL, ACTIONS_QUERY, BOARD_ID)
        card_list = self._get_data_from_API(CARDS_LIST_URL, CARDS_LIST_QUERY, BOARD_ID)

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
                              self._check_date_in_period(act['date'][: -11], period) and
                              (act['type'] == 'createCard' or
                               act['type'] == 'updateCard' or
                               'listAfter' in act['data'] or
                               'Check' in act['type'] or
                               'fromCopy' in act['data'])]

        # seperate tasks
        for act in actions_all_needed:
            act_user_initial = act['memberCreator']['initials'].lower()
            card_data = act['data']
            if 'card' in card_data:
                card_id = card_data['card']['id']  #TODO: changes in trello api?
            else:
                continue
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


class SlackAPIHandler:
    def __init__(self):
        pass

    def _connect_slack_api(self):
        self.slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        self.starterbot_id = 'DFAB'

    def handle_parsed_command(self):
        pass

    def parse_bot_commands(self):
        pass


class DFABBot(SlackAPIHandler, TrelloAPIHandler):

    def __init__(self, cfg):
        self.cfg = cfg

    def handle_bot_command(bot_command):
        self._connect_slack_api()
        command = self.parse_bot_commands()
        trello_result = self.request_trello_commands(command)  # naming
        self.return_result(trello_result)  # naming, in slack
