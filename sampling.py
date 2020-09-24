#!/usr/bin/env python3

import re
from datetime import datetime


def get_one(calls_query, calls_group):

    last_calldate = ''
    last_src = None
    last_uniqueid = None

    answered_store = []
    dstchannel_store = ''

    call_status = ''

    for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:

        if dstchannel:
            dstchannel = re.findall(r'/(\d+)', dstchannel)[0]
        else:
            dstchannel = '???'

        if dst == calls_group:
            if uniqueid == last_uniqueid or last_uniqueid is None:
                answered_store.append(disposition)
                dstchannel_store += dstchannel + ' > '
            elif answered_store.count('ANSWERED') == 0:
                call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                    last_calldate.time(), last_src, dstchannel_store)
                answered_store = [disposition]
                dstchannel_store = dstchannel + ' > '
            else:
                answered_store = [disposition]
                dstchannel_store = dstchannel + ' > '

            last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
            last_src = src
            last_uniqueid = uniqueid

    if last_uniqueid is not None and answered_store.count('ANSWERED') == 0:
        call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
            last_calldate.time(), last_src, dstchannel_store)

    return call_status


def get_common(calls_query, first_group, statistics=False):

    last_calldate = ''
    last_src = None
    last_uniqueid = None
    last_dstchannel = ''

    answered_store = []
    dst_store = []
    dstchannel_store = ''

    call_status = ''
    hero = ''
    heroes = []
    answered_statistics = ''

    for (calldate, src, clid, dst, uniqueid, dstchannel, disposition) in calls_query:

        if dstchannel:
            dstchannel = re.findall(r'/(\d+)', dstchannel)[0]
        else:
            dstchannel = '???'

        if uniqueid == last_uniqueid or last_uniqueid is None:
            answered_store.append(disposition)
            dst_store.append(dst)
            dstchannel_store += dstchannel + ' > '
        elif answered_store.count('ANSWERED') == 0 and dst_store.count(first_group) > 0:
            call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
                last_calldate.time(), last_src, dstchannel_store)
            answered_store = [disposition]
            dst_store = [dst]
            dstchannel_store = dstchannel + ' > '
        elif answered_store.count('ANSWERED') > 0 and dst_store.count(first_group) > 0:
            call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
                last_calldate.time(), last_src,
                hero, dstchannel_store)
            answered_store = [disposition]
            dst_store = [dst]
            heroes.extend([hero])
            dstchannel_store = dstchannel + ' > '
        else:
            answered_store = [disposition]
            dst_store = [dst]
            dstchannel_store = dstchannel + ' > '

        last_calldate = datetime.strptime(str(calldate), '%Y-%m-%d %H:%M:%S')
        last_src = src
        last_uniqueid = uniqueid
        last_dstchannel = dstchannel

        if disposition == 'ANSWERED':
            hero = dstchannel

    if last_uniqueid is not None and answered_store.count('ANSWERED') == 0 and dst_store.count(first_group) > 0:
        call_status += '\n' + '{} - *{}* is missed call! {} :bangbang:'.format(
            last_calldate.time(), last_src, dstchannel_store)
    elif dst_store.count(first_group) > 0:
        call_status += '\n' + '{} - *{}* was answered by *{}*! {} :heavy_check_mark:'.format(
            last_calldate.time(), last_src,
            hero, dstchannel_store)
        heroes.extend([hero])

    answered_statistics_store = dict((i, heroes.count(i)) for i in heroes)
    for i in answered_statistics_store:
        answered_statistics += '\n' + '*{}* answered *{}* calls!'.format(i, answered_statistics_store.get(i))

    if statistics:
        return answered_statistics
    else:
        return call_status
