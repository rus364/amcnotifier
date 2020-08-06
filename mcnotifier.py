#!/usr/bin/env python3.6
import sys
import re
from datetime import date, datetime
import sqlite3
import MySQLdb
import push

db = sys.argv[1]
dbuser = sys.argv[2]
dbpass = sys.argv[3]
main_group = sys.argv[4]
next_group = sys.argv[5]


class GetCalls:
    def __init__(self):
        self._last_calldate = str()
        self._last_src = None
        self._last_clid = None
        self._last_dst = None
        self._last_uniqueid = None
        self._last_dstchannel = str()
        self._last_disposition = None
        self._call_status = str()
        self._answered_store = []
        self._dst_store = []
        self._dstchannel_store = str()

    def get_one(self, calls_query, calls_group):
        for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:
            if dst == calls_group:
                if uniqueid == self._last_uniqueid or self._last_uniqueid is None:
                    self._answered_store.append(disposition)
                    self._dstchannel_store += re.findall(r'/(\d+)', dstchannel)[0] + ' > '
                elif self._answered_store.count('ANSWERED') == 0:
                    self._call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                        self._last_calldate.time(), self._last_src, self._dstchannel_store)
                    self._answered_store = [disposition]
                    self._dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '
                else:
                    self._answered_store = [disposition]
                    self._dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '

                self._last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
                self._last_src = src
                self._last_uniqueid = uniqueid
                self._last_dstchannel = dstchannel

        if self._last_uniqueid is not None and self._answered_store.count('ANSWERED') == 0:
            self._call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                self._last_calldate.time(), self._last_src, self._dstchannel_store)

        return self._call_status

    def get_common(self, calls_query, first_group, second_group):
        for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:
            if uniqueid == self._last_uniqueid or self._last_uniqueid is None:
                self._answered_store.append(disposition)
                self._dst_store.append(dst)
                self._dstchannel_store += re.findall(r'/(\d+)', dstchannel)[0] + ' > '
            elif self._answered_store.count('ANSWERED') == 0 and self._dst_store.count(first_group) > 0:
                self._call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                    self._last_calldate.time(), self._last_src, self._dstchannel_store)
                self._answered_store = [disposition]
                self._dst_store = [dst]
                self._dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '
            elif self._dst_store.count(first_group) > 0:
                self._call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
                    self._last_calldate.time(), self._last_src,
                    re.findall(r'/(\d+)', self._last_dstchannel)[0], self._dstchannel_store)
                self._answered_store = [disposition]
                self._dst_store = [dst]
                self._dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '

            self._last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
            self._last_src = src
            self._last_uniqueid = uniqueid
            self._last_dstchannel = dstchannel

        if self._last_uniqueid is not None and self._answered_store.count('ANSWERED') == 0 \
                and self._dst_store.count(first_group) > 0:
            self._call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                self._last_calldate.time(), self._last_src, self._dstchannel_store)
        elif self._dst_store.count(first_group) > 0:
            self._call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
                self._last_calldate.time(), self._last_src,
                re.findall(r'/(\d+)', self._last_dstchannel)[0], self._dstchannel_store)

        return self._call_status


# connect to MariaDB
try:
    mariadb_conn = MySQLdb.connect(
        host='127.0.0.1',
        port=3306,
        database=db,
        user=dbuser,
        password=dbpass
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
        AND (dst='{main_group}' OR dst='{next_group}')
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
get_support = GetCalls()
get_common = GetCalls()
support_status = get_support.get_one(calls, main_group)
common_status = get_common.get_common(calls, main_group, next_group)
if support_status != '':
    push.post('Missed call statistics :nyancat_big:',
              'Technical support:', support_status,
              'Common:', common_status
              )
