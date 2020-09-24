#!/usr/bin/env python3

import sys
from datetime import date
import sqlite3
import MySQLdb
import sampling
import push

db = sys.argv[1]
dbuser = sys.argv[2]
dbpass = sys.argv[3]
main_group = sys.argv[4]
next_group = sys.argv[5]

personal_numbers = ''
personal_numbers_list = []

try:
    with open('numbers.list', 'r', encoding='utf-8') as numbers:
        for line in numbers:
            personal_numbers += f"OR dst='{line[:-1]}' "
            personal_numbers_list.append(line[:-1])
except FileNotFoundError:
    print('The file "numbers.list" was not found.')

# connect to MariaDB
try:
    mariadb_conn = MySQLdb.connect(
        host='127.0.0.1',
        port=3306,
        database=db,
        user=dbuser,
        password=dbpass,
        charset='utf8'
    )
except MySQLdb.Error as e:
    print(f'Error connecting to MariaDB: {e}')
    sys.exit(1)

# get MariaDB cursor
mariadb_cursor = mariadb_conn.cursor()

# connect to sqlite
try:
    sqlite_conn = sqlite3.connect('state.db')
except sqlite3.Error as e:
    print(f'Error connecting to sqlite DB: {e}')
    sys.exit(1)

# get sqlite cursor
sqlite_cursor = sqlite_conn.cursor()

sqlite_cursor.execute('CREATE TABLE IF NOT EXISTS calls (calldate,src,clid,dst,uniqueid,dstchannel,disposition)')
sqlite_cursor.execute(f"DELETE FROM calls WHERE calldate NOT LIKE '{date.today()}%'")

last_stored_id = sqlite_cursor.execute('SELECT uniqueid FROM calls ORDER BY calldate DESC').fetchone()
if not last_stored_id:
    last_stored_id = (0,)

mariadb_cursor.execute(
    f"""SELECT DISTINCT calldate,src,clid,dst,uniqueid,dstchannel,disposition
    FROM cdr
    WHERE calldate LIKE '{date.today()}%'
        AND (dst='{main_group}' {personal_numbers} OR dst='{next_group}')
        AND uniqueid > '{last_stored_id[0]}'
    ORDER BY calldate;"""
)

# get calls list
calls = mariadb_cursor.fetchall()

sqlite_cursor.executemany('INSERT INTO calls VALUES (?,?,?,?,?,?,?)', calls)

# commit and close sqlite connection
sqlite_conn.commit()
sqlite_conn.close()

# close MariaDB connection
mariadb_conn.close()

# push statistics to Slack
support_status = sampling.get_one(calls, main_group)
common_status = sampling.get_common(calls, main_group)
if support_status:
    push.post('Unanswered call statistics :nyancat_big:',
              'Technical support:', support_status,
              'Common:', common_status
              )

one = ''
common = ''
for number in personal_numbers_list:
    get_one = sampling.get_one(calls, number)
    get_common = sampling.get_common(calls, number)
    if get_one:
        one += get_one
        common += get_common

if one:
    push.post('Unanswered call statistics :nyancat_big:',
              'Technical support:', one,
              'Common:', common
              )
