#!/usr/bin/env python3

import sys
import sqlite3
import sampling
import push

main_group = sys.argv[1]

# connect to sqlite
try:
    sqlite_conn = sqlite3.connect('state.db')
except sqlite3.Error as e:
    print(f'Error connecting to sqlite DB: {e}')
    sys.exit(1)

# get sqlite cursor
sqlite_cursor = sqlite_conn.cursor()

sqlite_cursor.execute(
    'SELECT calldate,src,clid,dst,uniqueid,dstchannel,disposition FROM calls ORDER BY calldate;'
)

# get calls list
calls = sqlite_cursor.fetchall()

# close sqlite connection
sqlite_conn.close()

# push statistics to Slack
support_status = sampling.get_one(calls, main_group)
common_status = sampling.get_common(calls, main_group)
if support_status != '':
    push.post('Missed call statistics :nyancat_big:',
              'Technical support:', support_status,
              'Common:', common_status
              )
