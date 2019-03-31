TrelloAPIHandler
"""accept user related info, return scraped info""" 
	- accept trello information(user, date)
	- ask trello to get user related information and return
		- succeed
		- fail - None?

SlackAPIHandler
"""init, parse init msg, return msg only"""
	- init slack handler
	- parse message from bot command
	- return message to slack(message argument needed)

DFABBot
"""use 2 above handlers"""
	- get bot command
	- init slack, parse message from bot 
	- ask trello and get info
	- return message to slack
