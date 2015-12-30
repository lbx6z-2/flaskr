# -*- coding: utf8 -*-
from os_type import get_args, get_limits, get_keys, items_no, items
from continual import datetime2timestamp
import json
import time
import datetime

def timestamp2str(timeStamp, convert_to_utc=False):
    if convert_to_utc:
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        styleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    else:
        timeArray = time.localtime(timeStamp)
        styleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return styleTime

def changeStyle(oldStyle):
    newStyle = '2015-11-25 ' + oldStyle + ':00'
    return newStyle

def get_online_time(db, table, args=[u'所有', u'所有', u'所有', u'所有', u'None']):
    args = get_args(args)
    divide_type = args.pop()
    limits = get_limits(args)

    Duration_Style = []
    for i in range(24):
        Duration_Style.append(str(i)+':00')
        Duration_Style.append(str(i)+':30')
    
    Duration = []
    for style in Duration_Style:
        style = changeStyle(style)
        Duration.append(datetime2timestamp(style, True))
        
 
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

    if divide_type:
        nos_query = 'select distinct {0} from {1} order by {0}'.format(divide_type, table)
        cur = db.execute(nos_query)
    
        for row in cur.fetchall():
            no = row[0]
            nos.append(no)
            data.setdefault(no, {})

    for i in range(len(Duration) - 1):
        gte = Duration[i]
        lt = Duration[i + 1]
        if limits:
            cur_query = '{0} and login_time>{1} and login_time<{2} and logout_time>{1}'.format(query, gte, lt)
        else:
            cur_query = '{0} where login_time>{1} and login_time<{2} and logout_time>{1}'.format(query, gte, lt)

        if divide_type:
            cur_query += ' group by {0}'.format(divide_type)
        cur = db.execute(cur_query)

        name = '{0}-{1}'.format(Duration_Style[i], Duration_Style[i + 1])
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
        cur_query = '{0} and login_time>={1}'.format(query, gte)
    else:
        cur_query = '{0} where login_time>={1}'.format(query, gte)

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

















