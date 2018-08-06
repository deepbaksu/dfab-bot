# -*- coding: utf-8 -*-
"""Slack bot tutorial followed the code of https://www.fullstackpython.com/blog/build-first-slack-bot-python.html"""

import os
import logging
import time
import re
from slackclient import SlackClient
from trello_api import get_trello

from logger import logging_file_config


logging_file_config('./log')

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = 'DFAB'

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "get"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "입력 값은 *get* 으로 시작해야 합니다."

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        inputs = command.split()
        if len(inputs) > 4:
            response = '4개가 넘는 item이 입력되었습니다. 입력 형식을 확인해주세요. \n*입력 형식*: @DFAB get [userinitial] [기간] [a or b]'
            logging.info(inputs)
        else:
            username = inputs[-3]
            period = inputs[-2]
            board = inputs[-1].lower()
            try:
                response = get_trello(username, period, board)
                if not response:
                    response = '입력된 user에 대한 정보를 찾지 못했습니다.  입력된 userinitial을 다시 확인해주세요.'
            except Exception as e:
                logging.error("ERROR", exc_info=True)
                response = '에러가 발생했습니다. 입력 형식을 확인해주세요.  \n*입력 형식*: @DFAB get [userinitial] [기간] [a or b]'
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
                break
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
