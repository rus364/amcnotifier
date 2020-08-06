# amcnotifier
At first you shoud create the bot for your Slack space.

The script (mcnotifier.py) can be run as an asterisk post call script, but first you need to export environment variables to the user on whose behalf the asterisk is run:
##### export SLACK_API_TOKEN=<API_TOKEN>
##### export SLACK_CHANNEL_ID=<CHANNEL_ID>

The script takes 5 arguments:
##### asteriskcdrbd name
##### user with permission to db
##### his password
##### the first ring group
##### the group of calls that answers after the first group
