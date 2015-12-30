# -*- coding: utf8 -*-
from os_type import get_args, get_limits, get_keys, items_no, items
from conf import User_Type, Address_Type
import json

def get_os_version(db, table, args=[u'所有', u'所有', u'所有', u'所有', u'None']):
    args = get_args(args)
    divide_type = args.pop()

    limits = get_limits(args)

    if divide_type:
        query = 'select os_version, {0}, count(os_version) from {1}'.format(divide_type, table)
    else:
        query = 'select os_version, count(os_version) from {0}'.format(table)

    if limits:
        query = '{0} where {1}'.format(query, limits)

    if divide_type:
        query = '{0} group by os_version, {1} order by {1}'.format(query, divide_type)
    else:
        query += ' group by os_version'

    print query

    res = {}
    names = []
    cur = db.execute(query)
    if divide_type:
        rows = [[row[0], row[1], row[2]] for row in cur.fetchall()]
        data = {}
        keys = []
        nos = []
        for os_version, no, ct in rows:
            if os_version not in keys:
                names.append(os_version)
            if no not in nos:
                nos.append(no)
            data.setdefault(no, {})
            data[no][os_version] = ct
        for no in data:
            tmp = []
            for name in names:
                if name in data[no]:
                    tmp.append(data[no][name])
                else:
                    tmp.append(0)
            data[no] = tmp
        res['type'] = 'line'

        
        keys = get_keys(divide_type, nos)
        res['nos'] = nos
        res['keys'] = keys
    else:
        rows = [[row[0], row[1]] for row in cur.fetchall()]
        data = []
        names = []
        for os_version, num in rows:
            names.append(os_version)
            data.append(num)
        res['type'] = 'pie'

    res['data'] = data
    res['names'] = names
    return json.dumps(res)


