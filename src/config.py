import os


class config:
    alpha_board = os.environ.get('ALPHA')
    bravo_board = os.environ.get('BRAVO')
    key = os.environ.get('KEY')
    token = os.environ.get('TOKEN')
    action_query_limit = 300
    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')
