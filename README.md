# amcnotifier

##### This is a simple Slack notifier that can send information about missed calls to tech support, for example.

At first you shoud [create the app](https://api.slack.com/apps) for your Slack space. Also, you should give him rights for incoming webhooks and permissions for sending message to some channel, where you want to get statistics. It's simple.

The script (mcnotifier.py) can be run as an asterisk post call script, but first you need to export environment variables to the user on whose behalf the asterisk is running.

For example, you can add below lines to his .bashrc
```
export SLACK_API_TOKEN=<API_TOKEN>
export SLACK_CHANNEL_ID=<CHANNEL_ID>
```

The script takes 5 arguments:

1. Asterisk CDR database name;
2. User with access to the database;
3. His password;
4. The first asterisk ring group;
5. The call group answering after the first group.

Also, you can add dailyreport.py to cron for the daily full reports.

Just a simple:

`00 18 * * * . ~/.bash_profile ; cd /opt/mcnotifier && ./dailyreport.py 666 >/tmp/amcnotifier.log 2>&1`
