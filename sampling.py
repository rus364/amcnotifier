#!/usr/bin/env python3

import re
from datetime import datetime


def get_one(calls_query, calls_group):

    last_calldate = str()
    last_src = None
    last_uniqueid = None

    answered_store = []
    dstchannel_store = str()

    call_status = str()

    for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:
        if dst == calls_group:
            if uniqueid == last_uniqueid or last_uniqueid is None:
                answered_store.append(disposition)
                dstchannel_store += re.findall(r'/(\d+)', dstchannel)[0] + ' > '
            elif answered_store.count('ANSWERED') == 0:
                call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                    last_calldate.time(), last_src, dstchannel_store)
                answered_store = [disposition]
                dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '
            else:
                answered_store = [disposition]
                dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '

            last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
            last_src = src
            last_uniqueid = uniqueid

    if last_uniqueid is not None and answered_store.count('ANSWERED') == 0:
        call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
            last_calldate.time(), last_src, dstchannel_store)

    return call_status


def get_common(calls_query, first_group):

    last_calldate = str()
    last_src = None
    last_uniqueid = None
    last_dstchannel = str()

    answered_store = []
    dst_store = []
    dstchannel_store = str()

    call_status = str()

    for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:
        if uniqueid == last_uniqueid or last_uniqueid is None:
            answered_store.append(disposition)
            dst_store.append(dst)
            dstchannel_store += re.findall(r'/(\d+)', dstchannel)[0] + ' > '
        elif answered_store.count('ANSWERED') == 0 and dst_store.count(first_group) > 0:
            call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                last_calldate.time(), last_src, dstchannel_store)
            answered_store = [disposition]
            dst_store = [dst]
            dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '
        elif dst_store.count(first_group) > 0:
            call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
                last_calldate.time(), last_src,
                re.findall(r'/(\d+)', last_dstchannel)[0], dstchannel_store)
            answered_store = [disposition]
            dst_store = [dst]
            dstchannel_store = re.findall(r'/(\d+)', dstchannel)[0] + ' > '

        last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
        last_src = src
        last_uniqueid = uniqueid
        last_dstchannel = dstchannel

    if last_uniqueid is not None and answered_store.count('ANSWERED') == 0 and dst_store.count(first_group) > 0:
        call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
            last_calldate.time(), last_src, dstchannel_store)
    elif dst_store.count(first_group) > 0:
        call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
            last_calldate.time(), last_src,
            re.findall(r'/(\d+)', last_dstchannel)[0], dstchannel_store)

    return call_status
