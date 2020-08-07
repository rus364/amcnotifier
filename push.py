import os
# import logging
from slack import WebClient
from slack.errors import SlackApiError

# logging.basicConfig(level=logging.DEBUG)

slack_token = os.environ['SLACK_API_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL_ID']

client = WebClient(token=slack_token)


def post(title, description, data, next_description, next_data):
    try:
        response = client.chat_postMessage(
            channel=slack_channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{title}*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*_{description}_*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{data}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*_{next_description}_*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{next_data}"
                    }
                }
            ]
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
