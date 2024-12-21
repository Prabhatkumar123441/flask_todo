from flask import Blueprint, request, redirect, session, render_template, jsonify, abort
from functools import wraps
import sqlite3
from servers.flask.responsebuilder import ResponseBuilder
from config  import Config
from servers.flask.log.logger import Log
from servers.flask.log.logtype import LogLevel

login_r = Blueprint("login", __name__)


def printheaders(f):
    @wraps(f)
    def printallheaders(*args, **kwargs):
        headers = dict(request.headers)
        client_ip = request.remote_addr
        print("URL: %s" % request.base_url)
        print("Request IP: %s" % client_ip)
        print("Headers:")
        print(headers)
        return f(*args, **kwargs)
    return printallheaders

@login_r.route('/login',methods = ['POST', 'GET'])
@printheaders
def login():
    username = request.form['username']
    if username[0].isdigit():
        abort(400)
        
    password = request.form['password']

    conn = sqlite3.connect(Config.database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        # return redirect(url_for('dashboard'))
        return redirect('/user')
    else:
        # return jsonify({'message': 'Invalid username or password'})
        message =   'Invalid username or password'
        return render_template('home.html',message=message)

@login_r.errorhandler(400)
@printheaders
def bad_request(error):
    # Perform the redirection here
    message =   'Interger is not allow in first place of username'
    return render_template('home.html',message=message)