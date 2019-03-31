import os
import logging
import json
import datetime
import requests

from abc import ABC, abstractmethod

from slackclient import SlackClient
from config import Config
from utils import datatime_converter, check_date_in_period


class TrelloAPIHandler:

    def __init__(self, cfg):
        self.base_action_url = cfg.url.action
        self.base_card_list_url = cfg.url.card_list
        self.board_alpha_id = cfg.board.alpha
        self.board_bravo_id = cfg.board.bravo
        self.action_query = cfg.query.action
        self.card_list_query = cfg.query.card_list
        self.key = cfg.key
        self.token = cfg.token

    def _get_data_from_url(self, api_url, query, board_id):
        query = query.update(key=self.key, token=self.token)
        api_url = api_url.format(board_id)
        result = requests.request('GET', api_url, params=query)
        result.raise_for_status()
        json_data = json.loads(result.text)
        return json_data

    def split_cards_by_category(self, card_list):
        idea_cards = {cd['id']: cd['name'] for cd in card_list[0]['cards']}
        today_cards = {cd['id']: cd['name'] for cd in card_list[1]['cards']}
        complete_cards = {cd['id']: cd['name'] for cd in card_list[2]['cards']}
        paused_cards = {cd['id']: cd['name'] for cd in card_list[3]['cards']}
        return idea_cards, today_cards, complete_cards, paused_cards

    def _filter_actions(self, actions):
        filtered_actions = []
        for action in actions:
            action_date = act['date'][: -11]
            action_type = act['type']
            action_data = act['data']

            if check_date_in_period(action_date, period) and
                action_type in ['createCard', 'updateCard', 'Check'] or
                action_data in ['listAfter', 'fromCopy']:
                    filtered_actions.append(action)

        return filtered_actions

    def _generate_msg(self):
        pass

    def request(self, user_initial, period, board_prefix):
        if board_prefix == 'a':
            board_id = self.board_alpha_id
        elif board_prefix == 'b':
            board_id = self.board_bravo_id

        actions = self._get_data_from_API(self.base_action_url,
            self.action_query, board_id)
        card_list = self._get_data_from_API(self.base_card_list_url,
            self.card_list_query, board_id)

        idea_cards, today_cards, complete_cards, paused_cards = \
            self.split_cards_by_category(card_list)

        # gathering info for the user by matching userlabel.
        completed_tasks = []
        today_tasks = []
        idea_tasks = []
        paused_tasks = []
        added_tasks = []  # to prevent duplicate

        actions_all_needed = [act for act in actions if
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
                card_id = card_data['card']['id']  # TODO: changes in trello api?
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

    def __init__(self, cfg):
        pass

    def initialize_slack_api(self):
        self.slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        self.starterbot_id = 'DFAB'

    def parse_command(self):
        pass

    def return_result(self):
        pass


class DFABBot(SlackAPIHandler, TrelloAPIHandler):

    def __init__(self, cfg):
        self.cfg = cfg

    def run(self, bot_command, forever=True):
        while True:
            self.initialize_slack_api()
            parsed_command = self.parse_command(bot_command)
            result = self.request(parsed_command)
            self.return_result(result)
            if forever:
                continue
            else:
                break
