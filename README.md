# dfab-bot

### 1. Slack API 
1. `pip install slackclient` 
2. [Create a Slack App](https://api.slack.com/apps/new)
3. Click on the new App - Install App and get **Bot User OAuth Access Token**.
4. `export SLACK_BOT_TOKEN='your bot user access token'`.
5. copy script from [gist](https://github.com/mattmakai/slack-starterbot/blob/master/starterbot.py).
6. Check if the script works right. 

### 2. Trello API 
1. Go to https://trello.com/1/appKey/generate and generate **API key.**
2. `export KEY='your trello API key'`
3. Go to https://trello.com/1/authorize?key=[KEY]&name=SimpleBASHScript&expiration=never&response_type=token&scope=read,write and get **token**
4. `export TOKEN='your trello API token'`.
5. Using given **key and token**, go to https://developers.trello.com/v1.0/reference#introduction and check.
6. What i've used:
	- [`[GET] /boards/{id}/actions`](https://developers.trello.com/v1.0/reference#boardsboardidactions): Getting all the actions related to the boards.

### 3. Integration
1. Command format: `@DFAB get [user initial] [period] [a/b]`.
2. `trello_api.py`: receive arguments, requests and preprocess user's trello data and return.
3. `starterbot.py`: split the command, pass arguments to get trello data, pass output to the user.
4. `forever.py`: run forever in local!

### 4. Distribution
local PC (24hr): `nohup ./forever starterbot.py > /dev/null 2>&1&`

### Reference
1. https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
2. https://gist.github.com/CrookedNumber/8856939
3. https://developers.trello.com/v1.0/reference#introduction
