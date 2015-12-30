# -*- coding: utf8 -*-
import json
from conf import User_Type, Address_Type

items_no = {'create_year': 0, 'user_type': 1, 'faculty': 2, 'address_type': 3, 'divide_type': 4}
items = ['create_year', 'user_type', 'faculty', 'address_type', 'divide_type']


def get_args(args):
    divide_type = args.pop()
    if divide_type == u'None':
        divide_type = ''

    no = items_no['create_year']
    if args[no] == u'所有':
        args[no] = 'all'


    no = items_no['faculty']
    if args[no] == u'所有':
        args[no] = 'all'


    no = items_no['user_type']
    if args[no] != u'所有':
        type_no = User_Type['name'].index(args[no])
        args[no] = User_Type['no'][type_no]
        if args[no] < 10:
            args[no] = '0' + str(args[no])
        else:
            args[no] = str(args[no])
    else:
        args[no] = 'all'

    no = items_no['address_type']
    if args[no] != u'所有':
        type_no = Address_Type['name'].index(args[no])
        args[no] = Address_Type['no'][type_no]
    else:
        args[no] = 'all'

    args.append(divide_type)
    return args

def get_limits(args):
    limits = ''
    for i, arg in enumerate(args):
        if arg != 'all':
            if type(arg) == str:
                arg = '"' + arg + '"'
            if limits:
                limits = '{0} and {1}'.format(limits, '{0}={1}'.format(items[i], arg))
            else:
                limits = '{0}={1}'.format(items[i], arg)
    return limits

def get_keys(divide_type, nos):
    keys = []
    if divide_type == 'user_type':
        for no in nos:
            type_no = int(no)
            if type_no in User_Type['no']:
                type_no = User_Type['no'].index(type_no)
                keys.append(User_Type['name'][type_no])
            else:
                keys.append(no)
    elif divide_type == 'address_type':
        for no in nos:
            no = Address_Type['no'].index(int(no))
            keys.append(Address_Type['name'][no])
    else:
        keys = nos
    return keys


def get_os_type(db, table, args=[u'所有', u'所有', u'所有', u'所有', u'None']):
    args = get_args(args)
    divide_type = args.pop()

    limits = get_limits(args)

    if divide_type:
        query = 'select os, {0}, count(os) from {1}'.format(divide_type, table)
    else:
        query = 'select os, count(os) from {0}'.format(table)

    if limits:
        query = '{0} where {1}'.format(query, limits)

    if divide_type:
        query = '{0} group by os, {1} order by {1}'.format(query, divide_type)
    else:
        query += ' group by os'

    print query


    res = {}
    data = {}
    names = []
    cur = db.execute(query)
    if divide_type:
        rows = [[row[0], row[1], row[2]] for row in cur.fetchall()]
        nos = []
        for os_type, no, ct in rows:
            if os_type not in names:
                names.append(os_type)
            if no not in nos:
                nos.append(no)
            data.setdefault(no, {})
            data[no][os_type] = ct
        for no in data:
            tmp = []
            for name in names:
                if name in data[no]:
                    tmp.append(data[no][name])
                else:
                    tmp.append(0)
            data[no] = tmp

        keys = get_keys(divide_type, nos)

        res['type'] = 'line'
        res['nos'] = nos
        res['keys'] = keys
    else:
        data = []
        rows = [[row[0], row[1]] for row in cur.fetchall()]
        for os_type, num in rows:
            names.append(os_type)
            data.append(num)
        res['type'] = 'pie'

    res['data'] = data
    res['names'] = names
    return json.dumps(res)


