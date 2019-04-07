import json
import re

import requests

from config import Config
from slackclient import SlackClient
from utils import check_date_in_period, datatime_converter


class TrelloAPIHandler:
    def __init__(self, cfg):
        self.base_action_url = cfg.url.action
        self.base_card_list_url = cfg.url.card_list
        self.board_alpha_id = cfg.board.alpha
        self.board_bravo_id = cfg.board.bravo
        self.key = cfg.key
        self.token = cfg.token
        self.action_query = cfg.query.action
        self.action_query = self.action_query.update(key=self.key,
            token=self.token)
        self.card_list_query = cfg.query.card_list
        self.card_list_query = self.card_list_query.update(key=self.key,
            token=self.token)

    def get_data_from_query(self, base_url, query, board_id):
        query_url = base_url.format(board_id)
        data = requests.request("GET", query_url, params=query)
        data.raise_for_status()
        json_data = json.loads(data.text)
        return json_data

    def split_cards_by_category(self, card_list):
        today_cards = {cd["id"]: cd["name"] for cd in card_list[1]["cards"]}
        done_cards = {cd["id"]: cd["name"] for cd in card_list[2]["cards"]}
        paused_cards = {cd["id"]: cd["name"] for cd in card_list[3]["cards"]}
        idea_cards = {cd["id"]: cd["name"] for cd in card_list[0]["cards"]}
        return today_cards, done_cards, paused_cards, idea_cards

    def filter_action_data(self, actions, period):
        filtered_action_data = []
        for action in actions:
            action_date = action["date"][:-11]
            action_data = action["data"]
            action_type = action["type"]

            if (
                check_date_in_period(action_date, period)
                and action_type in ["createCard", "updateCard"]
                or "Check" in action_type
                or "listAfter" in action_data
                or "fromCopy" in action_data
            ):
                filtered_action_data.append(action_data)
        return filtered_action_data

    def separate_tasks_from_action_data(actions_data, user_initial, *cards):
        assert len(cards) == 4
        today_cards, done_cards, paused_cards, idea_cards = cards

        today_tasks = []
        done_tasks = []
        paused_tasks = []
        idea_tasks = []
        added_tasks = []

        for action_data in actions_data:
            acted_user_initial = (
                action_data.get("memberCreator", {}).get("initials").lower()
            )

            card_id = action_data.get("card", {}).get("id")
            if (
                card_id is None
                or card_id in added_tasks
                or user_initial != acted_user_initial
            ):
                continue

            added_tasks.append(card_id)

            if card_id in today_cards:
                today_tasks.append(today_cards[card_id])
            elif card_id in done_cards:
                done_tasks.append(done_cards[card_id])
            elif card_id in paused_cards:
                paused_tasks.append(paused_cards[card_id])
            elif card_id in idea_cards:
                idea_tasks.append(idea_cards[card_id])
        return idea_tasks, today_tasks, done_tasks, paused_tasks

    def generate_msg(self, *tasks):
        assert len(tasks) == 4
        today_tasks, done_tasks, paused_tasks, idea_tasks = tasks

        done_msg = "*Done*\n" + "\n".join(done_tasks) + "\n\n" if done_tasks else ""
        today_msg = "*Today*\n" + "\n".join(today_tasks) + "\n\n" if today_tasks else ""
        idea_msg = "*Idea*\n" + "\n".join(idea_tasks) + "\n\n" if idea_tasks else ""
        paused_msg = (
            "*Paused*\n" + "\n".join(paused_tasks) + "\n\n" if paused_tasks else ""
        )
        final_msg = done_msg + today_msg + idea_msg + paused_msg
        return final_msg

    def request_daily_log(self, user_initial, period, board_prefix):
        user_initial = user_initial.lower()
        assert board_prefix in ["a", "b"]

        if board_prefix == "a":
            board_id = self.board_alpha_id
        elif board_prefix == "b":
            board_id = self.board_bravo_id

        actions = self.get_data_from_query(
            self.base_action_url, self.action_query, board_id
        )
        card_list = self.get_data_from_query(
            self.base_card_list_url, self.card_list_query, board_id
        )

        split_cards = self.split_cards_by_category(card_list)

        filtered_actions_data= self.filter_actions_data(actions)
        separated_tasks = self.separate_tasks_from_action_data(
            filtered_actions_data, split_cards
        )

        final_msg = self.generate_msg(separated_tasks)
        return final_msg


class SlackAPIHandler:
    def __init__(self, cfg):
        self.token = cfg.token
        self.bot_id = cfg.bot_id
        self.mention_regex = cfg.mention_regex
        self.start_cmd = cfg.start_cmd

    def initialize_slack_api(self):
        self.slack_client = SlackClient(self.token)

    def receive_events(self):
        return self.slack_client.rtm_read()

    def parse_events_to_bot_command(self, events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                channel = event["channel"]
                if user_id == self.bot_id:
                    return message, channel
        return None, None

    def parse_message_to_trello_input(self, message):
        response = None

        if message.startswith(self.start_cmd):
            trello_inputs = message.split()
            self.logger.info(message)
            if len(trello_inputs) != 4:
                response = 'More or less than 4 items input, please check the input
                format \n e.g.) @DFAB get [userinitial] [period] [a/b]
                '
            else:
                trello_inputs = trello_inputs[1:]
        return trello_inputs, response

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(self.mention_regex, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def response(self, response, channel):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )


class DFABBot(SlackAPIHandler, TrelloAPIHandler):
    def __init__(self, cfg, logger):
        self.cfg = cfg
        self.logger = logger

    def run(self):
        self.initialize_slack_api()

        while not events:  # or is not None
            events = self.receive_events()
        message, channel = self.parse_events_to_bot_command(events)
        trello_inputs, response = self.parse_message_to_trello_input(message)

        if response is not None:
            try:
                daily_log = self.request_daily_log(*trello_inputs)
            except Exception as e:
                self.logger.error("[ERROR]", exc_info=True)
                daily_log = "Error has occurred, please check the input
                    format \n e.g.) @DFAB get [userinitial] [period] [a/b]"

        self.response(daily_log)


def test_trello_handler():
    cfg = Config()
    logger = get_logger()
    bot = DFABBot(cfg=cfg, logger=logger)

    user_initial = 'wk'
    period = 1
    board_prefix = 'a'
    response = bot.request_daily_log(user_initial, period, board_prefix)
    assert response == "something"


def test_slack_handler():
    cfg = Config()
    logger = get_logger()
    bot = DFABBot(cfg=cfg, logger=logger)
    pass


if __name__ == '__main__':
    test_trello_handler()
    test_slack_handler()
