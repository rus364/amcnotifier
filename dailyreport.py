#!/usr/bin/env python3

import sys
import sqlite3
import sampling
import push

main_group = sys.argv[1]

personal_numbers = ''
personal_numbers_list = []

try:
    with open('numbers.list', 'r', encoding='utf-8') as numbers:
        for line in numbers:
            personal_numbers += f"OR dst='{line[:-1]}' "
            personal_numbers_list.append(line[:-1])
except FileNotFoundError:
    print('The file "numbers.list" was not found.')

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
answered_statistics = sampling.get_common(calls, main_group, statistics=True)
if support_status:
    push.post_daily('Unanswered call statistics for today :meow_party:',
                    'Technical support:', support_status,
                    'Common:', common_status,
                    'Statistics:', answered_statistics
                    )

one = ''
common = ''
statistics = ''
for number in personal_numbers_list:
    get_one = sampling.get_one(calls, number)
    get_common = sampling.get_common(calls, number)
    get_statistics = sampling.get_common(calls, number, statistics=True)
    if get_one:
        one += f'\nFor number *{number}*:' + get_one + '\n'
        common += f'\nFor number *{number}*:' + get_common + '\n'
        statistics += get_statistics

if one:
    push.post_daily('Unanswered call statistics by users for today :meow_party:',
                    'Unanswered:', one,
                    'Common:', common,
                    'Statistics:', statistics
                    )
