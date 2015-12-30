# -*- coding: utf8 -*-
from os_type import get_args, get_limits, get_keys, items_no, items
import json
import time
import datetime

def changeStyle(oldStyle):
    newStyle = '1970-01-01 ' + oldStyle + ':00:00'
    return newStyle

def timestamp2str(timeStamp):
    dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
    styleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return styleTime


def datetime2timestamp(style, convert_to_utc=False):
    dt = datetime.datetime.strptime(style, "%Y-%m-%d %H:%M:%S")
    EPOCH = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    if isinstance(dt, datetime.datetime):
        if convert_to_utc: # 是否转化为UTC时间
            dt = dt + datetime.timedelta(hours=-8) # 中国默认时区
        timestamp = (dt - EPOCH).total_seconds()
        return long(timestamp)
    return dt


def get_continual(db, table, args=[u'所有', u'所有', u'所有', u'所有', u'None']):
    args = get_args(args)
    divide_type = args.pop()
    limits = get_limits(args)

    Duration_Style = [str(i) for i in range(12)]
    Duration = []
    for style in Duration_Style:
        style = changeStyle(style)
        Duration.append(datetime2timestamp(style))
        
    if divide_type:
        query = 'select {0}, count({0}) from {1}'.format(divide_type, table)
    else:
        query = 'select count(*) from {0}'.format(table)

    if limits:
        query = '{0} where {1}'.format(query, limits)

    res = {}
    names = []
    keys = []
    nos = []
    data = {}
    for i in range(len(Duration) - 1):
        gte = Duration[i]
        lt = Duration[i + 1]
        if limits:
            cur_query = '{0} and continual_time>{1} and continual_time<{2}'.format(query, gte, lt)
        else:
            cur_query = '{0} where continual_time>{1} and continual_time<{2}'.format(query, gte, lt)
        if divide_type:
            cur_query += ' group by {0}'.format(divide_type)
        cur = db.execute(cur_query)

        name = '{0}-{1}h'.format(Duration_Style[i], Duration_Style[i + 1])
        names.append(name)
    
        if divide_type:
            rows = [[row[0], row[1]] for row in cur.fetchall()]
            for no, ct in rows:
                if no not in nos:
                    nos.append(no)
                data.setdefault(no, {})
                data[no][name] = ct
        else:
            data.setdefault('0', [])
            num = (cur.fetchall())[0][0]
            data['0'].append(num)

    ### the last
    gte = Duration[-1]
    if limits:
        cur_query = '{0} and continual_time>={1}'.format(query, gte)
    else:
        cur_query = '{0} where continual_time>={1}'.format(query, gte)

    if divide_type:
        cur_query += ' group by {0}'.format(divide_type)

    cur = db.execute(cur_query)

    if divide_type:
        rows = [[row[0], row[1]] for row in cur.fetchall()]
        for no, ct in rows:
            if no not in nos:
                nos.append(no)
            data.setdefault(no, {})
            data[no][name] = ct
        names.append('{0}h--'.format(Duration_Style[-1]))
        for no in data:
            tmp = []
            for name in names:
                if name in data[no]:
                    tmp.append(data[no][name])
                else:
                    tmp.append(0)
            data[no] = tmp
    else:
        data.setdefault('0', [])
        num = (cur.fetchall())[0][0]
        data['0'].append(num)
    ### end the last
    

    if divide_type:
        res['nos'] = nos
        res['keys'] = get_keys(divide_type, nos)
        res['data'] = data
        res['type'] = 'line'
    else:
        res['data'] = data['0']
        res['type'] = 'bar'

    res['names'] = names
    
    return json.dumps(res)



