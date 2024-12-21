from flask import Blueprint, request, redirect, session, render_template, jsonify, abort
from functools import wraps
import sqlite3
from servers.flask.responsebuilder import ResponseBuilder
from config  import Config
from servers.flask.log.logger import Log
from servers.flask.log.logtype import LogLevel


registration_r = Blueprint("registration", __name__)

available_emails = set()


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

@registration_r.route('/register')
@printheaders
def register():
    return  render_template('register.html')


@registration_r.route('/add_new_user',methods = ['POST', 'GET'])
@printheaders
def add_new_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    if username and password:
        conn = sqlite3.connect(Config.database)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if not user:
            conn = sqlite3.connect(Config.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))
            conn.commit()
            conn.close()
            available_emails.add(email)
            message= "You have successfully registered, Now you can login"
            return render_template('home.html',message = message)
        else:
            message = "This username is already in Config.database, Please choose another one."
            return render_template('register.html',message = message)
    else:
        message = "Username and Password can not be empty"
        return render_template('register.html',message = message)