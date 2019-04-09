import os


trello_cfg = dict(
    board=dict(alpha=os.environ.get("ALPHA"), bravo=os.environ.get("BRAVO")),
    key=os.environ.get("KEY"),
    token=os.environ.get("TOKEN"),
    url=dict(
        action="https://api.trello.com/1/boards/{}/actions",
        card_list="https://api.trello.com/1/boards/{}/lists",
    ),
    query=dict(
        action=dict(limit=300),
        card_list=dict(cards="all", card_fields="all", filter="open", fields="all"),
    ),
)

slack_cfg = dict(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    mention_regex="^<@(|[WU].+?)>(.*)",
    start_cmd="get",
)
