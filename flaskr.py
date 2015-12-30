# all the imports
# -*- coding: utf8 -*-
# import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from contextlib import closing
import flask.ext.login as flask_login
import json
from queries.os_type import get_os_type
from queries.os_version import get_os_version
from queries.continual import get_continual
from queries.online_time import get_online_time
from queries import conf

# configuration
DATABASE = '/home/luz/git/flaskr/sqlite/test.db'
TABLE = 'just_test'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = '123'

app = Flask(__name__)
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config.from_object(__name__)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username != USERNAME:
        return
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    print 'request_loader!!!'
    username = request.form.get('username')
    if username != USERNAME:
        return
    user = User()
    user.id = username

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = (request.form['password'] == PASSWORD)
    return user

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    args = request.args if request.method == 'GET' else request.form
    error = args.get('error', None)
    print error
    return render_template('index.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print 'POST'
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            user = User()
            user.id = USERNAME
            flask_login.login_user(user)
            return redirect(url_for('protected'))
    return redirect(url_for('index', error=error))

@app.route('/protected')
def protected():
    if not flask_login.current_user:
        return redirect(url_for('index'))
    return redirect(url_for('query'))
    # return render_template('main.html', res=res, user_id=flask_login.current_user.id)

@app.route('/query', methods=['GET', 'POST'])
def query():
    if not flask_login.current_user:
        return redirect(url_for('index'))
    cur = g.db.execute('select distinct create_year from just_test where create_year>"1978" and create_year<"2016" order by create_year')
    create_years = [row[0] for row in cur.fetchall()]
    create_years = [u'所有'] + create_years

    cur = g.db.execute('select distinct user_type from just_test')
    user_types_no = [int(row[0]) for row in cur.fetchall()]
    user_types_no.sort()
    user_types = [u'所有']
    for i, user_type in enumerate(user_types_no):
        if user_type in conf.User_Type['no']:
            no = conf.User_Type['no'].index(user_type)
            name = conf.User_Type['name'][no]
            user_types.append(name)

    query_types = conf.Query_Type['name']

    divide_types = {}
    for i in range(len(conf.Divide_Type['name'])):
        divide_types[conf.Divide_Type['name'][i]] = conf.Divide_Type['value'][i]

    cur = g.db.execute('select distinct faculty from just_test order by faculty')
    faculties = [row[0] for row in cur.fetchall()]
    faculties = [u'所有'] + faculties

    cur = g.db.execute('select distinct address_type from just_test')
    address_nos = [int(row[0]) for row in cur.fetchall()]
    address_nos.sort()
    address_types = [u'所有']
    for i, addr_no in enumerate(address_nos):
        if addr_no in conf.Address_Type['no']:
            no = conf.Address_Type['no'].index(addr_no)
            name = conf.Address_Type['name'][no]
            address_types.append(name)

    res = json.dumps({})

    if request.method == 'POST':
        print request.form
        create_year = request.form['create_year']
        if create_year != u'所有':
            create_year = int(create_year)
        user_type = request.form['user_type']
        faculty = request.form['faculty']
        print faculty
        if faculty != u'所有':
            faculty = int(faculty)
        address_type = request.form['address_type']
        query_type = request.form['query_type']
        divide_type = request.form['divide_type']
        print faculty, type(faculty)
        args = [create_year, user_type, faculty, address_type, divide_type]
        print args
        selected = {'create_year': create_year, 'user_type': user_type, 'faculty': faculty, 'address_type': address_type, 'query_type': query_type, 'divide_type': divide_type}
        if query_type == u'操作系统':
            res = get_os_type(g.db, TABLE, args)
        elif query_type == u'操作系统版本':
            res = get_os_version(g.db, TABLE, args)
        elif query_type == u'时长':
            res = get_continual(g.db, TABLE, args)
        elif query_type == u'上网时间':
            res = get_online_time(g.db, TABLE, args)
        print res
        return render_template('main.html', res=res, user_id=flask_login.current_user.id, create_years=create_years, user_types=user_types, faculties=faculties, address_types=address_types, query_types=query_types, divide_types=divide_types, selected=selected)
    else:
        return render_template('main.html', res=res, user_id=flask_login.current_user.id, create_years=create_years, user_types=user_types, faculties=faculties, address_types=address_types, query_types=query_types, divide_types=divide_types)


@app.route('/display')
def display():
    if not flask_login.current_user:
        return redirect(url_for('index'))
    cur = g.db.execute('select os, os_version from just_test limit 10')
    rows =  [[row[0], row[1]] for row in cur.fetchall()]
    src_data = {}
    for row in rows:
        src_data.setdefault(row[0], 0)
        src_data[row[0]] += 1

    data = []
    for label in src_data:
        data.append([label, src_data[label]])
    print len(data)
    return render_template('main.html', data=json.dumps(data), user_id=flask_login.current_user.id)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


if __name__=='__main__':
    app.run(debug = True)
